"""
ATE Opportunity Detection Service - Authentication Utilities
Integration with authentication service
"""

import requests
from functools import wraps
from flask import request, jsonify, current_app, g
import jwt

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401
        
        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
            
            # Verify token with auth service
            auth_service_url = current_app.config['AUTH_SERVICE_URL']
            response = requests.post(
                f"{auth_service_url}/api/auth/verify",
                headers={'Authorization': f'Bearer {token}'},
                timeout=5
            )
            
            if response.status_code != 200:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            user_data = response.json()
            g.current_user = user_data['user']
            
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({'error': f'Authentication failed: {str(e)}'}), 401
    
    return decorated_function

def get_current_user():
    """Get current authenticated user"""
    return getattr(g, 'current_user', None)

def verify_tenant_access(tenant_id):
    """Verify user has access to tenant"""
    current_user = get_current_user()
    if not current_user:
        return False
    
    return current_user.get('tenant_id') == tenant_id

def get_auth_headers():
    """Get authentication headers for service-to-service calls"""
    auth_header = request.headers.get('Authorization')
    if auth_header:
        return {'Authorization': auth_header}
    return {}

