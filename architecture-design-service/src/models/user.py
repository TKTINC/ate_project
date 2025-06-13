"""
ATE Architecture Design Service - Database Models
Comprehensive models for architecture design and implementation planning
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication integration"""
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

class ArchitecturePattern(db.Model):
    """Architecture patterns and templates"""
    __tablename__ = 'architecture_patterns'
    
    id = db.Column(db.String(36), primary_key=True)
    pattern_name = db.Column(db.String(200), nullable=False)
    pattern_type = db.Column(db.String(50), nullable=False)  # automation, modernization, optimization, integration
    pattern_category = db.Column(db.String(50), nullable=False)  # microservices, serverless, event_driven, etc.
    pattern_description = db.Column(db.Text)
    
    # Pattern definition
    pattern_definition = db.Column(db.JSON)  # YAML/JSON pattern definition
    technology_stack = db.Column(db.JSON)  # Required technologies
    design_principles = db.Column(db.JSON)  # Design principles and guidelines
    implementation_guidelines = db.Column(db.JSON)  # Implementation best practices
    
    # Pattern metadata
    complexity_level = db.Column(db.String(20), default='medium')  # low, medium, high
    maturity_level = db.Column(db.String(20), default='stable')  # experimental, beta, stable
    industry_focus = db.Column(db.JSON)  # Target industries
    use_cases = db.Column(db.JSON)  # Common use cases
    
    # Pattern relationships
    compatible_patterns = db.Column(db.JSON)  # Compatible pattern IDs
    alternative_patterns = db.Column(db.JSON)  # Alternative pattern IDs
    prerequisite_patterns = db.Column(db.JSON)  # Required prerequisite patterns
    
    # Usage and effectiveness
    usage_count = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Float, default=0.8)
    average_implementation_time = db.Column(db.Float)  # Average implementation time in months
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'pattern_name': self.pattern_name,
            'pattern_type': self.pattern_type,
            'pattern_category': self.pattern_category,
            'pattern_description': self.pattern_description,
            'pattern_definition': self.pattern_definition,
            'technology_stack': self.technology_stack,
            'design_principles': self.design_principles,
            'implementation_guidelines': self.implementation_guidelines,
            'complexity_level': self.complexity_level,
            'maturity_level': self.maturity_level,
            'industry_focus': self.industry_focus,
            'use_cases': self.use_cases,
            'compatible_patterns': self.compatible_patterns,
            'alternative_patterns': self.alternative_patterns,
            'prerequisite_patterns': self.prerequisite_patterns,
            'usage_count': self.usage_count,
            'success_rate': self.success_rate,
            'average_implementation_time': self.average_implementation_time,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'is_active': self.is_active
        }

