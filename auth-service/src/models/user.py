"""
ATE Authentication Service - Enhanced User and Tenant Models
Multi-tenant authentication with JWT support
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
import uuid

db = SQLAlchemy()

class Tenant(db.Model):
    """Multi-tenant organization model"""
    __tablename__ = 'tenants'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    organization = db.Column(db.String(200), nullable=False)
    plan = db.Column(db.String(50), default='basic')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Settings stored as JSON
    settings = db.Column(db.JSON, default=dict)
    
    # Usage limits
    max_analyses_per_month = db.Column(db.Integer, default=10)
    max_codebase_size_mb = db.Column(db.Integer, default=100)
    max_concurrent_analyses = db.Column(db.Integer, default=2)
    
    # Relationships
    users = db.relationship('User', backref='tenant_ref', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'organization': self.organization,
            'plan': self.plan,
            'active': self.active,
            'created_at': self.created_at.isoformat(),
            'settings': self.settings,
            'usage_limits': {
                'max_analyses_per_month': self.max_analyses_per_month,
                'max_codebase_size_mb': self.max_codebase_size_mb,
                'max_concurrent_analyses': self.max_concurrent_analyses
            }
        }

class User(db.Model):
    """Enhanced user model with authentication and tenant support"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # User profile
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    
    # Tenant relationship
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False)
    
    # Role and permissions
    role = db.Column(db.String(50), default='user')  # user, admin, super_admin
    permissions = db.Column(db.JSON, default=list)
    
    # Account status
    active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hash and set password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def has_permission(self, permission):
        """Check if user has specific permission"""
        return permission in self.permissions or self.role == 'super_admin'
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        user_dict = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'tenant_id': self.tenant_id,
            'role': self.role,
            'permissions': self.permissions,
            'active': self.active,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            user_dict['password_hash'] = self.password_hash
            
        return user_dict

class RefreshToken(db.Model):
    """Refresh token model for JWT token management"""
    __tablename__ = 'refresh_tokens'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    token_hash = db.Column(db.String(128), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    revoked = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', backref='refresh_tokens')
    
    def is_valid(self):
        """Check if refresh token is still valid"""
        return not self.revoked and self.expires_at > datetime.utcnow()
    
    def revoke(self):
        """Revoke the refresh token"""
        self.revoked = True
        db.session.commit()

class AuditLog(db.Model):
    """Audit log for tracking authentication events"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'))
    
    # Event details
    event_type = db.Column(db.String(50), nullable=False)  # login, logout, register, etc.
    event_data = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='audit_logs')
    tenant = db.relationship('Tenant', backref='audit_logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'event_type': self.event_type,
            'event_data': self.event_data,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat()
        }

