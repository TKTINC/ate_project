"""
ATE API Gateway - Main Application
Central API gateway with authentication, routing, and load balancing
"""

import os
import sys
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
import time
import json

# Load environment variables
load_dotenv()

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ate-gateway-secret-change-in-production')
    
    # Service endpoints
    app.config['AUTH_SERVICE_URL'] = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001')
    app.config['STORAGE_SERVICE_URL'] = os.getenv('STORAGE_SERVICE_URL', 'http://localhost:5002')
    app.config['ANALYSIS_SERVICE_URL'] = os.getenv('ANALYSIS_SERVICE_URL', 'http://localhost:5003')
    app.config['BUSINESS_SERVICE_URL'] = os.getenv('BUSINESS_SERVICE_URL', 'http://localhost:5004')
    app.config['OPPORTUNITY_SERVICE_URL'] = os.getenv('OPPORTUNITY_SERVICE_URL', 'http://localhost:5005')
    app.config['ARCHITECTURE_SERVICE_URL'] = os.getenv('ARCHITECTURE_SERVICE_URL', 'http://localhost:5006')
    
    # Request timeout
    app.config['REQUEST_TIMEOUT'] = int(os.getenv('REQUEST_TIMEOUT', 30))
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'ate-api-gateway',
            'version': '1.0.0',
            'timestamp': time.time()
        })
    
    # Service health check endpoint
    @app.route('/health/services')
    def services_health():
        services = {
            'auth': app.config['AUTH_SERVICE_URL'],
            'storage': app.config['STORAGE_SERVICE_URL'],
            'analysis': app.config['ANALYSIS_SERVICE_URL'],
            'business': app.config['BUSINESS_SERVICE_URL'],
            'opportunity': app.config['OPPORTUNITY_SERVICE_URL'],
            'architecture': app.config['ARCHITECTURE_SERVICE_URL']
        }
        
        health_status = {}
        
        for service_name, service_url in services.items():
            try:
                response = requests.get(f"{service_url}/health", timeout=5)
                health_status[service_name] = {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'response_time_ms': response.elapsed.total_seconds() * 1000,
                    'url': service_url
                }
            except requests.RequestException as e:
                health_status[service_name] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'url': service_url
                }
        
        overall_status = 'healthy' if all(
            service['status'] == 'healthy' for service in health_status.values()
        ) else 'degraded'
        
        return jsonify({
            'overall_status': overall_status,
            'services': health_status,
            'timestamp': time.time()
        })
    
    # Authentication routes proxy
    @app.route('/api/auth/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def proxy_auth(path):
        return proxy_request('AUTH_SERVICE_URL', f'/api/auth/{path}')
    
    # Storage routes proxy
    @app.route('/api/storage/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def proxy_storage(path):
        return proxy_request('STORAGE_SERVICE_URL', f'/api/storage/{path}')
    
    @app.route('/api/projects/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def proxy_projects(path):
        return proxy_request('STORAGE_SERVICE_URL', f'/api/projects/{path}')
    
    @app.route('/api/analysis/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def proxy_analysis(path):
        return proxy_request('STORAGE_SERVICE_URL', f'/api/analysis/{path}')
    
    # Analysis engine routes proxy (when implemented)
    @app.route('/api/parse/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def proxy_parse(path):
        return proxy_request('ANALYSIS_SERVICE_URL', f'/api/parse/{path}')
    
    # Business intelligence routes proxy (when implemented)
    @app.route('/api/business/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def proxy_business(path):
        return proxy_request('BUSINESS_SERVICE_URL', f'/api/business/{path}')
    
    # Opportunity detection routes proxy (when implemented)
    @app.route('/api/opportunities/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def proxy_opportunities(path):
        return proxy_request('OPPORTUNITY_SERVICE_URL', f'/api/opportunities/{path}')
    
    # Architecture design routes proxy (when implemented)
    @app.route('/api/architecture/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def proxy_architecture(path):
        return proxy_request('ARCHITECTURE_SERVICE_URL', f'/api/architecture/{path}')
    
    def proxy_request(service_config_key, path):
        """Proxy request to backend service"""
        try:
            service_url = app.config[service_config_key]
            target_url = f"{service_url}{path}"
            
            # Forward query parameters
            if request.query_string:
                target_url += f"?{request.query_string.decode()}"
            
            # Prepare headers (exclude host header)
            headers = {
                key: value for key, value in request.headers.items()
                if key.lower() not in ['host', 'content-length']
            }
            
            # Prepare request data
            data = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                if request.is_json:
                    data = request.get_json()
                elif request.form:
                    data = request.form.to_dict()
                elif request.data:
                    data = request.data
            
            # Make request to backend service
            response = requests.request(
                method=request.method,
                url=target_url,
                headers=headers,
                json=data if request.is_json and data else None,
                data=data if not request.is_json and data else None,
                files=request.files if request.files else None,
                timeout=app.config['REQUEST_TIMEOUT']
            )
            
            # Create response
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            response_headers = [
                (name, value) for name, value in response.headers.items()
                if name.lower() not in excluded_headers
            ]
            
            return Response(
                response.content,
                status=response.status_code,
                headers=response_headers
            )
            
        except requests.RequestException as e:
            return jsonify({
                'error': 'Service unavailable',
                'service': service_config_key,
                'details': str(e)
            }), 503
        except Exception as e:
            return jsonify({
                'error': 'Gateway error',
                'details': str(e)
            }), 500
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint not found',
            'path': request.path,
            'method': request.method
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal gateway error',
            'details': str(error)
        }), 500
    
    # Request logging middleware
    @app.before_request
    def log_request():
        if app.config.get('LOG_REQUESTS', False):
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {request.method} {request.path}")
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

