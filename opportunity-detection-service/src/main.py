"""
ATE Opportunity Detection Service - Main Application
AI-powered opportunity detection and business case generation service
"""

import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.opportunities import opportunities_bp
from src.routes.business_cases import business_cases_bp
from src.routes.patterns import patterns_bp
from src.routes.analysis import analysis_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration
app.config['SECRET_KEY'] = 'ate-opportunity-detection-service-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Service configuration
app.config['SERVICE_NAME'] = 'ate-opportunity-detection-service'
app.config['SERVICE_VERSION'] = '1.0.0'
app.config['SERVICE_PORT'] = 5005

# External service URLs
app.config['AUTH_SERVICE_URL'] = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001')
app.config['STORAGE_SERVICE_URL'] = os.getenv('STORAGE_SERVICE_URL', 'http://localhost:5002')
app.config['ANALYSIS_SERVICE_URL'] = os.getenv('ANALYSIS_SERVICE_URL', 'http://localhost:5003')
app.config['BUSINESS_INTELLIGENCE_SERVICE_URL'] = os.getenv('BUSINESS_INTELLIGENCE_SERVICE_URL', 'http://localhost:5004')

# Opportunity detection configuration
app.config['OPPORTUNITY_DETECTION_CONFIDENCE_THRESHOLD'] = 0.7
app.config['MAX_OPPORTUNITIES_PER_ANALYSIS'] = 50
app.config['ROI_CALCULATION_DISCOUNT_RATE'] = 0.10  # 10% discount rate for NPV
app.config['DEFAULT_PROJECT_DURATION_YEARS'] = 3

# Business case configuration
app.config['BUSINESS_CASE_TEMPLATE_VERSION'] = '1.0'
app.config['FINANCIAL_MODEL_CURRENCY'] = 'USD'
app.config['RISK_ASSESSMENT_FRAMEWORK'] = 'standard'

# Enable CORS for all routes
CORS(app, origins="*")

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(opportunities_bp, url_prefix='/api/opportunities')
app.register_blueprint(business_cases_bp, url_prefix='/api/business-cases')
app.register_blueprint(patterns_bp, url_prefix='/api/patterns')
app.register_blueprint(analysis_bp, url_prefix='/api/analysis')

# Initialize database
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': app.config['SERVICE_NAME'],
        'version': app.config['SERVICE_VERSION'],
        'capabilities': [
            'ai-opportunity-detection',
            'business-value-calculation',
            'roi-assessment',
            'implementation-complexity-analysis',
            'business-case-generation',
            'pattern-recognition',
            'risk-assessment'
        ]
    })

@app.route('/config')
def get_config():
    """Get service configuration"""
    return jsonify({
        'service_name': app.config['SERVICE_NAME'],
        'service_version': app.config['SERVICE_VERSION'],
        'opportunity_detection': {
            'confidence_threshold': app.config['OPPORTUNITY_DETECTION_CONFIDENCE_THRESHOLD'],
            'max_opportunities': app.config['MAX_OPPORTUNITIES_PER_ANALYSIS']
        },
        'financial_modeling': {
            'discount_rate': app.config['ROI_CALCULATION_DISCOUNT_RATE'],
            'default_duration_years': app.config['DEFAULT_PROJECT_DURATION_YEARS'],
            'currency': app.config['FINANCIAL_MODEL_CURRENCY']
        },
        'external_services': {
            'auth_service': app.config['AUTH_SERVICE_URL'],
            'storage_service': app.config['STORAGE_SERVICE_URL'],
            'analysis_service': app.config['ANALYSIS_SERVICE_URL'],
            'business_intelligence_service': app.config['BUSINESS_INTELLIGENCE_SERVICE_URL']
        }
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve static files"""
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

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', app.config['SERVICE_PORT']))
    app.run(host='0.0.0.0', port=port, debug=True)

