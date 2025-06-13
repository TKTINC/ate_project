"""
ATE Opportunity Detection Service - Database Models
Comprehensive models for opportunity detection, scoring, and business case generation
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

class OpportunityAnalysis(db.Model):
    """Main opportunity analysis tracking"""
    __tablename__ = 'opportunity_analyses'
    
    id = db.Column(db.String(36), primary_key=True)
    tenant_id = db.Column(db.String(36), nullable=False, index=True)
    codebase_id = db.Column(db.String(36), nullable=False)
    business_analysis_id = db.Column(db.String(36), nullable=False)
    analysis_name = db.Column(db.String(200), nullable=False)
    analysis_status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Analysis configuration
    analysis_config = db.Column(db.JSON, default=dict)
    
    # Overall analysis results
    total_opportunities = db.Column(db.Integer, default=0)
    high_value_opportunities = db.Column(db.Integer, default=0)
    total_estimated_value = db.Column(db.Float, default=0.0)
    average_roi = db.Column(db.Float, default=0.0)
    confidence_score = db.Column(db.Float, default=0.0)
    
    # Analysis summary
    analysis_summary = db.Column(db.JSON, default=dict)
    
    # Relationships
    opportunities = db.relationship('TransformationOpportunity', backref='analysis', lazy=True, cascade='all, delete-orphan')
    business_cases = db.relationship('BusinessCase', backref='analysis', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_details=False):
        result = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'codebase_id': self.codebase_id,
            'business_analysis_id': self.business_analysis_id,
            'analysis_name': self.analysis_name,
            'analysis_status': self.analysis_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'total_opportunities': self.total_opportunities,
            'high_value_opportunities': self.high_value_opportunities,
            'total_estimated_value': self.total_estimated_value,
            'average_roi': self.average_roi,
            'confidence_score': self.confidence_score,
            'analysis_summary': self.analysis_summary
        }
        
        if include_details:
            result.update({
                'analysis_config': self.analysis_config,
                'opportunities': [opp.to_dict() for opp in self.opportunities],
                'business_cases': [bc.to_dict() for bc in self.business_cases]
            })
        
        return result

class TransformationOpportunity(db.Model):
    """Individual transformation opportunities"""
    __tablename__ = 'transformation_opportunities'
    
    id = db.Column(db.String(36), primary_key=True)
    analysis_id = db.Column(db.String(36), db.ForeignKey('opportunity_analyses.id'), nullable=False)
    
    # Opportunity identification
    opportunity_name = db.Column(db.String(200), nullable=False)
    opportunity_type = db.Column(db.String(100), nullable=False)  # automation, modernization, optimization, integration
    opportunity_category = db.Column(db.String(100), nullable=False)  # process, architecture, technology, business
    opportunity_scope = db.Column(db.String(100), default='component')  # component, service, domain, system
    
    # Source information
    source_domain = db.Column(db.String(100))
    source_processes = db.Column(db.JSON, default=list)
    source_components = db.Column(db.JSON, default=list)
    affected_stakeholders = db.Column(db.JSON, default=list)
    
    # Opportunity scoring
    opportunity_score = db.Column(db.Float, nullable=False)  # 0-100 overall score
    confidence_score = db.Column(db.Float, nullable=False)  # 0-1 confidence
    priority_score = db.Column(db.Float, nullable=False)  # 0-100 priority
    
    # Business value assessment
    estimated_annual_value = db.Column(db.Float, default=0.0)
    estimated_cost_savings = db.Column(db.Float, default=0.0)
    estimated_revenue_impact = db.Column(db.Float, default=0.0)
    estimated_efficiency_gain = db.Column(db.Float, default=0.0)  # percentage
    
    # Implementation assessment
    implementation_complexity = db.Column(db.String(50), default='medium')  # low, medium, high
    estimated_effort_months = db.Column(db.Float, default=0.0)
    estimated_cost = db.Column(db.Float, default=0.0)
    required_skills = db.Column(db.JSON, default=list)
    
    # Risk assessment
    implementation_risk = db.Column(db.String(50), default='medium')  # low, medium, high
    business_risk = db.Column(db.String(50), default='medium')
    technical_risk = db.Column(db.String(50), default='medium')
    risk_factors = db.Column(db.JSON, default=list)
    mitigation_strategies = db.Column(db.JSON, default=list)
    
    # ROI calculation
    estimated_roi = db.Column(db.Float, default=0.0)  # percentage
    payback_period_months = db.Column(db.Float, default=0.0)
    npv = db.Column(db.Float, default=0.0)  # Net Present Value
    irr = db.Column(db.Float, default=0.0)  # Internal Rate of Return
    
    # Detailed analysis
    opportunity_description = db.Column(db.Text)
    current_state_analysis = db.Column(db.JSON, default=dict)
    proposed_solution = db.Column(db.JSON, default=dict)
    implementation_approach = db.Column(db.JSON, default=dict)
    success_metrics = db.Column(db.JSON, default=list)
    
    # Dependencies and prerequisites
    dependencies = db.Column(db.JSON, default=list)
    prerequisites = db.Column(db.JSON, default=list)
    
    # Timeline and milestones
    estimated_timeline = db.Column(db.JSON, default=dict)
    key_milestones = db.Column(db.JSON, default=list)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'opportunity_name': self.opportunity_name,
            'opportunity_type': self.opportunity_type,
            'opportunity_category': self.opportunity_category,
            'opportunity_scope': self.opportunity_scope,
            'source_domain': self.source_domain,
            'source_processes': self.source_processes,
            'source_components': self.source_components,
            'affected_stakeholders': self.affected_stakeholders,
            'opportunity_score': self.opportunity_score,
            'confidence_score': self.confidence_score,
            'priority_score': self.priority_score,
            'estimated_annual_value': self.estimated_annual_value,
            'estimated_cost_savings': self.estimated_cost_savings,
            'estimated_revenue_impact': self.estimated_revenue_impact,
            'estimated_efficiency_gain': self.estimated_efficiency_gain,
            'implementation_complexity': self.implementation_complexity,
            'estimated_effort_months': self.estimated_effort_months,
            'estimated_cost': self.estimated_cost,
            'required_skills': self.required_skills,
            'implementation_risk': self.implementation_risk,
            'business_risk': self.business_risk,
            'technical_risk': self.technical_risk,
            'risk_factors': self.risk_factors,
            'mitigation_strategies': self.mitigation_strategies,
            'estimated_roi': self.estimated_roi,
            'payback_period_months': self.payback_period_months,
            'npv': self.npv,
            'irr': self.irr,
            'opportunity_description': self.opportunity_description,
            'current_state_analysis': self.current_state_analysis,
            'proposed_solution': self.proposed_solution,
            'implementation_approach': self.implementation_approach,
            'success_metrics': self.success_metrics,
            'dependencies': self.dependencies,
            'prerequisites': self.prerequisites,
            'estimated_timeline': self.estimated_timeline,
            'key_milestones': self.key_milestones,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class BusinessCase(db.Model):
    """Generated business cases for opportunities"""
    __tablename__ = 'business_cases'
    
    id = db.Column(db.String(36), primary_key=True)
    analysis_id = db.Column(db.String(36), db.ForeignKey('opportunity_analyses.id'), nullable=False)
    opportunity_id = db.Column(db.String(36), db.ForeignKey('transformation_opportunities.id'), nullable=True)
    
    # Business case metadata
    case_name = db.Column(db.String(200), nullable=False)
    case_type = db.Column(db.String(100), default='single_opportunity')  # single_opportunity, portfolio, strategic
    case_status = db.Column(db.String(50), default='draft')
    
    # Executive summary
    executive_summary = db.Column(db.Text)
    problem_statement = db.Column(db.Text)
    proposed_solution = db.Column(db.Text)
    key_benefits = db.Column(db.JSON, default=list)
    
    # Financial analysis
    financial_summary = db.Column(db.JSON, default=dict)
    cost_breakdown = db.Column(db.JSON, default=dict)
    benefit_analysis = db.Column(db.JSON, default=dict)
    roi_analysis = db.Column(db.JSON, default=dict)
    sensitivity_analysis = db.Column(db.JSON, default=dict)
    
    # Implementation plan
    implementation_strategy = db.Column(db.JSON, default=dict)
    project_timeline = db.Column(db.JSON, default=dict)
    resource_requirements = db.Column(db.JSON, default=dict)
    risk_management_plan = db.Column(db.JSON, default=dict)
    
    # Success criteria and metrics
    success_criteria = db.Column(db.JSON, default=list)
    kpis = db.Column(db.JSON, default=list)
    measurement_plan = db.Column(db.JSON, default=dict)
    
    # Stakeholder analysis
    stakeholder_analysis = db.Column(db.JSON, default=dict)
    change_management_plan = db.Column(db.JSON, default=dict)
    communication_plan = db.Column(db.JSON, default=dict)
    
    # Recommendations
    recommendations = db.Column(db.JSON, default=list)
    next_steps = db.Column(db.JSON, default=list)
    decision_criteria = db.Column(db.JSON, default=dict)
    
    # Approval tracking
    approval_status = db.Column(db.String(50), default='pending')
    approved_by = db.Column(db.String(100))
    approved_at = db.Column(db.DateTime)
    approval_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    opportunity = db.relationship('TransformationOpportunity', backref='business_cases')
    
    def to_dict(self):
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'opportunity_id': self.opportunity_id,
            'case_name': self.case_name,
            'case_type': self.case_type,
            'case_status': self.case_status,
            'executive_summary': self.executive_summary,
            'problem_statement': self.problem_statement,
            'proposed_solution': self.proposed_solution,
            'key_benefits': self.key_benefits,
            'financial_summary': self.financial_summary,
            'cost_breakdown': self.cost_breakdown,
            'benefit_analysis': self.benefit_analysis,
            'roi_analysis': self.roi_analysis,
            'sensitivity_analysis': self.sensitivity_analysis,
            'implementation_strategy': self.implementation_strategy,
            'project_timeline': self.project_timeline,
            'resource_requirements': self.resource_requirements,
            'risk_management_plan': self.risk_management_plan,
            'success_criteria': self.success_criteria,
            'kpis': self.kpis,
            'measurement_plan': self.measurement_plan,
            'stakeholder_analysis': self.stakeholder_analysis,
            'change_management_plan': self.change_management_plan,
            'communication_plan': self.communication_plan,
            'recommendations': self.recommendations,
            'next_steps': self.next_steps,
            'decision_criteria': self.decision_criteria,
            'approval_status': self.approval_status,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'approval_notes': self.approval_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class OpportunityPattern(db.Model):
    """Learned patterns for opportunity detection"""
    __tablename__ = 'opportunity_patterns'
    
    id = db.Column(db.String(36), primary_key=True)
    pattern_name = db.Column(db.String(200), nullable=False)
    pattern_type = db.Column(db.String(100), nullable=False)
    pattern_category = db.Column(db.String(100), nullable=False)
    
    # Pattern definition
    pattern_description = db.Column(db.Text)
    detection_criteria = db.Column(db.JSON, default=dict)
    pattern_indicators = db.Column(db.JSON, default=list)
    
    # Pattern scoring
    pattern_weight = db.Column(db.Float, default=1.0)
    confidence_threshold = db.Column(db.Float, default=0.7)
    
    # Pattern effectiveness
    success_rate = db.Column(db.Float, default=0.0)
    usage_count = db.Column(db.Integer, default=0)
    
    # Pattern metadata
    created_by = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'pattern_name': self.pattern_name,
            'pattern_type': self.pattern_type,
            'pattern_category': self.pattern_category,
            'pattern_description': self.pattern_description,
            'detection_criteria': self.detection_criteria,
            'pattern_indicators': self.pattern_indicators,
            'pattern_weight': self.pattern_weight,
            'confidence_threshold': self.confidence_threshold,
            'success_rate': self.success_rate,
            'usage_count': self.usage_count,
            'created_by': self.created_by,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

