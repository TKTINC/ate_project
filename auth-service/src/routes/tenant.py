"""
ATE Authentication Service - Tenant Management Routes
Multi-tenant organization management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from src.models.user import db, User, Tenant, AuditLog

tenant_bp = Blueprint('tenant', __name__)

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

@tenant_bp.route('/', methods=['GET'])
@jwt_required()
def get_tenants():
    """Get all tenants (super admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'super_admin':
        return jsonify({'error': 'Super admin access required'}), 403
    
    tenants = Tenant.query.all()
    return jsonify({
        'tenants': [tenant.to_dict() for tenant in tenants]
    })

@tenant_bp.route('/<tenant_id>', methods=['GET'])
@jwt_required()
def get_tenant(tenant_id):
    """Get specific tenant information"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Users can only access their own tenant unless they're super admin
    if user.tenant_id != tenant_id and user.role != 'super_admin':
        return jsonify({'error': 'Access denied'}), 403
    
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({'error': 'Tenant not found'}), 404
    
    return jsonify({
        'tenant': tenant.to_dict()
    })

@tenant_bp.route('/<tenant_id>', methods=['PUT'])
@jwt_required()
@require_permission('tenant:manage')
def update_tenant(tenant_id):
    """Update tenant information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Users can only update their own tenant unless they're super admin
        if user.tenant_id != tenant_id and user.role != 'super_admin':
            return jsonify({'error': 'Access denied'}), 403
        
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            tenant.name = data['name']
        if 'organization' in data:
            tenant.organization = data['organization']
        if 'settings' in data:
            tenant.settings.update(data['settings'])
        
        # Only super admin can update plan and limits
        if user.role == 'super_admin':
            if 'plan' in data:
                tenant.plan = data['plan']
            if 'max_analyses_per_month' in data:
                tenant.max_analyses_per_month = data['max_analyses_per_month']
            if 'max_codebase_size_mb' in data:
                tenant.max_codebase_size_mb = data['max_codebase_size_mb']
            if 'max_concurrent_analyses' in data:
                tenant.max_concurrent_analyses = data['max_concurrent_analyses']
            if 'active' in data:
                tenant.active = data['active']
        
        db.session.commit()
        
        # Create audit log
        audit_log = AuditLog(
            user_id=user.id,
            tenant_id=tenant.id,
            event_type='tenant_updated',
            event_data={'updated_fields': list(data.keys())},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Tenant updated successfully',
            'tenant': tenant.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Tenant update failed: {str(e)}'}), 500

@tenant_bp.route('/<tenant_id>/users', methods=['GET'])
@jwt_required()
@require_permission('users:view')
def get_tenant_users(tenant_id):
    """Get all users for a specific tenant"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Users can only view users from their own tenant unless they're super admin
    if user.tenant_id != tenant_id and user.role != 'super_admin':
        return jsonify({'error': 'Access denied'}), 403
    
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({'error': 'Tenant not found'}), 404
    
    users = User.query.filter_by(tenant_id=tenant_id).all()
    
    return jsonify({
        'users': [user.to_dict() for user in users],
        'total': len(users)
    })

@tenant_bp.route('/<tenant_id>/usage', methods=['GET'])
@jwt_required()
def get_tenant_usage(tenant_id):
    """Get tenant usage statistics"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Users can only view usage for their own tenant unless they're super admin
    if user.tenant_id != tenant_id and user.role != 'super_admin':
        return jsonify({'error': 'Access denied'}), 403
    
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({'error': 'Tenant not found'}), 404
    
    # TODO: Implement actual usage tracking from analysis service
    # For now, return mock data
    usage_data = {
        'current_month': {
            'analyses_performed': 5,
            'total_codebase_size_mb': 45.2,
            'concurrent_analyses': 1
        },
        'limits': {
            'max_analyses_per_month': tenant.max_analyses_per_month,
            'max_codebase_size_mb': tenant.max_codebase_size_mb,
            'max_concurrent_analyses': tenant.max_concurrent_analyses
        },
        'usage_percentage': {
            'analyses': 50.0,  # 5/10 * 100
            'storage': 45.2,   # 45.2/100 * 100
            'concurrent': 50.0  # 1/2 * 100
        }
    }
    
    return jsonify({
        'tenant_id': tenant_id,
        'usage': usage_data
    })

@tenant_bp.route('/<tenant_id>/audit-logs', methods=['GET'])
@jwt_required()
@require_permission('audit:view')
def get_tenant_audit_logs(tenant_id):
    """Get audit logs for a specific tenant"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Users can only view audit logs for their own tenant unless they're super admin
    if user.tenant_id != tenant_id and user.role != 'super_admin':
        return jsonify({'error': 'Access denied'}), 403
    
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({'error': 'Tenant not found'}), 404
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 100)
    event_type = request.args.get('event_type')
    
    # Build query
    query = AuditLog.query.filter_by(tenant_id=tenant_id)
    
    if event_type:
        query = query.filter_by(event_type=event_type)
    
    # Order by most recent first
    query = query.order_by(AuditLog.created_at.desc())
    
    # Paginate
    audit_logs = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'audit_logs': [log.to_dict() for log in audit_logs.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': audit_logs.total,
            'pages': audit_logs.pages,
            'has_next': audit_logs.has_next,
            'has_prev': audit_logs.has_prev
        }
    })

@tenant_bp.route('/', methods=['POST'])
@jwt_required()
def create_tenant():
    """Create new tenant (super admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or user.role != 'super_admin':
        return jsonify({'error': 'Super admin access required'}), 403
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'organization']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create new tenant
        tenant = Tenant(
            name=data['name'],
            organization=data['organization'],
            plan=data.get('plan', 'basic'),
            max_analyses_per_month=data.get('max_analyses_per_month', 10),
            max_codebase_size_mb=data.get('max_codebase_size_mb', 100),
            max_concurrent_analyses=data.get('max_concurrent_analyses', 2)
        )
        
        db.session.add(tenant)
        db.session.commit()
        
        # Create audit log
        audit_log = AuditLog(
            user_id=user.id,
            tenant_id=tenant.id,
            event_type='tenant_created',
            event_data={'name': tenant.name, 'organization': tenant.organization},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Tenant created successfully',
            'tenant': tenant.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Tenant creation failed: {str(e)}'}), 500

