"""
ATE Enterprise Integration Service - Service Discovery and Registry Routes
Comprehensive service management and orchestration
"""

from flask import Blueprint, request, jsonify
from src.models.user import db, ServiceRegistry, ServiceMetrics
from src.utils.auth import require_auth, get_tenant_id
from datetime import datetime, timedelta
import uuid
import json
import requests
import logging

logger = logging.getLogger(__name__)
services_bp = Blueprint('services', __name__)

@services_bp.route('/services', methods=['GET'])
@require_auth
def list_services():
    """List all registered services with filtering"""
    try:
        # Get query parameters
        service_type = request.args.get('service_type')
        environment = request.args.get('environment', 'development')
        health_status = request.args.get('health_status')
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        
        # Build query
        query = ServiceRegistry.query.filter_by(is_active=is_active)
        
        if service_type:
            query = query.filter_by(service_type=service_type)
        if environment:
            query = query.filter_by(environment=environment)
        if health_status:
            query = query.filter_by(health_status=health_status)
        
        services = query.all()
        
        return jsonify({
            'status': 'success',
            'services': [service.to_dict() for service in services],
            'total': len(services)
        })
        
    except Exception as e:
        logger.error(f"Error listing services: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@services_bp.route('/services/register', methods=['POST'])
@require_auth
def register_service():
    """Register a new service in the service registry"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['service_name', 'service_type', 'service_version', 'service_url', 'service_port']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
        
        # Check if service already exists
        existing_service = ServiceRegistry.query.filter_by(
            service_name=data['service_name'],
            environment=data.get('environment', 'development')
        ).first()
        
        if existing_service:
            return jsonify({'status': 'error', 'message': 'Service already registered'}), 409
        
        # Create new service registration
        service = ServiceRegistry(
            id=str(uuid.uuid4()),
            service_name=data['service_name'],
            service_type=data['service_type'],
            service_version=data['service_version'],
            service_url=data['service_url'],
            service_port=data['service_port'],
            health_endpoint=data.get('health_endpoint', '/health'),
            service_config=json.dumps(data.get('service_config', {})),
            environment=data.get('environment', 'development'),
            deployment_type=data.get('deployment_type', 'standalone'),
            health_check_interval=data.get('health_check_interval', 30),
            load_balancer_weight=data.get('load_balancer_weight', 100),
            max_connections=data.get('max_connections', 1000),
            tags=json.dumps(data.get('tags', [])),
            dependencies=json.dumps(data.get('dependencies', [])),
            capabilities=json.dumps(data.get('capabilities', []))
        )
        
        db.session.add(service)
        db.session.commit()
        
        logger.info(f"Service registered: {service.service_name}")
        
        return jsonify({
            'status': 'success',
            'message': 'Service registered successfully',
            'service': service.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error registering service: {e}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@services_bp.route('/services/<service_id>', methods=['GET'])
@require_auth
def get_service(service_id):
    """Get service details by ID"""
    try:
        service = ServiceRegistry.query.get(service_id)
        if not service:
            return jsonify({'status': 'error', 'message': 'Service not found'}), 404
        
        return jsonify({
            'status': 'success',
            'service': service.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error getting service: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@services_bp.route('/services/<service_id>/health', methods=['POST'])
@require_auth
def check_service_health(service_id):
    """Perform health check on a specific service"""
    try:
        service = ServiceRegistry.query.get(service_id)
        if not service:
            return jsonify({'status': 'error', 'message': 'Service not found'}), 404
        
        # Perform health check
        health_url = f"{service.service_url}:{service.service_port}{service.health_endpoint}"
        
        try:
            response = requests.get(health_url, timeout=10)
            if response.status_code == 200:
                service.health_status = 'healthy'
                service.consecutive_failures = 0
            else:
                service.health_status = 'unhealthy'
                service.consecutive_failures += 1
        except requests.RequestException:
            service.health_status = 'unreachable'
            service.consecutive_failures += 1
        
        service.last_health_check = datetime.utcnow()
        service.last_seen = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'service_id': service_id,
            'health_status': service.health_status,
            'last_health_check': service.last_health_check.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error checking service health: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@services_bp.route('/services/health/check-all', methods=['POST'])
@require_auth
def check_all_services_health():
    """Perform health check on all active services"""
    try:
        services = ServiceRegistry.query.filter_by(is_active=True).all()
        results = []
        
        for service in services:
            health_url = f"{service.service_url}:{service.service_port}{service.health_endpoint}"
            
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    service.health_status = 'healthy'
                    service.consecutive_failures = 0
                else:
                    service.health_status = 'unhealthy'
                    service.consecutive_failures += 1
            except requests.RequestException:
                service.health_status = 'unreachable'
                service.consecutive_failures += 1
            
            service.last_health_check = datetime.utcnow()
            service.last_seen = datetime.utcnow()
            
            results.append({
                'service_id': service.id,
                'service_name': service.service_name,
                'health_status': service.health_status,
                'consecutive_failures': service.consecutive_failures
            })
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Health check completed for all services',
            'results': results,
            'total_services': len(services)
        })
        
    except Exception as e:
        logger.error(f"Error checking all services health: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@services_bp.route('/services/<service_id>/metrics', methods=['POST'])
@require_auth
def record_service_metrics(service_id):
    """Record performance metrics for a service"""
    try:
        service = ServiceRegistry.query.get(service_id)
        if not service:
            return jsonify({'status': 'error', 'message': 'Service not found'}), 404
        
        data = request.get_json()
        
        # Create metrics record
        metrics = ServiceMetrics(
            id=str(uuid.uuid4()),
            service_id=service_id,
            response_time_avg=data.get('response_time_avg'),
            response_time_p95=data.get('response_time_p95'),
            response_time_p99=data.get('response_time_p99'),
            throughput=data.get('throughput'),
            error_rate=data.get('error_rate'),
            cpu_usage=data.get('cpu_usage'),
            memory_usage=data.get('memory_usage'),
            disk_usage=data.get('disk_usage'),
            network_in=data.get('network_in'),
            network_out=data.get('network_out'),
            active_connections=data.get('active_connections'),
            queue_size=data.get('queue_size'),
            cache_hit_rate=data.get('cache_hit_rate'),
            database_connections=data.get('database_connections'),
            custom_metrics=json.dumps(data.get('custom_metrics', {}))
        )
        
        db.session.add(metrics)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Metrics recorded successfully',
            'metrics_id': metrics.id
        })
        
    except Exception as e:
        logger.error(f"Error recording service metrics: {e}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@services_bp.route('/services/<service_id>/metrics', methods=['GET'])
@require_auth
def get_service_metrics(service_id):
    """Get performance metrics for a service"""
    try:
        service = ServiceRegistry.query.get(service_id)
        if not service:
            return jsonify({'status': 'error', 'message': 'Service not found'}), 404
        
        # Get time range parameters
        hours = int(request.args.get('hours', 24))
        since = datetime.utcnow() - timedelta(hours=hours)
        
        metrics = ServiceMetrics.query.filter(
            ServiceMetrics.service_id == service_id,
            ServiceMetrics.metric_timestamp >= since
        ).order_by(ServiceMetrics.metric_timestamp.desc()).all()
        
        return jsonify({
            'status': 'success',
            'service_id': service_id,
            'service_name': service.service_name,
            'metrics': [metric.to_dict() for metric in metrics],
            'total_records': len(metrics),
            'time_range_hours': hours
        })
        
    except Exception as e:
        logger.error(f"Error getting service metrics: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@services_bp.route('/services/discovery', methods=['GET'])
@require_auth
def service_discovery():
    """Service discovery endpoint for finding services by capabilities"""
    try:
        capability = request.args.get('capability')
        service_type = request.args.get('service_type')
        environment = request.args.get('environment', 'development')
        
        query = ServiceRegistry.query.filter_by(
            is_active=True,
            health_status='healthy',
            environment=environment
        )
        
        if service_type:
            query = query.filter_by(service_type=service_type)
        
        services = query.all()
        
        # Filter by capability if specified
        if capability:
            filtered_services = []
            for service in services:
                capabilities = json.loads(service.capabilities) if service.capabilities else []
                if capability in capabilities:
                    filtered_services.append(service)
            services = filtered_services
        
        return jsonify({
            'status': 'success',
            'services': [service.to_dict() for service in services],
            'total': len(services),
            'filters': {
                'capability': capability,
                'service_type': service_type,
                'environment': environment
            }
        })
        
    except Exception as e:
        logger.error(f"Error in service discovery: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

