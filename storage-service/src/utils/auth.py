"""
ATE Storage Service - Authentication Utilities
JWT token validation and user context management
"""

import jwt
import requests
from functools import wraps
from flask import request, jsonify, current_app
import os

# Mock authentication for development - replace with actual auth service integration
def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401
        
        try:
            # Extract token from "Bearer <token>" format
            token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
            
            # For development, use a simple mock validation
            # In production, this would validate against the auth service
            if token == 'mock-token':
                # Mock user data
                request.current_user = {
                    'id': 'mock-user-id',
                    'email': 'test@example.com',
                    'tenant_id': 'mock-tenant-id',
                    'role': 'admin',
                    'permissions': ['storage:read', 'storage:write']
                }
            else:
                # Try to validate with auth service
                user_data = validate_token_with_auth_service(token)
                if not user_data:
                    return jsonify({'error': 'Invalid or expired token'}), 401
                
                request.current_user = user_data
            
            return f(*args, **kwargs)
            
        except (IndexError, jwt.InvalidTokenError) as e:
            return jsonify({'error': 'Invalid token format'}), 401
        except Exception as e:
            return jsonify({'error': f'Authentication failed: {str(e)}'}), 401
    
    return decorated_function

def get_current_user():
    """Get current authenticated user from request context"""
    return getattr(request, 'current_user', None)

def validate_token_with_auth_service(token):
    """Validate token with the authentication service"""
    try:
        # Get auth service URL from environment
        auth_service_url = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001')
        
        # Call auth service to verify token
        response = requests.get(
            f"{auth_service_url}/api/auth/verify",
            headers={'Authorization': f'Bearer {token}'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'id': data['user']['id'],
                'email': data['user']['email'],
                'tenant_id': data['user']['tenant_id'],
                'role': data['user']['role'],
                'permissions': data['user']['permissions']
            }
        
        return None
        
    except requests.RequestException:
        # If auth service is unavailable, fall back to mock for development
        if os.getenv('FLASK_ENV') == 'development':
            return {
                'id': 'dev-user-id',
                'email': 'dev@example.com',
                'tenant_id': 'dev-tenant-id',
                'role': 'admin',
                'permissions': ['*']
            }
        return None
    except Exception:
        return None

def check_permission(permission):
    """Check if current user has specific permission"""
    user = get_current_user()
    if not user:
        return False
    
    permissions = user.get('permissions', [])
    return '*' in permissions or permission in permissions or user.get('role') == 'super_admin'

def require_permission(permission):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not check_permission(permission):
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_tenant_id():
    """Get tenant ID for current user"""
    user = get_current_user()
    return user.get('tenant_id') if user else None

def is_super_admin():
    """Check if current user is super admin"""
    user = get_current_user()
    return user.get('role') == 'super_admin' if user else False