class ArchitectureDesign(db.Model):
    """Generated architecture designs"""
    __tablename__ = 'architecture_designs'
    
    id = db.Column(db.String(36), primary_key=True)
    tenant_id = db.Column(db.String(36), nullable=False)
    opportunity_id = db.Column(db.String(36), nullable=False)
    business_case_id = db.Column(db.String(36))
    
    # Design metadata
    design_name = db.Column(db.String(200), nullable=False)
    design_type = db.Column(db.String(50), nullable=False)  # automation, modernization, optimization, integration
    design_scope = db.Column(db.String(50), nullable=False)  # component, service, system, enterprise
    design_status = db.Column(db.String(50), default='draft')  # draft, review, approved, implemented
    
    # Architecture specification
    architecture_overview = db.Column(db.JSON)  # High-level architecture description
    system_architecture = db.Column(db.JSON)  # Detailed system architecture
    component_design = db.Column(db.JSON)  # Component-level design
    data_architecture = db.Column(db.JSON)  # Data architecture and flow
    integration_architecture = db.Column(db.JSON)  # Integration patterns and APIs
    security_architecture = db.Column(db.JSON)  # Security design and controls
    deployment_architecture = db.Column(db.JSON)  # Deployment and infrastructure
    
    # Technology specifications
    technology_stack = db.Column(db.JSON)  # Selected technology stack
    technology_rationale = db.Column(db.JSON)  # Technology selection rationale
    architecture_patterns = db.Column(db.JSON)  # Applied architecture patterns
    design_decisions = db.Column(db.JSON)  # Key design decisions and trade-offs
    
    # Implementation planning
    implementation_phases = db.Column(db.JSON)  # Implementation phases and milestones
    resource_requirements = db.Column(db.JSON)  # Resource and skill requirements
    timeline_estimate = db.Column(db.JSON)  # Implementation timeline
    risk_assessment = db.Column(db.JSON)  # Architecture-specific risks
    
    # Quality attributes
    performance_requirements = db.Column(db.JSON)  # Performance specifications
    scalability_design = db.Column(db.JSON)  # Scalability considerations
    reliability_design = db.Column(db.JSON)  # Reliability and availability
    maintainability_design = db.Column(db.JSON)  # Maintainability considerations
    
    # Documentation and artifacts
    design_documentation = db.Column(db.JSON)  # Generated documentation
    architecture_diagrams = db.Column(db.JSON)  # Diagram specifications
    technical_specifications = db.Column(db.JSON)  # Detailed technical specs
    implementation_guides = db.Column(db.JSON)  # Implementation guidance
    
    # Validation and approval
    design_validation = db.Column(db.JSON)  # Design validation results
    stakeholder_approval = db.Column(db.JSON)  # Approval tracking
    compliance_assessment = db.Column(db.JSON)  # Compliance validation
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'opportunity_id': self.opportunity_id,
            'business_case_id': self.business_case_id,
            'design_name': self.design_name,
            'design_type': self.design_type,
            'design_scope': self.design_scope,
            'design_status': self.design_status,
            'architecture_overview': self.architecture_overview,
            'system_architecture': self.system_architecture,
            'component_design': self.component_design,
            'data_architecture': self.data_architecture,
            'integration_architecture': self.integration_architecture,
            'security_architecture': self.security_architecture,
            'deployment_architecture': self.deployment_architecture,
            'technology_stack': self.technology_stack,
            'technology_rationale': self.technology_rationale,
            'architecture_patterns': self.architecture_patterns,
            'design_decisions': self.design_decisions,
            'implementation_phases': self.implementation_phases,
            'resource_requirements': self.resource_requirements,
            'timeline_estimate': self.timeline_estimate,
            'risk_assessment': self.risk_assessment,
            'performance_requirements': self.performance_requirements,
            'scalability_design': self.scalability_design,
            'reliability_design': self.reliability_design,
            'maintainability_design': self.maintainability_design,
            'design_documentation': self.design_documentation,
            'architecture_diagrams': self.architecture_diagrams,
            'technical_specifications': self.technical_specifications,
            'implementation_guides': self.implementation_guides,
            'design_validation': self.design_validation,
            'stakeholder_approval': self.stakeholder_approval,
            'compliance_assessment': self.compliance_assessment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'approved_by': self.approved_by
        }

class TechnologyStack(db.Model):
    """Technology stack definitions and recommendations"""
    __tablename__ = 'technology_stacks'
    
    id = db.Column(db.String(36), primary_key=True)
    stack_name = db.Column(db.String(200), nullable=False)
    stack_type = db.Column(db.String(50), nullable=False)  # frontend, backend, database, infrastructure
    stack_category = db.Column(db.String(50), nullable=False)  # web, mobile, data, ai_ml, etc.
    
    # Stack definition
    technologies = db.Column(db.JSON)  # List of technologies in the stack
    technology_versions = db.Column(db.JSON)  # Recommended versions
    compatibility_matrix = db.Column(db.JSON)  # Technology compatibility
    configuration_templates = db.Column(db.JSON)  # Configuration templates
    
    # Stack characteristics
    complexity_level = db.Column(db.String(20), default='medium')
    learning_curve = db.Column(db.String(20), default='medium')
    community_support = db.Column(db.String(20), default='good')
    enterprise_readiness = db.Column(db.String(20), default='production')
    
    # Cost and licensing
    licensing_model = db.Column(db.String(50))  # open_source, commercial, hybrid
    estimated_cost = db.Column(db.JSON)  # Cost estimates
    vendor_dependencies = db.Column(db.JSON)  # Vendor lock-in considerations
    
    # Performance and scalability
    performance_characteristics = db.Column(db.JSON)
    scalability_limits = db.Column(db.JSON)
    resource_requirements = db.Column(db.JSON)
    
    # Use case suitability
    suitable_for = db.Column(db.JSON)  # Suitable use cases
    not_suitable_for = db.Column(db.JSON)  # Unsuitable use cases
    industry_adoption = db.Column(db.JSON)  # Industry adoption patterns
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'stack_name': self.stack_name,
            'stack_type': self.stack_type,
            'stack_category': self.stack_category,
            'technologies': self.technologies,
            'technology_versions': self.technology_versions,
            'compatibility_matrix': self.compatibility_matrix,
            'configuration_templates': self.configuration_templates,
            'complexity_level': self.complexity_level,
            'learning_curve': self.learning_curve,
            'community_support': self.community_support,
            'enterprise_readiness': self.enterprise_readiness,
            'licensing_model': self.licensing_model,
            'estimated_cost': self.estimated_cost,
            'vendor_dependencies': self.vendor_dependencies,
            'performance_characteristics': self.performance_characteristics,
            'scalability_limits': self.scalability_limits,
            'resource_requirements': self.resource_requirements,
            'suitable_for': self.suitable_for,
            'not_suitable_for': self.not_suitable_for,
            'industry_adoption': self.industry_adoption,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'is_active': self.is_active
        }

