"""
ATE Authentication Service - User Management Routes
User CRUD operations with role-based access control
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.models.user import db, User, Tenant, AuditLog

user_bp = Blueprint('user', __name__)

def require_permission(permission):
    """Decorator to check user permissions"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if not user.has_permission(permission) and user.role not in ['admin', 'super_admin']:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@user_bp.route('/', methods=['GET'])
@jwt_required()
@require_permission('users:view')
def get_users():
    """Get users (filtered by tenant unless super admin)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Super admin can see all users, others only see users from their tenant
    if current_user.role == 'super_admin':
        users = User.query.all()
    else:
        users = User.query.filter_by(tenant_id=current_user.tenant_id).all()
    
    return jsonify({
        'users': [user.to_dict() for user in users],
        'total': len(users)
    })

@user_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get specific user information"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Users can view their own profile or users from same tenant (if admin)
    # Super admin can view any user
    if (user_id != current_user_id and 
        current_user.tenant_id != user.tenant_id and 
        current_user.role != 'super_admin'):
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'user': user.to_dict()
    })

@user_bp.route('/', methods=['POST'])
@jwt_required()
@require_permission('users:create')
def create_user():
    """Create new user in the same tenant"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Determine tenant_id
        if current_user.role == 'super_admin' and data.get('tenant_id'):
            tenant_id = data['tenant_id']
            # Verify tenant exists
            tenant = Tenant.query.get(tenant_id)
            if not tenant:
                return jsonify({'error': 'Tenant not found'}), 404
        else:
            tenant_id = current_user.tenant_id
        
        # Create new user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            tenant_id=tenant_id,
            role=data.get('role', 'user'),
            permissions=data.get('permissions', []),
            active=data.get('active', True),
            email_verified=data.get('email_verified', False)
        )
        user.set_password(data['password'])
        
        # Validate role assignment
        if (current_user.role != 'super_admin' and 
            user.role in ['super_admin', 'admin'] and 
            current_user.role != 'admin'):
            return jsonify({'error': 'Insufficient permissions to assign this role'}), 403
        
        db.session.add(user)
        db.session.commit()
        
        # Create audit log
        audit_log = AuditLog(
            user_id=current_user.id,
            tenant_id=tenant_id,
            event_type='user_created',
            event_data={
                'created_user_id': user.id,
                'created_user_email': user.email,
                'role': user.role
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'User creation failed: {str(e)}'}), 500

@user_bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user information"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Permission check
        is_self_update = user_id == current_user_id
        is_same_tenant = current_user.tenant_id == user.tenant_id
        is_admin = current_user.role in ['admin', 'super_admin']
        
        if not (is_self_update or (is_same_tenant and is_admin) or current_user.role == 'super_admin'):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Fields that users can update for themselves
        self_updatable_fields = ['first_name', 'last_name']
        
        # Fields that admins can update
        admin_updatable_fields = ['first_name', 'last_name', 'role', 'permissions', 'active']
        
        # Fields that only super admin can update
        super_admin_fields = ['tenant_id', 'email']
        
        # Update allowed fields based on permissions
        for field in data:
            if field in self_updatable_fields:
                setattr(user, field, data[field])
            elif field in admin_updatable_fields and is_admin:
                # Additional validation for role changes
                if field == 'role' and not is_self_update:
                    if (current_user.role != 'super_admin' and 
                        data[field] in ['super_admin', 'admin']):
                        return jsonify({'error': 'Insufficient permissions to assign this role'}), 403
                setattr(user, field, data[field])
            elif field in super_admin_fields and current_user.role == 'super_admin':
                if field == 'tenant_id':
                    # Verify new tenant exists
                    tenant = Tenant.query.get(data[field])
                    if not tenant:
                        return jsonify({'error': 'Tenant not found'}), 404
                setattr(user, field, data[field])
            elif field == 'password' and (is_self_update or is_admin):
                user.set_password(data[field])
        
        db.session.commit()
        
        # Create audit log
        audit_log = AuditLog(
            user_id=current_user.id,
            tenant_id=user.tenant_id,
            event_type='user_updated',
            event_data={
                'updated_user_id': user.id,
                'updated_user_email': user.email,
                'updated_fields': list(data.keys()),
                'is_self_update': is_self_update
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'User update failed: {str(e)}'}), 500

@user_bp.route('/<user_id>', methods=['DELETE'])
@jwt_required()
@require_permission('users:delete')
def delete_user(user_id):
    """Delete user (soft delete by deactivating)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent self-deletion
        if user_id == current_user_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Permission check
        is_same_tenant = current_user.tenant_id == user.tenant_id
        is_admin = current_user.role in ['admin', 'super_admin']
        
        if not ((is_same_tenant and is_admin) or current_user.role == 'super_admin'):
            return jsonify({'error': 'Access denied'}), 403
        
        # Soft delete by deactivating
        user.active = False
        db.session.commit()
        
        # Create audit log
        audit_log = AuditLog(
            user_id=current_user.id,
            tenant_id=user.tenant_id,
            event_type='user_deleted',
            event_data={
                'deleted_user_id': user.id,
                'deleted_user_email': user.email
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'User deactivated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'User deletion failed: {str(e)}'}), 500

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user's profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    tenant = Tenant.query.get(user.tenant_id)
    
    return jsonify({
        'user': user.to_dict(),
        'tenant': tenant.to_dict() if tenant else None
    })

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user's profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Fields that users can update in their own profile
        updatable_fields = ['first_name', 'last_name']
        
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # Handle password change separately
        if 'password' in data:
            if not data.get('current_password'):
                return jsonify({'error': 'Current password required for password change'}), 400
            
            if not user.check_password(data['current_password']):
                return jsonify({'error': 'Current password is incorrect'}), 401
            
            user.set_password(data['password'])
        
        db.session.commit()
        
        # Create audit log
        audit_log = AuditLog(
            user_id=user.id,
            tenant_id=user.tenant_id,
            event_type='profile_updated',
            event_data={'updated_fields': list(data.keys())},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Profile update failed: {str(e)}'}), 500

