"""
ATE Business Intelligence Service - Authentication Utilities
Integration with authentication service
"""

import requests
from functools import wraps
from flask import request, jsonify, current_app, g

def require_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            # Verify token with auth service
            auth_service_url = current_app.config['AUTH_SERVICE_URL']
            response = requests.post(
                f"{auth_service_url}/api/auth/verify",
                json={'token': token},
                timeout=5
            )
            
            if response.status_code != 200:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            user_data = response.json()
            g.current_user = user_data['user']
            
            return f(*args, **kwargs)
            
        except requests.RequestException:
            return jsonify({'error': 'Authentication service unavailable'}), 503
    
    return decorated_function

def get_current_user():
    """Get current authenticated user from request context"""
    return getattr(g, 'current_user', None)

