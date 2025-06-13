"""
ATE Storage Service - Secure Multi-Tenant Codebase Storage
Enterprise-grade storage with encryption and tenant isolation
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import json

db = SQLAlchemy()

class CodebaseProject(db.Model):
    """Codebase project model with tenant isolation"""
    __tablename__ = 'codebase_projects'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = db.Column(db.String(36), nullable=False, index=True)
    
    # Project metadata
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    repository_url = db.Column(db.String(500))
    branch = db.Column(db.String(100), default='main')
    
    # Storage information
    storage_path = db.Column(db.String(500), nullable=False)
    storage_size_bytes = db.Column(db.BigInteger, default=0)
    file_count = db.Column(db.Integer, default=0)
    
    # Encryption details
    encryption_key_id = db.Column(db.String(100), nullable=False)
    encryption_algorithm = db.Column(db.String(50), default='AES-256-GCM')
    
    # Status and metadata
    status = db.Column(db.String(50), default='uploaded')  # uploaded, processing, analyzed, error
    upload_method = db.Column(db.String(50))  # git, zip, direct
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_analyzed = db.Column(db.DateTime)
    
    # Analysis metadata
    analysis_metadata = db.Column(db.JSON, default=dict)
    
    # Relationships
    files = db.relationship('CodebaseFile', backref='project', lazy=True, cascade='all, delete-orphan')
    analyses = db.relationship('AnalysisResult', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_files=False):
        result = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'repository_url': self.repository_url,
            'branch': self.branch,
            'storage_size_bytes': self.storage_size_bytes,
            'file_count': self.file_count,
            'status': self.status,
            'upload_method': self.upload_method,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_analyzed': self.last_analyzed.isoformat() if self.last_analyzed else None,
            'analysis_metadata': self.analysis_metadata
        }
        
        if include_files:
            result['files'] = [file.to_dict() for file in self.files]
            
        return result

class CodebaseFile(db.Model):
    """Individual file within a codebase project"""
    __tablename__ = 'codebase_files'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('codebase_projects.id'), nullable=False)
    
    # File metadata
    file_path = db.Column(db.String(1000), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_extension = db.Column(db.String(50))
    file_size_bytes = db.Column(db.BigInteger, nullable=False)
    
    # Content metadata
    content_type = db.Column(db.String(100))
    language = db.Column(db.String(50))
    encoding = db.Column(db.String(50), default='utf-8')
    
    # Storage details
    storage_key = db.Column(db.String(500), nullable=False)
    checksum_md5 = db.Column(db.String(32))
    checksum_sha256 = db.Column(db.String(64))
    
    # Analysis metadata
    line_count = db.Column(db.Integer)
    complexity_score = db.Column(db.Float)
    analysis_metadata = db.Column(db.JSON, default=dict)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_extension': self.file_extension,
            'file_size_bytes': self.file_size_bytes,
            'content_type': self.content_type,
            'language': self.language,
            'encoding': self.encoding,
            'line_count': self.line_count,
            'complexity_score': self.complexity_score,
            'analysis_metadata': self.analysis_metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class AnalysisResult(db.Model):
    """Analysis results for codebase projects"""
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('codebase_projects.id'), nullable=False)
    
    # Analysis metadata
    analysis_type = db.Column(db.String(100), nullable=False)  # parsing, quality, architecture, etc.
    analysis_version = db.Column(db.String(50), default='1.0')
    status = db.Column(db.String(50), default='pending')  # pending, running, completed, failed
    
    # Results
    results = db.Column(db.JSON, default=dict)
    metrics = db.Column(db.JSON, default=dict)
    recommendations = db.Column(db.JSON, default=list)
    
    # Performance metadata
    processing_time_seconds = db.Column(db.Float)
    memory_usage_mb = db.Column(db.Float)
    
    # Error handling
    error_message = db.Column(db.Text)
    error_details = db.Column(db.JSON)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'analysis_type': self.analysis_type,
            'analysis_version': self.analysis_version,
            'status': self.status,
            'results': self.results,
            'metrics': self.metrics,
            'recommendations': self.recommendations,
            'processing_time_seconds': self.processing_time_seconds,
            'memory_usage_mb': self.memory_usage_mb,
            'error_message': self.error_message,
            'error_details': self.error_details,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class StorageQuota(db.Model):
    """Storage quota tracking per tenant"""
    __tablename__ = 'storage_quotas'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    
    # Quota limits
    max_storage_bytes = db.Column(db.BigInteger, default=1073741824)  # 1GB default
    max_projects = db.Column(db.Integer, default=10)
    max_files_per_project = db.Column(db.Integer, default=10000)
    
    # Current usage
    current_storage_bytes = db.Column(db.BigInteger, default=0)
    current_projects = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_usage_percentage(self):
        """Calculate storage usage percentage"""
        if self.max_storage_bytes == 0:
            return 0
        return (self.current_storage_bytes / self.max_storage_bytes) * 100
    
    def has_storage_available(self, required_bytes):
        """Check if tenant has enough storage available"""
        return (self.current_storage_bytes + required_bytes) <= self.max_storage_bytes
    
    def has_project_slots_available(self):
        """Check if tenant can create more projects"""
        return self.current_projects < self.max_projects
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'max_storage_bytes': self.max_storage_bytes,
            'max_projects': self.max_projects,
            'max_files_per_project': self.max_files_per_project,
            'current_storage_bytes': self.current_storage_bytes,
            'current_projects': self.current_projects,
            'usage_percentage': self.get_usage_percentage(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class EncryptionKey(db.Model):
    """Encryption key management for tenant data"""
    __tablename__ = 'encryption_keys'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = db.Column(db.String(36), nullable=False, index=True)
    
    # Key metadata
    key_id = db.Column(db.String(100), unique=True, nullable=False)
    algorithm = db.Column(db.String(50), default='AES-256-GCM')
    key_purpose = db.Column(db.String(50), default='data_encryption')
    
    # Key data (encrypted with master key)
    encrypted_key_data = db.Column(db.Text, nullable=False)
    key_derivation_salt = db.Column(db.String(100))
    
    # Status and rotation
    status = db.Column(db.String(50), default='active')  # active, rotating, retired
    rotation_schedule_days = db.Column(db.Integer, default=90)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_rotated = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    def to_dict(self, include_sensitive=False):
        result = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'key_id': self.key_id,
            'algorithm': self.algorithm,
            'key_purpose': self.key_purpose,
            'status': self.status,
            'rotation_schedule_days': self.rotation_schedule_days,
            'created_at': self.created_at.isoformat(),
            'last_rotated': self.last_rotated.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
        
        if include_sensitive:
            result['encrypted_key_data'] = self.encrypted_key_data
            result['key_derivation_salt'] = self.key_derivation_salt
            
        return result

