"""
ATE Storage Service - Storage Management Routes
Secure file upload, download, and management with encryption
"""

import os
import hashlib
import tempfile
import zipfile
import shutil
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
import uuid

from src.models.user import db, CodebaseProject, CodebaseFile, StorageQuota, EncryptionKey
from src.utils.encryption import EncryptionManager
from src.utils.storage_backend import StorageBackend
from src.utils.auth import require_auth, get_current_user

storage_bp = Blueprint('storage', __name__)

@storage_bp.route('/upload', methods=['POST'])
@require_auth
def upload_codebase():
    """Upload codebase files (zip or individual files)"""
    try:
        current_user = get_current_user()
        tenant_id = current_user['tenant_id']
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get project metadata
        project_name = request.form.get('project_name')
        project_description = request.form.get('project_description', '')
        repository_url = request.form.get('repository_url', '')
        branch = request.form.get('branch', 'main')
        
        if not project_name:
            return jsonify({'error': 'Project name is required'}), 400
        
        # Check storage quota
        quota = StorageQuota.query.filter_by(tenant_id=tenant_id).first()
        if not quota:
            # Create default quota for new tenant
            quota = StorageQuota(tenant_id=tenant_id)
            db.session.add(quota)
            db.session.flush()
        
        if not quota.has_project_slots_available():
            return jsonify({
                'error': 'Project limit exceeded',
                'current_projects': quota.current_projects,
                'max_projects': quota.max_projects
            }), 429
        
        # Create temporary file to check size
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        file.save(temp_file.name)
        file_size = os.path.getsize(temp_file.name)
        
        if not quota.has_storage_available(file_size):
            os.unlink(temp_file.name)
            return jsonify({
                'error': 'Storage quota exceeded',
                'required_bytes': file_size,
                'available_bytes': quota.max_storage_bytes - quota.current_storage_bytes
            }), 429
        
        # Create project
        project = CodebaseProject(
            tenant_id=tenant_id,
            name=project_name,
            description=project_description,
            repository_url=repository_url,
            branch=branch,
            storage_path=f"tenants/{tenant_id}/projects/{uuid.uuid4()}",
            upload_method='zip' if file.filename.endswith('.zip') else 'direct',
            encryption_key_id=f"tenant-{tenant_id}-{uuid.uuid4()}"
        )
        
        db.session.add(project)
        db.session.flush()  # Get project ID
        
        # Initialize encryption for this project
        encryption_manager = EncryptionManager(current_app.config['MASTER_KEY'])
        project_key = encryption_manager.create_project_key(tenant_id, project.id)
        
        # Store encryption key
        enc_key = EncryptionKey(
            tenant_id=tenant_id,
            key_id=project.encryption_key_id,
            encrypted_key_data=project_key['encrypted_key'],
            key_derivation_salt=project_key['salt']
        )
        db.session.add(enc_key)
        
        # Initialize storage backend
        storage_backend = StorageBackend(current_app.config)
        
        # Process uploaded file
        if file.filename.endswith('.zip'):
            # Handle zip file
            total_size, file_count = _process_zip_file(
                temp_file.name, project, encryption_manager, storage_backend
            )
        else:
            # Handle single file
            total_size, file_count = _process_single_file(
                temp_file.name, file.filename, project, encryption_manager, storage_backend
            )
        
        # Update project metadata
        project.storage_size_bytes = total_size
        project.file_count = file_count
        project.status = 'uploaded'
        
        # Update quota
        quota.current_storage_bytes += total_size
        quota.current_projects += 1
        
        db.session.commit()
        
        # Clean up temp file
        os.unlink(temp_file.name)
        
        return jsonify({
            'message': 'Codebase uploaded successfully',
            'project': project.to_dict(),
            'storage_usage': quota.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        if 'temp_file' in locals():
            try:
                os.unlink(temp_file.name)
            except:
                pass
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

def _process_zip_file(zip_path, project, encryption_manager, storage_backend):
    """Process uploaded zip file and extract contents"""
    total_size = 0
    file_count = 0
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            if file_info.is_dir():
                continue
            
            # Skip hidden files and common non-code files
            if _should_skip_file(file_info.filename):
                continue
            
            # Extract file content
            file_content = zip_ref.read(file_info.filename)
            
            # Create file record and upload
            file_record = _create_file_record(
                project, file_info.filename, file_content, 
                encryption_manager, storage_backend
            )
            
            total_size += file_record.file_size_bytes
            file_count += 1
    
    return total_size, file_count

def _process_single_file(file_path, filename, project, encryption_manager, storage_backend):
    """Process single uploaded file"""
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    file_record = _create_file_record(
        project, filename, file_content, 
        encryption_manager, storage_backend
    )
    
    return file_record.file_size_bytes, 1

def _create_file_record(project, file_path, content, encryption_manager, storage_backend):
    """Create file record and upload encrypted content"""
    # Generate checksums
    md5_hash = hashlib.md5(content).hexdigest()
    sha256_hash = hashlib.sha256(content).hexdigest()
    
    # Encrypt content
    encrypted_content = encryption_manager.encrypt_data(content, project.encryption_key_id)
    
    # Generate storage key
    storage_key = f"{project.storage_path}/{file_path}"
    
    # Upload to storage backend
    storage_backend.upload_file(storage_key, encrypted_content)
    
    # Detect file properties
    file_extension = os.path.splitext(file_path)[1].lower()
    language = _detect_language(file_extension)
    content_type = _get_content_type(file_extension)
    
    # Create file record
    file_record = CodebaseFile(
        project_id=project.id,
        file_path=file_path,
        file_name=os.path.basename(file_path),
        file_extension=file_extension,
        file_size_bytes=len(content),
        content_type=content_type,
        language=language,
        storage_key=storage_key,
        checksum_md5=md5_hash,
        checksum_sha256=sha256_hash,
        line_count=len(content.decode('utf-8', errors='ignore').splitlines()) if content_type == 'text' else None
    )
    
    db.session.add(file_record)
    return file_record

def _should_skip_file(filename):
    """Check if file should be skipped during upload"""
    skip_patterns = [
        '.git/', '__pycache__/', 'node_modules/', '.vscode/', '.idea/',
        '.DS_Store', 'Thumbs.db', '.env', '.log'
    ]
    
    for pattern in skip_patterns:
        if pattern in filename:
            return True
    
    return False

def _detect_language(file_extension):
    """Detect programming language from file extension"""
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.cs': 'csharp',
        '.go': 'go',
        '.php': 'php',
        '.rb': 'ruby',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.sql': 'sql',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.txt': 'text'
    }
    
    return language_map.get(file_extension, 'unknown')

def _get_content_type(file_extension):
    """Get content type from file extension"""
    text_extensions = [
        '.py', '.js', '.ts', '.java', '.cs', '.go', '.php', '.rb', 
        '.cpp', '.c', '.h', '.hpp', '.sql', '.html', '.css', '.json', 
        '.xml', '.yaml', '.yml', '.md', '.txt', '.sh', '.bat'
    ]
    
    return 'text' if file_extension in text_extensions else 'binary'

@storage_bp.route('/download/<project_id>/<file_id>', methods=['GET'])
@require_auth
def download_file(project_id, file_id):
    """Download specific file from project"""
    try:
        current_user = get_current_user()
        tenant_id = current_user['tenant_id']
        
        # Get project and verify access
        project = CodebaseProject.query.filter_by(
            id=project_id, tenant_id=tenant_id
        ).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get file record
        file_record = CodebaseFile.query.filter_by(
            id=file_id, project_id=project_id
        ).first()
        
        if not file_record:
            return jsonify({'error': 'File not found'}), 404
        
        # Initialize storage and encryption
        storage_backend = StorageBackend(current_app.config)
        encryption_manager = EncryptionManager(current_app.config['MASTER_KEY'])
        
        # Download and decrypt file
        encrypted_content = storage_backend.download_file(file_record.storage_key)
        decrypted_content = encryption_manager.decrypt_data(
            encrypted_content, project.encryption_key_id
        )
        
        # Create temporary file for download
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(decrypted_content)
        temp_file.close()
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=file_record.file_name,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@storage_bp.route('/quota/<tenant_id>', methods=['GET'])
@require_auth
def get_storage_quota(tenant_id):
    """Get storage quota information for tenant"""
    current_user = get_current_user()
    
    # Users can only access their own tenant quota unless super admin
    if current_user['tenant_id'] != tenant_id and current_user['role'] != 'super_admin':
        return jsonify({'error': 'Access denied'}), 403
    
    quota = StorageQuota.query.filter_by(tenant_id=tenant_id).first()
    if not quota:
        # Create default quota
        quota = StorageQuota(tenant_id=tenant_id)
        db.session.add(quota)
        db.session.commit()
    
    return jsonify({
        'quota': quota.to_dict()
    })

@storage_bp.route('/quota/<tenant_id>', methods=['PUT'])
@require_auth
def update_storage_quota(tenant_id):
    """Update storage quota (super admin only)"""
    current_user = get_current_user()
    
    if current_user['role'] != 'super_admin':
        return jsonify({'error': 'Super admin access required'}), 403
    
    try:
        data = request.get_json()
        
        quota = StorageQuota.query.filter_by(tenant_id=tenant_id).first()
        if not quota:
            quota = StorageQuota(tenant_id=tenant_id)
            db.session.add(quota)
        
        # Update quota limits
        if 'max_storage_bytes' in data:
            quota.max_storage_bytes = data['max_storage_bytes']
        if 'max_projects' in data:
            quota.max_projects = data['max_projects']
        if 'max_files_per_project' in data:
            quota.max_files_per_project = data['max_files_per_project']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Quota updated successfully',
            'quota': quota.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Quota update failed: {str(e)}'}), 500

