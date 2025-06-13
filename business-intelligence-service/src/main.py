"""
ATE Business Intelligence Service - Main Application
Business domain mapping, process identification, and knowledge graph construction
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
from src.routes.domains import domains_bp
from src.routes.processes import processes_bp
from src.routes.knowledge import knowledge_bp
from src.routes.intelligence import intelligence_bp

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ate-business-intelligence-secret-change-in-production')
    
    # Database configuration
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Fallback to SQLite for development
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Service configuration
    app.config['ANALYSIS_SERVICE_URL'] = os.getenv('ANALYSIS_SERVICE_URL', 'http://localhost:5003')
    app.config['AUTH_SERVICE_URL'] = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001')
    app.config['STORAGE_SERVICE_URL'] = os.getenv('STORAGE_SERVICE_URL', 'http://localhost:5002')
    
    # Business intelligence configuration
    app.config['DOMAIN_CLASSIFICATION_CONFIDENCE_THRESHOLD'] = float(os.getenv('DOMAIN_CLASSIFICATION_CONFIDENCE_THRESHOLD', 0.7))
    app.config['PROCESS_IDENTIFICATION_CONFIDENCE_THRESHOLD'] = float(os.getenv('PROCESS_IDENTIFICATION_CONFIDENCE_THRESHOLD', 0.6))
    app.config['ENABLE_ADVANCED_NLP'] = os.getenv('ENABLE_ADVANCED_NLP', 'true').lower() == 'true'
    app.config['MAX_KNOWLEDGE_GRAPH_NODES'] = int(os.getenv('MAX_KNOWLEDGE_GRAPH_NODES', 10000))
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(domains_bp, url_prefix='/api/domains')
    app.register_blueprint(processes_bp, url_prefix='/api/processes')
    app.register_blueprint(knowledge_bp, url_prefix='/api/knowledge')
    app.register_blueprint(intelligence_bp, url_prefix='/api/intelligence')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'ate-business-intelligence-service',
            'version': '1.0.0',
            'capabilities': [
                'business-domain-classification',
                'business-process-identification',
                'knowledge-graph-construction',
                'business-intelligence-synthesis'
            ]
        })
    
    # Service capabilities endpoint
    @app.route('/capabilities')
    def get_capabilities():
        return jsonify({
            'domain_analysis': {
                'classification_types': [
                    'finance', 'healthcare', 'ecommerce', 'manufacturing', 
                    'education', 'logistics', 'hr', 'crm', 'inventory'
                ],
                'features': [
                    'entity_extraction', 'business_rule_identification', 
                    'domain_vocabulary_analysis', 'domain_relationship_mapping'
                ]
            },
            'process_analysis': {
                'process_types': [
                    'workflow', 'transaction', 'batch', 'event_driven',
                    'approval', 'notification', 'data_processing'
                ],
                'features': [
                    'process_step_identification', 'decision_point_analysis',
                    'data_flow_mapping', 'bottleneck_detection', 'optimization_recommendations'
                ]
            },
            'knowledge_graphs': {
                'graph_types': [
                    'entity_relationship', 'concept_hierarchy', 'process_flow',
                    'business_rule', 'stakeholder_network'
                ],
                'features': [
                    'semantic_analysis', 'relationship_inference', 'community_detection',
                    'centrality_analysis', 'graph_visualization'
                ]
            },
            'intelligence_synthesis': {
                'intelligence_types': [
                    'domain_summary', 'process_optimization', 'risk_assessment',
                    'opportunity_identification', 'stakeholder_analysis'
                ],
                'features': [
                    'insight_generation', 'recommendation_engine', 'impact_assessment',
                    'trend_analysis', 'business_value_calculation'
                ]
            },
            'configuration': {
                'domain_confidence_threshold': app.config['DOMAIN_CLASSIFICATION_CONFIDENCE_THRESHOLD'],
                'process_confidence_threshold': app.config['PROCESS_IDENTIFICATION_CONFIDENCE_THRESHOLD'],
                'advanced_nlp_enabled': app.config['ENABLE_ADVANCED_NLP'],
                'max_knowledge_graph_nodes': app.config['MAX_KNOWLEDGE_GRAPH_NODES']
            }
        })
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        return jsonify({'error': 'Service temporarily unavailable'}), 503
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Business intelligence service database initialized")
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5004))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

