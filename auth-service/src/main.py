"""
ATE Authentication Service - Main Application
Enterprise-grade authentication with multi-tenant support
"""

import os
import sys
from datetime import timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db
from src.routes.auth import auth_bp
from src.routes.tenant import tenant_bp
from src.routes.user import user_bp

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ate-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'ate-jwt-secret-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Database configuration
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Fallback to SQLite for development
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tenant_bp, url_prefix='/api/tenants')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'ate-auth-service',
            'version': '1.0.0'
        })
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authorization token required'}), 401
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default super admin if it doesn't exist
        from src.models.user import User, Tenant
        
        super_admin = User.query.filter_by(email='admin@ate.local').first()
        if not super_admin:
            # Create default tenant
            default_tenant = Tenant(
                name='ATE System',
                organization='Agent Transformation Engine',
                plan='enterprise'
            )
            db.session.add(default_tenant)
            db.session.flush()  # Get the tenant ID
            
            # Create super admin user
            super_admin = User(
                email='admin@ate.local',
                first_name='System',
                last_name='Administrator',
                tenant_id=default_tenant.id,
                role='super_admin',
                permissions=['*'],
                active=True,
                email_verified=True
            )
            super_admin.set_password('admin123')  # Change this in production!
            
            db.session.add(super_admin)
            db.session.commit()
            
            print("Created default super admin: admin@ate.local / admin123")
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