class ImplementationPlan(db.Model):
    """Implementation plans and project management"""
    __tablename__ = 'implementation_plans'
    
    id = db.Column(db.String(36), primary_key=True)
    tenant_id = db.Column(db.String(36), nullable=False)
    architecture_design_id = db.Column(db.String(36), nullable=False)
    opportunity_id = db.Column(db.String(36), nullable=False)
    
    # Plan metadata
    plan_name = db.Column(db.String(200), nullable=False)
    plan_type = db.Column(db.String(50), nullable=False)  # implementation, migration, deployment
    plan_status = db.Column(db.String(50), default='draft')  # draft, approved, in_progress, completed
    
    # Project structure
    project_phases = db.Column(db.JSON)  # Detailed project phases
    work_breakdown = db.Column(db.JSON)  # Work breakdown structure
    deliverables = db.Column(db.JSON)  # Project deliverables
    milestones = db.Column(db.JSON)  # Key milestones
    
    # Timeline and scheduling
    timeline_estimate = db.Column(db.JSON)  # Detailed timeline
    critical_path = db.Column(db.JSON)  # Critical path analysis
    dependencies = db.Column(db.JSON)  # Task dependencies
    schedule_buffer = db.Column(db.JSON)  # Schedule buffers and contingency
    
    # Resource planning
    resource_requirements = db.Column(db.JSON)  # Detailed resource needs
    skill_requirements = db.Column(db.JSON)  # Required skills and expertise
    team_structure = db.Column(db.JSON)  # Recommended team structure
    external_resources = db.Column(db.JSON)  # External resource needs
    
    # Cost and budget
    cost_breakdown = db.Column(db.JSON)  # Detailed cost breakdown
    budget_allocation = db.Column(db.JSON)  # Budget allocation by phase
    cost_tracking = db.Column(db.JSON)  # Cost tracking framework
    
    # Risk management
    risk_assessment = db.Column(db.JSON)  # Implementation risks
    risk_mitigation = db.Column(db.JSON)  # Risk mitigation strategies
    contingency_plans = db.Column(db.JSON)  # Contingency planning
    
    # Quality and governance
    quality_gates = db.Column(db.JSON)  # Quality gates and checkpoints
    governance_framework = db.Column(db.JSON)  # Project governance
    approval_process = db.Column(db.JSON)  # Approval workflows
    
    # Monitoring and control
    success_criteria = db.Column(db.JSON)  # Success criteria and KPIs
    monitoring_framework = db.Column(db.JSON)  # Progress monitoring
    reporting_schedule = db.Column(db.JSON)  # Reporting requirements
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'architecture_design_id': self.architecture_design_id,
            'opportunity_id': self.opportunity_id,
            'plan_name': self.plan_name,
            'plan_type': self.plan_type,
            'plan_status': self.plan_status,
            'project_phases': self.project_phases,
            'work_breakdown': self.work_breakdown,
            'deliverables': self.deliverables,
            'milestones': self.milestones,
            'timeline_estimate': self.timeline_estimate,
            'critical_path': self.critical_path,
            'dependencies': self.dependencies,
            'schedule_buffer': self.schedule_buffer,
            'resource_requirements': self.resource_requirements,
            'skill_requirements': self.skill_requirements,
            'team_structure': self.team_structure,
            'external_resources': self.external_resources,
            'cost_breakdown': self.cost_breakdown,
            'budget_allocation': self.budget_allocation,
            'cost_tracking': self.cost_tracking,
            'risk_assessment': self.risk_assessment,
            'risk_mitigation': self.risk_mitigation,
            'contingency_plans': self.contingency_plans,
            'quality_gates': self.quality_gates,
            'governance_framework': self.governance_framework,
            'approval_process': self.approval_process,
            'success_criteria': self.success_criteria,
            'monitoring_framework': self.monitoring_framework,
            'reporting_schedule': self.reporting_schedule,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'approved_by': self.approved_by
        }

