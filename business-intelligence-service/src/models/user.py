"""
ATE Business Intelligence Service - Database Models
Models for business domain mapping, process identification, and knowledge graphs
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import json

db = SQLAlchemy()

class BusinessAnalysis(db.Model):
    """Main business analysis record for a codebase"""
    __tablename__ = 'business_analyses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    codebase_id = db.Column(db.String(36), nullable=False, index=True)  # Reference to analysis service
    tenant_id = db.Column(db.String(36), nullable=False, index=True)
    
    # Analysis metadata
    analysis_status = db.Column(db.String(50), default='pending')  # pending, analyzing, completed, failed
    analysis_started_at = db.Column(db.DateTime, default=datetime.utcnow)
    analysis_completed_at = db.Column(db.DateTime)
    analysis_duration_seconds = db.Column(db.Float)
    
    # Business analysis configuration
    analysis_config = db.Column(db.JSON, default=dict)
    
    # Overall business intelligence summary
    business_summary = db.Column(db.JSON, default=dict)
    confidence_score = db.Column(db.Float)  # Overall confidence in analysis
    
    # Error information
    analysis_errors = db.Column(db.JSON, default=list)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    domains = db.relationship('BusinessDomain', backref='analysis', lazy=True, cascade='all, delete-orphan')
    processes = db.relationship('BusinessProcess', backref='analysis', lazy=True, cascade='all, delete-orphan')
    knowledge_graphs = db.relationship('KnowledgeGraph', backref='analysis', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_details=False):
        result = {
            'id': self.id,
            'codebase_id': self.codebase_id,
            'tenant_id': self.tenant_id,
            'analysis_status': self.analysis_status,
            'analysis_started_at': self.analysis_started_at.isoformat(),
            'analysis_completed_at': self.analysis_completed_at.isoformat() if self.analysis_completed_at else None,
            'analysis_duration_seconds': self.analysis_duration_seconds,
            'analysis_config': self.analysis_config,
            'business_summary': self.business_summary,
            'confidence_score': self.confidence_score,
            'analysis_errors': self.analysis_errors,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_details:
            result['domains'] = [domain.to_dict() for domain in self.domains]
            result['processes'] = [process.to_dict() for process in self.processes]
            result['knowledge_graphs'] = [kg.to_dict() for kg in self.knowledge_graphs]
            
        return result

class BusinessDomain(db.Model):
    """Business domain classification and mapping"""
    __tablename__ = 'business_domains'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = db.Column(db.String(36), db.ForeignKey('business_analyses.id'), nullable=False)
    
    # Domain identification
    domain_name = db.Column(db.String(200), nullable=False)
    domain_category = db.Column(db.String(100))  # e.g., 'finance', 'healthcare', 'ecommerce'
    domain_subcategory = db.Column(db.String(100))
    confidence_score = db.Column(db.Float)
    
    # Domain characteristics
    business_entities = db.Column(db.JSON, default=list)  # Identified business entities
    business_rules = db.Column(db.JSON, default=list)  # Business rules and constraints
    domain_vocabulary = db.Column(db.JSON, default=list)  # Domain-specific terms
    
    # Code mapping
    related_files = db.Column(db.JSON, default=list)  # Files associated with this domain
    related_functions = db.Column(db.JSON, default=list)  # Functions in this domain
    related_classes = db.Column(db.JSON, default=list)  # Classes in this domain
    
    # Domain metrics
    complexity_score = db.Column(db.Float)
    coverage_percentage = db.Column(db.Float)  # Percentage of codebase in this domain
    
    # Domain relationships
    parent_domain_id = db.Column(db.String(36), db.ForeignKey('business_domains.id'))
    subdomain_relationships = db.Column(db.JSON, default=list)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'domain_name': self.domain_name,
            'domain_category': self.domain_category,
            'domain_subcategory': self.domain_subcategory,
            'confidence_score': self.confidence_score,
            'business_entities': self.business_entities,
            'business_rules': self.business_rules,
            'domain_vocabulary': self.domain_vocabulary,
            'related_files': self.related_files,
            'related_functions': self.related_functions,
            'related_classes': self.related_classes,
            'complexity_score': self.complexity_score,
            'coverage_percentage': self.coverage_percentage,
            'parent_domain_id': self.parent_domain_id,
            'subdomain_relationships': self.subdomain_relationships,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class BusinessProcess(db.Model):
    """Business process identification and workflow analysis"""
    __tablename__ = 'business_processes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = db.Column(db.String(36), db.ForeignKey('business_analyses.id'), nullable=False)
    domain_id = db.Column(db.String(36), db.ForeignKey('business_domains.id'))
    
    # Process identification
    process_name = db.Column(db.String(200), nullable=False)
    process_type = db.Column(db.String(100))  # e.g., 'workflow', 'transaction', 'batch'
    process_category = db.Column(db.String(100))
    confidence_score = db.Column(db.Float)
    
    # Process characteristics
    process_steps = db.Column(db.JSON, default=list)  # Ordered list of process steps
    decision_points = db.Column(db.JSON, default=list)  # Decision points in the process
    data_flows = db.Column(db.JSON, default=list)  # Data flow through the process
    
    # Process mapping
    entry_points = db.Column(db.JSON, default=list)  # Code entry points for this process
    exit_points = db.Column(db.JSON, default=list)  # Process completion points
    involved_functions = db.Column(db.JSON, default=list)  # Functions involved in process
    involved_classes = db.Column(db.JSON, default=list)  # Classes involved in process
    
    # Process metrics
    complexity_score = db.Column(db.Float)
    estimated_duration = db.Column(db.Float)  # Estimated execution time
    error_handling_score = db.Column(db.Float)  # Quality of error handling
    
    # Process optimization
    bottlenecks = db.Column(db.JSON, default=list)  # Identified bottlenecks
    optimization_opportunities = db.Column(db.JSON, default=list)
    automation_potential = db.Column(db.Float)  # 0-1 score for automation potential
    
    # Process relationships
    parent_process_id = db.Column(db.String(36), db.ForeignKey('business_processes.id'))
    subprocess_relationships = db.Column(db.JSON, default=list)
    process_dependencies = db.Column(db.JSON, default=list)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'domain_id': self.domain_id,
            'process_name': self.process_name,
            'process_type': self.process_type,
            'process_category': self.process_category,
            'confidence_score': self.confidence_score,
            'process_steps': self.process_steps,
            'decision_points': self.decision_points,
            'data_flows': self.data_flows,
            'entry_points': self.entry_points,
            'exit_points': self.exit_points,
            'involved_functions': self.involved_functions,
            'involved_classes': self.involved_classes,
            'complexity_score': self.complexity_score,
            'estimated_duration': self.estimated_duration,
            'error_handling_score': self.error_handling_score,
            'bottlenecks': self.bottlenecks,
            'optimization_opportunities': self.optimization_opportunities,
            'automation_potential': self.automation_potential,
            'parent_process_id': self.parent_process_id,
            'subprocess_relationships': self.subprocess_relationships,
            'process_dependencies': self.process_dependencies,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class KnowledgeGraph(db.Model):
    """Business knowledge graph construction and semantic analysis"""
    __tablename__ = 'knowledge_graphs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = db.Column(db.String(36), db.ForeignKey('business_analyses.id'), nullable=False)
    
    # Graph metadata
    graph_name = db.Column(db.String(200), nullable=False)
    graph_type = db.Column(db.String(100))  # e.g., 'entity', 'concept', 'process', 'rule'
    graph_scope = db.Column(db.String(100))  # e.g., 'domain', 'process', 'global'
    
    # Graph structure
    nodes = db.Column(db.JSON, default=list)  # Graph nodes with properties
    edges = db.Column(db.JSON, default=list)  # Graph edges with relationships
    node_count = db.Column(db.Integer, default=0)
    edge_count = db.Column(db.Integer, default=0)
    
    # Semantic analysis
    concepts = db.Column(db.JSON, default=list)  # Identified concepts
    concept_hierarchy = db.Column(db.JSON, default=dict)  # Hierarchical concept relationships
    semantic_relationships = db.Column(db.JSON, default=list)  # Semantic relationships
    
    # Graph metrics
    density = db.Column(db.Float)  # Graph density
    clustering_coefficient = db.Column(db.Float)
    centrality_measures = db.Column(db.JSON, default=dict)  # Various centrality measures
    
    # Graph analysis
    communities = db.Column(db.JSON, default=list)  # Detected communities/clusters
    key_entities = db.Column(db.JSON, default=list)  # Most important entities
    relationship_patterns = db.Column(db.JSON, default=list)  # Common relationship patterns
    
    # Graph quality
    completeness_score = db.Column(db.Float)  # How complete the graph is
    consistency_score = db.Column(db.Float)  # Internal consistency
    confidence_score = db.Column(db.Float)  # Overall confidence in the graph
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_graph_data=False):
        result = {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'graph_name': self.graph_name,
            'graph_type': self.graph_type,
            'graph_scope': self.graph_scope,
            'node_count': self.node_count,
            'edge_count': self.edge_count,
            'concepts': self.concepts,
            'concept_hierarchy': self.concept_hierarchy,
            'semantic_relationships': self.semantic_relationships,
            'density': self.density,
            'clustering_coefficient': self.clustering_coefficient,
            'centrality_measures': self.centrality_measures,
            'communities': self.communities,
            'key_entities': self.key_entities,
            'relationship_patterns': self.relationship_patterns,
            'completeness_score': self.completeness_score,
            'consistency_score': self.consistency_score,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_graph_data:
            result['nodes'] = self.nodes
            result['edges'] = self.edges
            
        return result

class BusinessEntity(db.Model):
    """Individual business entities identified in the codebase"""
    __tablename__ = 'business_entities'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    domain_id = db.Column(db.String(36), db.ForeignKey('business_domains.id'), nullable=False)
    
    # Entity identification
    entity_name = db.Column(db.String(200), nullable=False)
    entity_type = db.Column(db.String(100))  # e.g., 'customer', 'product', 'order', 'payment'
    entity_category = db.Column(db.String(100))
    confidence_score = db.Column(db.Float)
    
    # Entity characteristics
    attributes = db.Column(db.JSON, default=list)  # Entity attributes/properties
    relationships = db.Column(db.JSON, default=list)  # Relationships to other entities
    business_rules = db.Column(db.JSON, default=list)  # Rules governing this entity
    
    # Code mapping
    source_files = db.Column(db.JSON, default=list)  # Files where entity is defined/used
    source_classes = db.Column(db.JSON, default=list)  # Classes representing this entity
    source_functions = db.Column(db.JSON, default=list)  # Functions operating on this entity
    
    # Entity metrics
    usage_frequency = db.Column(db.Integer, default=0)  # How often entity is referenced
    complexity_score = db.Column(db.Float)
    importance_score = db.Column(db.Float)  # Business importance
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'domain_id': self.domain_id,
            'entity_name': self.entity_name,
            'entity_type': self.entity_type,
            'entity_category': self.entity_category,
            'confidence_score': self.confidence_score,
            'attributes': self.attributes,
            'relationships': self.relationships,
            'business_rules': self.business_rules,
            'source_files': self.source_files,
            'source_classes': self.source_classes,
            'source_functions': self.source_functions,
            'usage_frequency': self.usage_frequency,
            'complexity_score': self.complexity_score,
            'importance_score': self.importance_score,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class BusinessIntelligence(db.Model):
    """Aggregated business intelligence and insights"""
    __tablename__ = 'business_intelligence'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = db.Column(db.String(36), db.ForeignKey('business_analyses.id'), nullable=False)
    
    # Intelligence metadata
    intelligence_type = db.Column(db.String(100))  # e.g., 'domain_summary', 'process_optimization', 'risk_assessment'
    scope = db.Column(db.String(100))  # e.g., 'global', 'domain', 'process'
    confidence_score = db.Column(db.Float)
    
    # Intelligence content
    insights = db.Column(db.JSON, default=list)  # Key insights and findings
    recommendations = db.Column(db.JSON, default=list)  # Actionable recommendations
    risk_factors = db.Column(db.JSON, default=list)  # Identified risks
    opportunities = db.Column(db.JSON, default=list)  # Business opportunities
    
    # Supporting data
    evidence = db.Column(db.JSON, default=list)  # Evidence supporting the intelligence
    metrics = db.Column(db.JSON, default=dict)  # Quantitative metrics
    trends = db.Column(db.JSON, default=list)  # Identified trends
    
    # Impact assessment
    business_impact = db.Column(db.String(50))  # high, medium, low
    technical_impact = db.Column(db.String(50))  # high, medium, low
    implementation_complexity = db.Column(db.String(50))  # high, medium, low
    
    # Stakeholder information
    affected_stakeholders = db.Column(db.JSON, default=list)
    required_expertise = db.Column(db.JSON, default=list)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'intelligence_type': self.intelligence_type,
            'scope': self.scope,
            'confidence_score': self.confidence_score,
            'insights': self.insights,
            'recommendations': self.recommendations,
            'risk_factors': self.risk_factors,
            'opportunities': self.opportunities,
            'evidence': self.evidence,
            'metrics': self.metrics,
            'trends': self.trends,
            'business_impact': self.business_impact,
            'technical_impact': self.technical_impact,
            'implementation_complexity': self.implementation_complexity,
            'affected_stakeholders': self.affected_stakeholders,
            'required_expertise': self.required_expertise,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

