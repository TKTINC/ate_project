"""
ATE Architecture Design Service - Authentication Utilities
"""

import jwt
import requests
from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime, timedelta

def require_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'status': 'error', 'message': 'Invalid authorization header format'}), 401
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Authentication token is missing'}), 401
        
        try:
            # Verify token with auth service
            auth_response = verify_token_with_auth_service(token)
            if not auth_response or not auth_response.get('valid'):
                return jsonify({'status': 'error', 'message': 'Invalid or expired token'}), 401
            
            # Store user info in request context
            request.current_user = auth_response.get('user', {})
            request.tenant_id = auth_response.get('tenant_id')
            
        except Exception as e:
            return jsonify({'status': 'error', 'message': 'Token verification failed'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def verify_token_with_auth_service(token):
    """Verify token with the authentication service"""
    try:
        auth_service_url = "http://localhost:5001"  # Auth service URL
        
        response = requests.post(
            f"{auth_service_url}/api/auth/verify",
            headers={'Authorization': f'Bearer {token}'},
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        print(f"Error verifying token with auth service: {e}")
        return None

def get_current_user():
    """Get current user from request context"""
    return getattr(request, 'current_user', {})

def get_tenant_id():
    """Get tenant ID from request context"""
    return getattr(request, 'tenant_id', None)