class DeploymentStrategy(db.Model):
    """Deployment strategies and configurations"""
    __tablename__ = 'deployment_strategies'
    
    id = db.Column(db.String(36), primary_key=True)
    tenant_id = db.Column(db.String(36), nullable=False)
    architecture_design_id = db.Column(db.String(36), nullable=False)
    implementation_plan_id = db.Column(db.String(36))
    
    # Strategy metadata
    strategy_name = db.Column(db.String(200), nullable=False)
    deployment_type = db.Column(db.String(50), nullable=False)  # blue_green, rolling, canary, big_bang
    environment_type = db.Column(db.String(50), nullable=False)  # cloud, on_premise, hybrid
    strategy_status = db.Column(db.String(50), default='draft')
    
    # Environment configuration
    environment_design = db.Column(db.JSON)  # Environment architecture
    infrastructure_requirements = db.Column(db.JSON)  # Infrastructure needs
    network_configuration = db.Column(db.JSON)  # Network design
    security_configuration = db.Column(db.JSON)  # Security setup
    
    # Deployment pipeline
    deployment_pipeline = db.Column(db.JSON)  # CI/CD pipeline design
    automation_scripts = db.Column(db.JSON)  # Deployment automation
    testing_strategy = db.Column(db.JSON)  # Testing approach
    rollback_procedures = db.Column(db.JSON)  # Rollback strategies
    
    # Operational readiness
    monitoring_setup = db.Column(db.JSON)  # Monitoring configuration
    logging_configuration = db.Column(db.JSON)  # Logging setup
    alerting_rules = db.Column(db.JSON)  # Alerting configuration
    backup_strategy = db.Column(db.JSON)  # Backup and recovery
    
    # Performance and scaling
    performance_targets = db.Column(db.JSON)  # Performance requirements
    scaling_configuration = db.Column(db.JSON)  # Auto-scaling setup
    capacity_planning = db.Column(db.JSON)  # Capacity requirements
    load_testing_plan = db.Column(db.JSON)  # Load testing strategy
    
    # Compliance and governance
    compliance_requirements = db.Column(db.JSON)  # Compliance needs
    governance_controls = db.Column(db.JSON)  # Governance framework
    audit_configuration = db.Column(db.JSON)  # Audit logging
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'architecture_design_id': self.architecture_design_id,
            'implementation_plan_id': self.implementation_plan_id,
            'strategy_name': self.strategy_name,
            'deployment_type': self.deployment_type,
            'environment_type': self.environment_type,
            'strategy_status': self.strategy_status,
            'environment_design': self.environment_design,
            'infrastructure_requirements': self.infrastructure_requirements,
            'network_configuration': self.network_configuration,
            'security_configuration': self.security_configuration,
            'deployment_pipeline': self.deployment_pipeline,
            'automation_scripts': self.automation_scripts,
            'testing_strategy': self.testing_strategy,
            'rollback_procedures': self.rollback_procedures,
            'monitoring_setup': self.monitoring_setup,
            'logging_configuration': self.logging_configuration,
            'alerting_rules': self.alerting_rules,
            'backup_strategy': self.backup_strategy,
            'performance_targets': self.performance_targets,
            'scaling_configuration': self.scaling_configuration,
            'capacity_planning': self.capacity_planning,
            'load_testing_plan': self.load_testing_plan,
            'compliance_requirements': self.compliance_requirements,
            'governance_controls': self.governance_controls,
            'audit_configuration': self.audit_configuration,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }

