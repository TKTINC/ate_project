"""
ATE Storage Service - Project Management Routes
Codebase project CRUD operations with tenant isolation
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

from src.models.user import db, CodebaseProject, CodebaseFile, AnalysisResult, StorageQuota
from src.utils.auth import require_auth, get_current_user

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/', methods=['GET'])
@require_auth
def get_projects():
    """Get all projects for current tenant"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    # Get filter parameters
    status = request.args.get('status')
    search = request.args.get('search')
    
    # Build query
    query = CodebaseProject.query.filter_by(tenant_id=tenant_id)
    
    if status:
        query = query.filter_by(status=status)
    
    if search:
        query = query.filter(
            CodebaseProject.name.contains(search) |
            CodebaseProject.description.contains(search)
        )
    
    # Order by most recent first
    query = query.order_by(CodebaseProject.created_at.desc())
    
    # Paginate
    projects = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return jsonify({
        'projects': [project.to_dict() for project in projects.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': projects.total,
            'pages': projects.pages,
            'has_next': projects.has_next,
            'has_prev': projects.has_prev
        }
    })

@projects_bp.route('/<project_id>', methods=['GET'])
@require_auth
def get_project(project_id):
    """Get specific project with optional file listing"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    project = CodebaseProject.query.filter_by(
        id=project_id, tenant_id=tenant_id
    ).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    include_files = request.args.get('include_files', 'false').lower() == 'true'
    
    return jsonify({
        'project': project.to_dict(include_files=include_files)
    })

@projects_bp.route('/<project_id>/files', methods=['GET'])
@require_auth
def get_project_files(project_id):
    """Get files for specific project"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Verify project access
    project = CodebaseProject.query.filter_by(
        id=project_id, tenant_id=tenant_id
    ).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 200)
    
    # Get filter parameters
    language = request.args.get('language')
    file_type = request.args.get('file_type')
    search = request.args.get('search')
    
    # Build query
    query = CodebaseFile.query.filter_by(project_id=project_id)
    
    if language:
        query = query.filter_by(language=language)
    
    if file_type:
        query = query.filter_by(content_type=file_type)
    
    if search:
        query = query.filter(
            CodebaseFile.file_name.contains(search) |
            CodebaseFile.file_path.contains(search)
        )
    
    # Order by file path
    query = query.order_by(CodebaseFile.file_path)
    
    # Paginate
    files = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # Get file statistics
    stats = {
        'total_files': CodebaseFile.query.filter_by(project_id=project_id).count(),
        'languages': db.session.query(
            CodebaseFile.language,
            db.func.count(CodebaseFile.id).label('count')
        ).filter_by(project_id=project_id).group_by(CodebaseFile.language).all(),
        'file_types': db.session.query(
            CodebaseFile.content_type,
            db.func.count(CodebaseFile.id).label('count')
        ).filter_by(project_id=project_id).group_by(CodebaseFile.content_type).all()
    }
    
    return jsonify({
        'files': [file.to_dict() for file in files.items],
        'statistics': {
            'total_files': stats['total_files'],
            'languages': [{'language': lang, 'count': count} for lang, count in stats['languages']],
            'file_types': [{'type': ftype, 'count': count} for ftype, count in stats['file_types']]
        },
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': files.total,
            'pages': files.pages,
            'has_next': files.has_next,
            'has_prev': files.has_prev
        }
    })

@projects_bp.route('/<project_id>', methods=['PUT'])
@require_auth
def update_project(project_id):
    """Update project metadata"""
    try:
        current_user = get_current_user()
        tenant_id = current_user['tenant_id']
        
        project = CodebaseProject.query.filter_by(
            id=project_id, tenant_id=tenant_id
        ).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            project.name = data['name']
        if 'description' in data:
            project.description = data['description']
        if 'repository_url' in data:
            project.repository_url = data['repository_url']
        if 'branch' in data:
            project.branch = data['branch']
        if 'analysis_metadata' in data:
            project.analysis_metadata.update(data['analysis_metadata'])
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Project updated successfully',
            'project': project.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Project update failed: {str(e)}'}), 500

