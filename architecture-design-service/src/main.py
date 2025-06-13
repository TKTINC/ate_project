"""
ATE Architecture Design Service - Main Application
Comprehensive architecture design and implementation planning service
"""

import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.patterns import patterns_bp
from src.routes.designs import designs_bp
from src.routes.implementations import implementations_bp
from src.routes.deployments import deployments_bp
from src.routes.technologies import technologies_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'ate_architecture_design_service_secret_key_2024'

# Enable CORS for all routes
CORS(app, origins="*")

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(patterns_bp, url_prefix='/api')
app.register_blueprint(designs_bp, url_prefix='/api')
app.register_blueprint(implementations_bp, url_prefix='/api')
app.register_blueprint(deployments_bp, url_prefix='/api')
app.register_blueprint(technologies_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize database
with app.app_context():
    db.create_all()

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint for service monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'ATE Architecture Design Service',
        'version': '1.0.0',
        'port': 5006
    })

# Service information endpoint
@app.route('/api/info')
def service_info():
    """Service information and capabilities"""
    return jsonify({
        'service_name': 'ATE Architecture Design Service',
        'description': 'Comprehensive architecture design and implementation planning service',
        'version': '1.0.0',
        'capabilities': [
            'Architecture Pattern Library',
            'Design Template Engine',
            'Technical Specification Generation',
            'Implementation Planning',
            'Resource Allocation',
            'Deployment Strategy Generation',
            'Technology Stack Recommendations'
        ],
        'endpoints': {
            'patterns': '/api/patterns',
            'designs': '/api/designs',
            'implementations': '/api/implementations',
            'deployments': '/api/deployments',
            'technologies': '/api/technologies'
        }
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
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
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)

