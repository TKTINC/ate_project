"""
Shared utilities and models for the Agent Transformation Engine
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import hashlib
import uuid

class AnalysisResult:
    """Base class for analysis results across all ATE services."""
    
    def __init__(self, analysis_id: str, tenant_id: str, analysis_type: str):
        self.analysis_id = analysis_id
        self.tenant_id = tenant_id
        self.analysis_type = analysis_type
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.status = "in_progress"
        self.metadata = {}
        self.results = {}
        self.errors = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis result to dictionary."""
        return {
            'analysis_id': self.analysis_id,
            'tenant_id': self.tenant_id,
            'analysis_type': self.analysis_type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status,
            'metadata': self.metadata,
            'results': self.results,
            'errors': self.errors
        }
    
    def update_status(self, status: str, error: Optional[str] = None):
        """Update analysis status."""
        self.status = status
        self.updated_at = datetime.utcnow()
        if error:
            self.errors.append({
                'timestamp': datetime.utcnow().isoformat(),
                'error': error
            })

class CodebaseInfo:
    """Information about a codebase structure and characteristics."""
    
    def __init__(self, codebase_path: str):
        self.codebase_path = codebase_path
        self.total_files = 0
        self.total_lines = 0
        self.files_by_language = {}
        self.frameworks_detected = []
        self.architecture_patterns = []
        self.directory_structure = {}
        self.file_types = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert codebase info to dictionary."""
        return {
            'codebase_path': self.codebase_path,
            'total_files': self.total_files,
            'total_lines': self.total_lines,
            'files_by_language': self.files_by_language,
            'frameworks_detected': self.frameworks_detected,
            'architecture_patterns': self.architecture_patterns,
            'directory_structure': self.directory_structure,
            'file_types': self.file_types
        }

class BusinessDomain:
    """Represents a business domain identified in the codebase."""
    
    def __init__(self, name: str, confidence: float):
        self.name = name
        self.confidence = confidence
        self.keywords = []
        self.files = []
        self.functions = []
        self.classes = []
        self.description = ""
        self.business_processes = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert business domain to dictionary."""
        return {
            'name': self.name,
            'confidence': self.confidence,
            'keywords': self.keywords,
            'files': self.files,
            'functions': self.functions,
            'classes': self.classes,
            'description': self.description,
            'business_processes': self.business_processes
        }

class AgenticOpportunity:
    """Represents an identified opportunity for agentic AI implementation."""
    
    def __init__(self, opportunity_id: str, name: str, opportunity_type: str):
        self.opportunity_id = opportunity_id
        self.name = name
        self.opportunity_type = opportunity_type
        self.description = ""
        self.business_value_score = 0.0
        self.technical_feasibility_score = 0.0
        self.implementation_complexity = "medium"
        self.estimated_effort_hours = 0
        self.roi_projection = {}
        self.risk_factors = []
        self.implementation_approach = ""
        self.affected_components = []
        self.business_processes = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert opportunity to dictionary."""
        return {
            'opportunity_id': self.opportunity_id,
            'name': self.name,
            'opportunity_type': self.opportunity_type,
            'description': self.description,
            'business_value_score': self.business_value_score,
            'technical_feasibility_score': self.technical_feasibility_score,
            'implementation_complexity': self.implementation_complexity,
            'estimated_effort_hours': self.estimated_effort_hours,
            'roi_projection': self.roi_projection,
            'risk_factors': self.risk_factors,
            'implementation_approach': self.implementation_approach,
            'affected_components': self.affected_components,
            'business_processes': self.business_processes
        }

class ArchitectureSpecification:
    """Technical architecture specification for agentic implementation."""
    
    def __init__(self, spec_id: str, opportunity_id: str):
        self.spec_id = spec_id
        self.opportunity_id = opportunity_id
        self.architecture_pattern = ""
        self.components = []
        self.interfaces = []
        self.data_flows = []
        self.integration_points = []
        self.deployment_requirements = {}
        self.security_considerations = []
        self.performance_requirements = {}
        self.monitoring_requirements = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert architecture specification to dictionary."""
        return {
            'spec_id': self.spec_id,
            'opportunity_id': self.opportunity_id,
            'architecture_pattern': self.architecture_pattern,
            'components': self.components,
            'interfaces': self.interfaces,
            'data_flows': self.data_flows,
            'integration_points': self.integration_points,
            'deployment_requirements': self.deployment_requirements,
            'security_considerations': self.security_considerations,
            'performance_requirements': self.performance_requirements,
            'monitoring_requirements': self.monitoring_requirements
        }

class Tenant:
    """Multi-tenant organization information."""
    
    def __init__(self, tenant_id: str, name: str, organization: str):
        self.tenant_id = tenant_id
        self.name = name
        self.organization = organization
        self.plan = "basic"
        self.settings = {}
        self.created_at = datetime.utcnow()
        self.active = True
        self.usage_limits = {
            'max_analyses_per_month': 10,
            'max_codebase_size_mb': 100,
            'max_concurrent_analyses': 2
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tenant to dictionary."""
        return {
            'tenant_id': self.tenant_id,
            'name': self.name,
            'organization': self.organization,
            'plan': self.plan,
            'settings': self.settings,
            'created_at': self.created_at.isoformat(),
            'active': self.active,
            'usage_limits': self.usage_limits
        }

class User:
    """User account information."""
    
    def __init__(self, user_id: str, email: str, tenant_id: str):
        self.user_id = user_id
        self.email = email
        self.tenant_id = tenant_id
        self.role = "user"
        self.permissions = []
        self.first_name = ""
        self.last_name = ""
        self.created_at = datetime.utcnow()
        self.last_login = None
        self.active = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'tenant_id': self.tenant_id,
            'role': self.role,
            'permissions': self.permissions,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'active': self.active
        }

def generate_id(prefix: str = "") -> str:
    """Generate a unique identifier."""
    unique_id = str(uuid.uuid4())
    return f"{prefix}_{unique_id}" if prefix else unique_id

def calculate_hash(content: str) -> str:
    """Calculate SHA-256 hash of content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def serialize_datetime(dt: datetime) -> str:
    """Serialize datetime to ISO format string."""
    return dt.isoformat() if dt else None

def deserialize_datetime(dt_str: str) -> Optional[datetime]:
    """Deserialize ISO format string to datetime."""
    try:
        return datetime.fromisoformat(dt_str) if dt_str else None
    except ValueError:
        return None

def validate_tenant_id(tenant_id: str) -> bool:
    """Validate tenant ID format."""
    return bool(tenant_id and len(tenant_id) > 0 and '_' in tenant_id)

def validate_analysis_id(analysis_id: str) -> bool:
    """Validate analysis ID format."""
    return bool(analysis_id and len(analysis_id) > 0 and '_' in analysis_id)

class APIResponse:
    """Standardized API response format."""
    
    def __init__(self, success: bool = True, data: Any = None, error: str = None, metadata: Dict = None):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert API response to dictionary."""
        response = {
            'success': self.success,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
        
        if self.success:
            response['data'] = self.data
        else:
            response['error'] = self.error
        
        return response

class ConfigurationManager:
    """Manages configuration across ATE services."""
    
    def __init__(self):
        self._config = {}
    
    def load_config(self, config_dict: Dict[str, Any]):
        """Load configuration from dictionary."""
        self._config.update(config_dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

# Global configuration instance
config = ConfigurationManager()

