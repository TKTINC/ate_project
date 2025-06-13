"""
ATE Analysis Service - Main Application
Multi-language code parsing and analysis service
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
from src.routes.parsing import parsing_bp
from src.routes.analysis import analysis_bp
from src.routes.quality import quality_bp
from src.routes.architecture import architecture_bp

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ate-analysis-secret-change-in-production')
    
    # Database configuration
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Fallback to SQLite for development
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Storage service configuration
    app.config['STORAGE_SERVICE_URL'] = os.getenv('STORAGE_SERVICE_URL', 'http://localhost:5002')
    app.config['AUTH_SERVICE_URL'] = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001')
    
    # Analysis configuration
    app.config['MAX_FILE_SIZE_MB'] = int(os.getenv('MAX_FILE_SIZE_MB', 50))
    app.config['PARSING_TIMEOUT_SECONDS'] = int(os.getenv('PARSING_TIMEOUT_SECONDS', 300))
    app.config['ENABLE_PARALLEL_PARSING'] = os.getenv('ENABLE_PARALLEL_PARSING', 'true').lower() == 'true'
    app.config['MAX_PARALLEL_WORKERS'] = int(os.getenv('MAX_PARALLEL_WORKERS', 4))
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(parsing_bp, url_prefix='/api/parse')
    app.register_blueprint(analysis_bp, url_prefix='/api/analyze')
    app.register_blueprint(quality_bp, url_prefix='/api/quality')
    app.register_blueprint(architecture_bp, url_prefix='/api/architecture')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'ate-analysis-service',
            'version': '1.0.0',
            'capabilities': [
                'multi-language-parsing',
                'dependency-analysis',
                'code-quality-assessment',
                'architectural-analysis'
            ]
        })
    
    # Service capabilities endpoint
    @app.route('/capabilities')
    def get_capabilities():
        return jsonify({
            'parsing': {
                'supported_languages': [
                    'python', 'javascript', 'typescript', 'java', 
                    'c', 'cpp', 'csharp', 'go', 'rust', 'php', 'ruby'
                ],
                'features': [
                    'ast_generation', 'semantic_analysis', 'symbol_resolution',
                    'import_analysis', 'function_extraction', 'class_extraction'
                ]
            },
            'analysis': {
                'dependency_analysis': [
                    'import_graphs', 'call_graphs', 'data_flow_analysis',
                    'circular_dependency_detection', 'modularity_assessment'
                ],
                'quality_analysis': [
                    'complexity_metrics', 'code_smells', 'technical_debt',
                    'maintainability_index', 'duplication_detection'
                ],
                'architectural_analysis': [
                    'pattern_detection', 'component_identification', 'layering_analysis',
                    'coupling_cohesion_metrics', 'architecture_quality_assessment'
                ]
            },
            'performance': {
                'max_file_size_mb': app.config['MAX_FILE_SIZE_MB'],
                'parsing_timeout_seconds': app.config['PARSING_TIMEOUT_SECONDS'],
                'parallel_processing': app.config['ENABLE_PARALLEL_PARSING'],
                'max_workers': app.config['MAX_PARALLEL_WORKERS']
            }
        })
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(413)
    def payload_too_large(error):
        return jsonify({
            'error': 'File too large',
            'max_size_mb': app.config['MAX_FILE_SIZE_MB']
        }), 413
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        return jsonify({'error': 'Service temporarily unavailable'}), 503
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Analysis service database initialized")
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5003))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

