"""
ATE Enterprise Integration Service - Database Models
Comprehensive service orchestration and integration models
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

class ServiceRegistry(db.Model):
    """Service registry for service discovery and health monitoring"""
    __tablename__ = 'service_registry'
    
    id = db.Column(db.String(36), primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)  # core, analysis, business, opportunity, architecture
    service_version = db.Column(db.String(20), nullable=False)
    service_url = db.Column(db.String(200), nullable=False)
    service_port = db.Column(db.Integer, nullable=False)
    health_endpoint = db.Column(db.String(100), nullable=False, default='/health')
    
    # Service configuration
    service_config = db.Column(db.Text)  # JSON configuration
    environment = db.Column(db.String(20), nullable=False, default='development')
    deployment_type = db.Column(db.String(20), nullable=False, default='standalone')
    
    # Health and status
    health_status = db.Column(db.String(20), nullable=False, default='unknown')
    last_health_check = db.Column(db.DateTime)
    health_check_interval = db.Column(db.Integer, default=30)  # seconds
    consecutive_failures = db.Column(db.Integer, default=0)
    
    # Load balancing and routing
    load_balancer_weight = db.Column(db.Integer, default=100)
    max_connections = db.Column(db.Integer, default=1000)
    current_connections = db.Column(db.Integer, default=0)
    
    # Metadata
    tags = db.Column(db.Text)  # JSON array of tags
    dependencies = db.Column(db.Text)  # JSON array of service dependencies
    capabilities = db.Column(db.Text)  # JSON array of service capabilities
    
    # Timestamps
    registered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Status flags
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_maintenance = db.Column(db.Boolean, nullable=False, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'service_name': self.service_name,
            'service_type': self.service_type,
            'service_version': self.service_version,
            'service_url': self.service_url,
            'service_port': self.service_port,
            'health_endpoint': self.health_endpoint,
            'service_config': json.loads(self.service_config) if self.service_config else {},
            'environment': self.environment,
            'deployment_type': self.deployment_type,
            'health_status': self.health_status,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'health_check_interval': self.health_check_interval,
            'consecutive_failures': self.consecutive_failures,
            'load_balancer_weight': self.load_balancer_weight,
            'max_connections': self.max_connections,
            'current_connections': self.current_connections,
            'tags': json.loads(self.tags) if self.tags else [],
            'dependencies': json.loads(self.dependencies) if self.dependencies else [],
            'capabilities': json.loads(self.capabilities) if self.capabilities else [],
            'registered_at': self.registered_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'is_active': self.is_active,
            'is_maintenance': self.is_maintenance
        }

class ServiceMetrics(db.Model):
    """Service performance and health metrics"""
    __tablename__ = 'service_metrics'
    
    id = db.Column(db.String(36), primary_key=True)
    service_id = db.Column(db.String(36), db.ForeignKey('service_registry.id'), nullable=False)
    metric_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Performance metrics
    response_time_avg = db.Column(db.Float)  # milliseconds
    response_time_p95 = db.Column(db.Float)  # milliseconds
    response_time_p99 = db.Column(db.Float)  # milliseconds
    throughput = db.Column(db.Float)  # requests per second
    error_rate = db.Column(db.Float)  # percentage
    
    # Resource metrics
    cpu_usage = db.Column(db.Float)  # percentage
    memory_usage = db.Column(db.Float)  # percentage
    disk_usage = db.Column(db.Float)  # percentage
    network_in = db.Column(db.Float)  # bytes per second
    network_out = db.Column(db.Float)  # bytes per second
    
    # Application metrics
    active_connections = db.Column(db.Integer)
    queue_size = db.Column(db.Integer)
    cache_hit_rate = db.Column(db.Float)  # percentage
    database_connections = db.Column(db.Integer)
    
    # Custom metrics
    custom_metrics = db.Column(db.Text)  # JSON object for service-specific metrics
    
    def to_dict(self):
        return {
            'id': self.id,
            'service_id': self.service_id,
            'metric_timestamp': self.metric_timestamp.isoformat(),
            'response_time_avg': self.response_time_avg,
            'response_time_p95': self.response_time_p95,
            'response_time_p99': self.response_time_p99,
            'throughput': self.throughput,
            'error_rate': self.error_rate,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'disk_usage': self.disk_usage,
            'network_in': self.network_in,
            'network_out': self.network_out,
            'active_connections': self.active_connections,
            'queue_size': self.queue_size,
            'cache_hit_rate': self.cache_hit_rate,
            'database_connections': self.database_connections,
            'custom_metrics': json.loads(self.custom_metrics) if self.custom_metrics else {}
        }

class IntegrationEndpoint(db.Model):
    """External system integration endpoints"""
    __tablename__ = 'integration_endpoints'
    
    id = db.Column(db.String(36), primary_key=True)
    tenant_id = db.Column(db.String(36), nullable=False)
    endpoint_name = db.Column(db.String(100), nullable=False)
    endpoint_type = db.Column(db.String(50), nullable=False)  # rest_api, soap, database, file_system, message_queue
    endpoint_url = db.Column(db.String(500), nullable=False)
    
    # Authentication and security
    auth_type = db.Column(db.String(50))  # none, basic, bearer, oauth2, api_key, certificate
    auth_config = db.Column(db.Text)  # JSON configuration for authentication
    ssl_config = db.Column(db.Text)  # JSON configuration for SSL/TLS
    
    # Connection configuration
    connection_config = db.Column(db.Text)  # JSON configuration
    timeout_seconds = db.Column(db.Integer, default=30)
    retry_attempts = db.Column(db.Integer, default=3)
    retry_delay = db.Column(db.Integer, default=1)  # seconds
    
    # Data transformation
    request_transform = db.Column(db.Text)  # JSON transformation rules
    response_transform = db.Column(db.Text)  # JSON transformation rules
    data_format = db.Column(db.String(20), default='json')  # json, xml, csv, binary
    
    # Health monitoring
    health_check_enabled = db.Column(db.Boolean, default=True)
    health_check_interval = db.Column(db.Integer, default=60)  # seconds
    health_status = db.Column(db.String(20), default='unknown')
    last_health_check = db.Column(db.DateTime)
    
    # Usage tracking
    total_requests = db.Column(db.Integer, default=0)
    successful_requests = db.Column(db.Integer, default=0)
    failed_requests = db.Column(db.Integer, default=0)
    last_request_time = db.Column(db.DateTime)
    
    # Metadata
    description = db.Column(db.Text)
    tags = db.Column(db.Text)  # JSON array
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))
    
    # Status flags
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_maintenance = db.Column(db.Boolean, nullable=False, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'endpoint_name': self.endpoint_name,
            'endpoint_type': self.endpoint_type,
            'endpoint_url': self.endpoint_url,
            'auth_type': self.auth_type,
            'auth_config': json.loads(self.auth_config) if self.auth_config else {},
            'ssl_config': json.loads(self.ssl_config) if self.ssl_config else {},
            'connection_config': json.loads(self.connection_config) if self.connection_config else {},
            'timeout_seconds': self.timeout_seconds,
            'retry_attempts': self.retry_attempts,
            'retry_delay': self.retry_delay,
            'request_transform': json.loads(self.request_transform) if self.request_transform else {},
            'response_transform': json.loads(self.response_transform) if self.response_transform else {},
            'data_format': self.data_format,
            'health_check_enabled': self.health_check_enabled,
            'health_check_interval': self.health_check_interval,
            'health_status': self.health_status,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'last_request_time': self.last_request_time.isoformat() if self.last_request_time else None,
            'description': self.description,
            'tags': json.loads(self.tags) if self.tags else [],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by,
            'is_active': self.is_active,
            'is_maintenance': self.is_maintenance
        }

class WorkflowExecution(db.Model):
    """Workflow execution tracking and orchestration"""
    __tablename__ = 'workflow_executions'
    
    id = db.Column(db.String(36), primary_key=True)
    tenant_id = db.Column(db.String(36), nullable=False)
    workflow_name = db.Column(db.String(100), nullable=False)
    workflow_type = db.Column(db.String(50), nullable=False)  # transformation, analysis, deployment
    workflow_version = db.Column(db.String(20), nullable=False)
    
    # Execution context
    execution_context = db.Column(db.Text)  # JSON context data
    input_data = db.Column(db.Text)  # JSON input data
    output_data = db.Column(db.Text)  # JSON output data
    
    # Execution status
    execution_status = db.Column(db.String(20), nullable=False, default='pending')  # pending, running, completed, failed, cancelled
    current_step = db.Column(db.String(100))
    total_steps = db.Column(db.Integer)
    completed_steps = db.Column(db.Integer, default=0)
    
    # Timing
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    estimated_duration = db.Column(db.Integer)  # seconds
    actual_duration = db.Column(db.Integer)  # seconds
    
    # Error handling
    error_message = db.Column(db.Text)
    error_details = db.Column(db.Text)  # JSON error details
    retry_count = db.Column(db.Integer, default=0)
    max_retries = db.Column(db.Integer, default=3)
    
    # Progress tracking
    progress_percentage = db.Column(db.Float, default=0.0)
    progress_details = db.Column(db.Text)  # JSON progress details
    
    # Resource usage
    cpu_time = db.Column(db.Float)  # seconds
    memory_peak = db.Column(db.Float)  # MB
    network_usage = db.Column(db.Float)  # bytes
    
    # Metadata
    triggered_by = db.Column(db.String(100))
    trigger_type = db.Column(db.String(50))  # manual, scheduled, event, api
    priority = db.Column(db.Integer, default=5)  # 1-10, 10 is highest
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'workflow_name': self.workflow_name,
            'workflow_type': self.workflow_type,
            'workflow_version': self.workflow_version,
            'execution_context': json.loads(self.execution_context) if self.execution_context else {},
            'input_data': json.loads(self.input_data) if self.input_data else {},
            'output_data': json.loads(self.output_data) if self.output_data else {},
            'execution_status': self.execution_status,
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'completed_steps': self.completed_steps,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'estimated_duration': self.estimated_duration,
            'actual_duration': self.actual_duration,
            'error_message': self.error_message,
            'error_details': json.loads(self.error_details) if self.error_details else {},
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'progress_percentage': self.progress_percentage,
            'progress_details': json.loads(self.progress_details) if self.progress_details else {},
            'cpu_time': self.cpu_time,
            'memory_peak': self.memory_peak,
            'network_usage': self.network_usage,
            'triggered_by': self.triggered_by,
            'trigger_type': self.trigger_type,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

