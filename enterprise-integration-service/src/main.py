"""
ATE Enterprise Integration Service - Main Application
Comprehensive service orchestration and enterprise integration platform
"""

import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.services import services_bp
from src.routes.integration import integration_bp
from src.routes.orchestration import orchestration_bp
from src.routes.monitoring import monitoring_bp
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'ate-enterprise-integration-secret-key-2024'

# Enable CORS for all routes
CORS(app, origins="*")

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(services_bp, url_prefix='/api')
app.register_blueprint(integration_bp, url_prefix='/api')
app.register_blueprint(orchestration_bp, url_prefix='/api')
app.register_blueprint(monitoring_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize database
with app.app_context():
    db.create_all()
    logger.info("Database initialized successfully")

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint for service monitoring"""
    try:
        # Check database connectivity
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'service': 'enterprise-integration-service',
            'version': '1.0.0',
            'timestamp': '2024-01-01T00:00:00Z',
            'checks': {
                'database': 'healthy',
                'service_registry': 'healthy',
                'integration_endpoints': 'healthy'
            }
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'enterprise-integration-service',
            'version': '1.0.0',
            'timestamp': '2024-01-01T00:00:00Z',
            'error': str(e)
        }), 503

# Metrics endpoint for Prometheus
@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# Service information endpoint
@app.route('/api/info')
def service_info():
    """Service information and capabilities"""
    return jsonify({
        'service_name': 'enterprise-integration-service',
        'service_type': 'integration',
        'version': '1.0.0',
        'description': 'ATE Enterprise Integration and Service Orchestration Platform',
        'capabilities': [
            'service_discovery',
            'service_orchestration',
            'health_monitoring',
            'load_balancing',
            'external_integration',
            'workflow_execution',
            'metrics_collection',
            'enterprise_connectivity'
        ],
        'endpoints': {
            'services': '/api/services',
            'integration': '/api/integration',
            'orchestration': '/api/orchestration',
            'monitoring': '/api/monitoring',
            'health': '/health',
            'metrics': '/metrics'
        },
        'dependencies': [
            'auth-service',
            'storage-service',
            'analysis-service',
            'business-intelligence-service',
            'opportunity-detection-service',
            'architecture-design-service'
        ]
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve static files and SPA routing"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({
                'message': 'ATE Enterprise Integration Service',
                'version': '1.0.0',
                'status': 'running',
                'api_docs': '/api/info'
            })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting ATE Enterprise Integration Service on port 5007")
    app.run(host='0.0.0.0', port=5007, debug=True)

