"""
Agent Transformation Engine - Authentication Service
Main Flask application entry point for authentication and authorization service.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from datetime import timedelta

from models.user import User, Tenant
from services.auth_service import AuthService
from services.tenant_service import TenantService
from utils.security import SecurityUtils
from utils.database import DatabaseUtils

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://ate:ate@localhost/ate_auth')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Initialize services
auth_service = AuthService(db)
tenant_service = TenantService(db)
security_utils = SecurityUtils()
db_utils = DatabaseUtils(db)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for service monitoring."""
    return jsonify({
        'status': 'healthy',
        'service': 'auth-service',
        'version': '1.0.0'
    })

@app.route('/auth/login', methods=['POST'])
def login():
    """Authenticate user and return access token."""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = auth_service.authenticate_user(email, password)
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'tenant_id': user.tenant_id,
                'role': user.role,
                'permissions': user.permissions
            }
        )
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'tenant_id': user.tenant_id
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auth/register', methods=['POST'])
def register():
    """Register new user account."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'tenant_name', 'organization']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create tenant first
        tenant = tenant_service.create_tenant(
            name=data['tenant_name'],
            organization=data['organization'],
            plan=data.get('plan', 'basic')
        )
        
        # Create user
        user = auth_service.create_user(
            email=data['email'],
            password=data['password'],
            tenant_id=tenant.id,
            role=data.get('role', 'admin'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'tenant_id': user.tenant_id,
                'role': user.role,
                'permissions': user.permissions
            }
        )
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'tenant_id': user.tenant_id
            },
            'tenant': {
                'id': tenant.id,
                'name': tenant.name,
                'organization': tenant.organization
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auth/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token and return user information."""
    try:
        user_id = get_jwt_identity()
        user = auth_service.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'tenant_id': user.tenant_id,
                'permissions': user.permissions
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tenants/<int:tenant_id>/users', methods=['GET'])
@jwt_required()
def get_tenant_users(tenant_id):
    """Get all users for a specific tenant."""
    try:
        current_user_id = get_jwt_identity()
        current_user = auth_service.get_user_by_id(current_user_id)
        
        # Check if user has permission to view tenant users
        if current_user.tenant_id != tenant_id and current_user.role != 'super_admin':
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        users = auth_service.get_tenant_users(tenant_id)
        
        return jsonify({
            'users': [{
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            } for user in users]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tenants/<int:tenant_id>/settings', methods=['GET', 'PUT'])
@jwt_required()
def tenant_settings(tenant_id):
    """Get or update tenant settings."""
    try:
        current_user_id = get_jwt_identity()
        current_user = auth_service.get_user_by_id(current_user_id)
        
        # Check permissions
        if current_user.tenant_id != tenant_id or current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        if request.method == 'GET':
            tenant = tenant_service.get_tenant_by_id(tenant_id)
            return jsonify({
                'tenant': {
                    'id': tenant.id,
                    'name': tenant.name,
                    'organization': tenant.organization,
                    'plan': tenant.plan,
                    'settings': tenant.settings,
                    'created_at': tenant.created_at.isoformat()
                }
            })
        
        elif request.method == 'PUT':
            data = request.get_json()
            tenant = tenant_service.update_tenant_settings(tenant_id, data)
            
            return jsonify({
                'tenant': {
                    'id': tenant.id,
                    'name': tenant.name,
                    'organization': tenant.organization,
                    'plan': tenant.plan,
                    'settings': tenant.settings
                }
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Run the application
    app.run(host='0.0.0.0', port=5001, debug=os.getenv('FLASK_ENV') == 'development')

