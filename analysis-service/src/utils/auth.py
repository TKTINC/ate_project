"""
ATE Analysis Service - Authentication Utilities
JWT token validation and user context management
"""

import jwt
import requests
from functools import wraps
from flask import request, jsonify, current_app, g

def require_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        
        if not token:
            return jsonify({'error': 'No authentication token provided'}), 401
        
        try:
            # Validate token with auth service
            user_data = validate_token_with_auth_service(token)
            if not user_data:
                return jsonify({'error': 'Invalid authentication token'}), 401
            
            # Store user data in Flask's g object for use in the request
            g.current_user = user_data
            
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({'error': f'Authentication failed: {str(e)}'}), 401
    
    return decorated_function

def get_token_from_request():
    """Extract JWT token from request headers"""
    auth_header = request.headers.get('Authorization')
    
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    
    return None

def validate_token_with_auth_service(token):
    """Validate token with the authentication service"""
    try:
        auth_service_url = current_app.config['AUTH_SERVICE_URL']
        
        response = requests.post(
            f"{auth_service_url}/api/auth/validate",
            headers={'Authorization': f'Bearer {token}'},
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json().get('user')
        else:
            return None
            
    except Exception as e:
        current_app.logger.error(f"Token validation failed: {str(e)}")
        return None

def get_current_user():
    """Get current user from Flask's g object"""
    return getattr(g, 'current_user', None)

def require_tenant_access(tenant_id):
    """Check if current user has access to specified tenant"""
    current_user = get_current_user()
    
    if not current_user:
        return False
    
    # Check if user belongs to the tenant
    if current_user.get('tenant_id') != tenant_id:
        return False
    
    return True

def require_role(required_role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_current_user()
            
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = current_user.get('role', 'user')
            
            # Define role hierarchy
            role_hierarchy = {
                'user': 0,
                'admin': 1,
                'super_admin': 2
            }
            
            required_level = role_hierarchy.get(required_role, 999)
            user_level = role_hierarchy.get(user_role, -1)
            
            if user_level < required_level:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

