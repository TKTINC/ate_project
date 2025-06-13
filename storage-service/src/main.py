"""
ATE Storage Service - Main Application
Secure multi-tenant codebase storage with encryption
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db
from src.routes.storage import storage_bp
from src.routes.projects import projects_bp
from src.routes.analysis import analysis_bp

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ate-storage-secret-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_SIZE', 1073741824))  # 1GB default
    
    # Database configuration
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Fallback to SQLite for development
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Storage configuration
    app.config['STORAGE_TYPE'] = os.getenv('STORAGE_TYPE', 'local')  # local, s3, minio
    app.config['STORAGE_BUCKET'] = os.getenv('STORAGE_BUCKET', 'ate-codebases')
    app.config['STORAGE_ENDPOINT'] = os.getenv('STORAGE_ENDPOINT')
    app.config['STORAGE_ACCESS_KEY'] = os.getenv('STORAGE_ACCESS_KEY')
    app.config['STORAGE_SECRET_KEY'] = os.getenv('STORAGE_SECRET_KEY')
    app.config['LOCAL_STORAGE_PATH'] = os.getenv('LOCAL_STORAGE_PATH', '/tmp/ate-storage')
    
    # Encryption configuration
    app.config['MASTER_KEY'] = os.getenv('MASTER_KEY', 'change-this-master-key-in-production')
    app.config['ENCRYPTION_ALGORITHM'] = os.getenv('ENCRYPTION_ALGORITHM', 'AES-256-GCM')
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(storage_bp, url_prefix='/api/storage')
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'ate-storage-service',
            'version': '1.0.0',
            'storage_type': app.config['STORAGE_TYPE']
        })
    
    # Error handlers
    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            'error': 'File too large',
            'max_size_bytes': app.config['MAX_CONTENT_LENGTH']
        }), 413
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Create database tables and setup
    with app.app_context():
        db.create_all()
        
        # Create local storage directory if using local storage
        if app.config['STORAGE_TYPE'] == 'local':
            os.makedirs(app.config['LOCAL_STORAGE_PATH'], exist_ok=True)
            print(f"Local storage directory: {app.config['LOCAL_STORAGE_PATH']}")
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