@projects_bp.route('/<project_id>', methods=['DELETE'])
@require_auth
def delete_project(project_id):
    """Delete project and all associated files"""
    try:
        current_user = get_current_user()
        tenant_id = current_user['tenant_id']
        
        project = CodebaseProject.query.filter_by(
            id=project_id, tenant_id=tenant_id
        ).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get storage size for quota update
        storage_size = project.storage_size_bytes
        
        # Delete from storage backend (files will be deleted via cascade)
        # TODO: Implement storage backend cleanup
        
        # Update quota
        quota = StorageQuota.query.filter_by(tenant_id=tenant_id).first()
        if quota:
            quota.current_storage_bytes -= storage_size
            quota.current_projects -= 1
        
        # Delete project (cascade will handle files and analyses)
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'message': 'Project deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Project deletion failed: {str(e)}'}), 500

@projects_bp.route('/<project_id>/analyses', methods=['GET'])
@require_auth
def get_project_analyses(project_id):
    """Get analysis results for project"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Verify project access
    project = CodebaseProject.query.filter_by(
        id=project_id, tenant_id=tenant_id
    ).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Get filter parameters
    analysis_type = request.args.get('analysis_type')
    status = request.args.get('status')
    
    # Build query
    query = AnalysisResult.query.filter_by(project_id=project_id)
    
    if analysis_type:
        query = query.filter_by(analysis_type=analysis_type)
    
    if status:
        query = query.filter_by(status=status)
    
    # Order by most recent first
    query = query.order_by(AnalysisResult.started_at.desc())
    
    analyses = query.all()
    
    return jsonify({
        'analyses': [analysis.to_dict() for analysis in analyses],
        'total': len(analyses)
    })

@projects_bp.route('/<project_id>/statistics', methods=['GET'])
@require_auth
def get_project_statistics(project_id):
    """Get comprehensive project statistics"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Verify project access
    project = CodebaseProject.query.filter_by(
        id=project_id, tenant_id=tenant_id
    ).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Calculate statistics
    total_files = CodebaseFile.query.filter_by(project_id=project_id).count()
    total_lines = db.session.query(
        db.func.sum(CodebaseFile.line_count)
    ).filter_by(project_id=project_id).scalar() or 0
    
    # Language distribution
    language_stats = db.session.query(
        CodebaseFile.language,
        db.func.count(CodebaseFile.id).label('file_count'),
        db.func.sum(CodebaseFile.file_size_bytes).label('total_size'),
        db.func.sum(CodebaseFile.line_count).label('total_lines')
    ).filter_by(project_id=project_id).group_by(CodebaseFile.language).all()
    
    # File type distribution
    type_stats = db.session.query(
        CodebaseFile.content_type,
        db.func.count(CodebaseFile.id).label('file_count'),
        db.func.sum(CodebaseFile.file_size_bytes).label('total_size')
    ).filter_by(project_id=project_id).group_by(CodebaseFile.content_type).all()
    
    # Analysis status
    analysis_stats = db.session.query(
        AnalysisResult.analysis_type,
        AnalysisResult.status,
        db.func.count(AnalysisResult.id).label('count')
    ).filter_by(project_id=project_id).group_by(
        AnalysisResult.analysis_type, AnalysisResult.status
    ).all()
    
    return jsonify({
        'project_id': project_id,
        'overview': {
            'total_files': total_files,
            'total_lines': total_lines,
            'total_size_bytes': project.storage_size_bytes,
            'created_at': project.created_at.isoformat(),
            'last_analyzed': project.last_analyzed.isoformat() if project.last_analyzed else None
        },
        'languages': [
            {
                'language': lang,
                'file_count': file_count,
                'total_size_bytes': total_size or 0,
                'total_lines': total_lines or 0,
                'percentage': (file_count / total_files * 100) if total_files > 0 else 0
            }
            for lang, file_count, total_size, total_lines in language_stats
        ],
        'file_types': [
            {
                'type': ftype,
                'file_count': file_count,
                'total_size_bytes': total_size or 0,
                'percentage': (file_count / total_files * 100) if total_files > 0 else 0
            }
            for ftype, file_count, total_size in type_stats
        ],
        'analyses': [
            {
                'analysis_type': analysis_type,
                'status': status,
                'count': count
            }
            for analysis_type, status, count in analysis_stats
        ]
    })

