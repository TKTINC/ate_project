"""
ATE Analysis Service - Multi-Language Code Parsing Models
Database models for storing analysis results and metadata
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import json

db = SQLAlchemy()

class ParsedCodebase(db.Model):
    """Parsed codebase with analysis metadata"""
    __tablename__ = 'parsed_codebases'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), nullable=False, index=True)  # Reference to storage service
    tenant_id = db.Column(db.String(36), nullable=False, index=True)
    
    # Parsing metadata
    parsing_status = db.Column(db.String(50), default='pending')  # pending, parsing, completed, failed
    parsing_started_at = db.Column(db.DateTime, default=datetime.utcnow)
    parsing_completed_at = db.Column(db.DateTime)
    parsing_duration_seconds = db.Column(db.Float)
    
    # Codebase statistics
    total_files = db.Column(db.Integer, default=0)
    parsed_files = db.Column(db.Integer, default=0)
    failed_files = db.Column(db.Integer, default=0)
    total_lines_of_code = db.Column(db.Integer, default=0)
    
    # Language distribution
    language_distribution = db.Column(db.JSON, default=dict)  # {language: file_count}
    
    # Parsing configuration
    parsing_config = db.Column(db.JSON, default=dict)
    
    # Error information
    parsing_errors = db.Column(db.JSON, default=list)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parsed_files = db.relationship('ParsedFile', backref='codebase', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_files=False):
        result = {
            'id': self.id,
            'project_id': self.project_id,
            'tenant_id': self.tenant_id,
            'parsing_status': self.parsing_status,
            'parsing_started_at': self.parsing_started_at.isoformat(),
            'parsing_completed_at': self.parsing_completed_at.isoformat() if self.parsing_completed_at else None,
            'parsing_duration_seconds': self.parsing_duration_seconds,
            'total_files': self.total_files,
            'parsed_files': self.parsed_files,
            'failed_files': self.failed_files,
            'total_lines_of_code': self.total_lines_of_code,
            'language_distribution': self.language_distribution,
            'parsing_config': self.parsing_config,
            'parsing_errors': self.parsing_errors,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_files:
            result['files'] = [file.to_dict() for file in self.parsed_files]
            
        return result

class ParsedFile(db.Model):
    """Individual parsed file with AST and semantic information"""
    __tablename__ = 'parsed_files'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    codebase_id = db.Column(db.String(36), db.ForeignKey('parsed_codebases.id'), nullable=False)
    file_id = db.Column(db.String(36), nullable=False)  # Reference to storage service file
    
    # File metadata
    file_path = db.Column(db.String(1000), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    file_size_bytes = db.Column(db.BigInteger)
    line_count = db.Column(db.Integer)
    
    # Parsing results
    parsing_status = db.Column(db.String(50), default='pending')  # pending, completed, failed
    parsing_duration_ms = db.Column(db.Float)
    
    # AST and semantic analysis
    ast_data = db.Column(db.JSON)  # Serialized AST
    semantic_data = db.Column(db.JSON)  # Semantic analysis results
    
    # Code structure
    functions = db.Column(db.JSON, default=list)  # Function definitions
    classes = db.Column(db.JSON, default=list)  # Class definitions
    imports = db.Column(db.JSON, default=list)  # Import statements
    exports = db.Column(db.JSON, default=list)  # Export statements
    variables = db.Column(db.JSON, default=list)  # Variable definitions
    
    # Code metrics
    complexity_metrics = db.Column(db.JSON, default=dict)
    quality_metrics = db.Column(db.JSON, default=dict)
    
    # Error information
    parsing_errors = db.Column(db.JSON, default=list)
    syntax_errors = db.Column(db.JSON, default=list)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_ast=False):
        result = {
            'id': self.id,
            'codebase_id': self.codebase_id,
            'file_id': self.file_id,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'language': self.language,
            'file_size_bytes': self.file_size_bytes,
            'line_count': self.line_count,
            'parsing_status': self.parsing_status,
            'parsing_duration_ms': self.parsing_duration_ms,
            'functions': self.functions,
            'classes': self.classes,
            'imports': self.imports,
            'exports': self.exports,
            'variables': self.variables,
            'complexity_metrics': self.complexity_metrics,
            'quality_metrics': self.quality_metrics,
            'parsing_errors': self.parsing_errors,
            'syntax_errors': self.syntax_errors,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_ast:
            result['ast_data'] = self.ast_data
            result['semantic_data'] = self.semantic_data
            
        return result

class DependencyGraph(db.Model):
    """Dependency relationships between files and modules"""
    __tablename__ = 'dependency_graphs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    codebase_id = db.Column(db.String(36), db.ForeignKey('parsed_codebases.id'), nullable=False)
    
    # Graph metadata
    graph_type = db.Column(db.String(50), nullable=False)  # import, call, data_flow
    graph_data = db.Column(db.JSON, nullable=False)  # Serialized graph structure
    
    # Graph statistics
    node_count = db.Column(db.Integer, default=0)
    edge_count = db.Column(db.Integer, default=0)
    strongly_connected_components = db.Column(db.Integer, default=0)
    cyclic_dependencies = db.Column(db.JSON, default=list)
    
    # Analysis results
    modularity_score = db.Column(db.Float)
    coupling_metrics = db.Column(db.JSON, default=dict)
    cohesion_metrics = db.Column(db.JSON, default=dict)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_graph_data=False):
        result = {
            'id': self.id,
            'codebase_id': self.codebase_id,
            'graph_type': self.graph_type,
            'node_count': self.node_count,
            'edge_count': self.edge_count,
            'strongly_connected_components': self.strongly_connected_components,
            'cyclic_dependencies': self.cyclic_dependencies,
            'modularity_score': self.modularity_score,
            'coupling_metrics': self.coupling_metrics,
            'cohesion_metrics': self.cohesion_metrics,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_graph_data:
            result['graph_data'] = self.graph_data
            
        return result

class CodeQualityAssessment(db.Model):
    """Code quality assessment results"""
    __tablename__ = 'code_quality_assessments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    codebase_id = db.Column(db.String(36), db.ForeignKey('parsed_codebases.id'), nullable=False)
    
    # Overall quality metrics
    overall_quality_score = db.Column(db.Float)  # 0-100 scale
    maintainability_index = db.Column(db.Float)
    technical_debt_ratio = db.Column(db.Float)
    
    # Complexity metrics
    average_cyclomatic_complexity = db.Column(db.Float)
    average_cognitive_complexity = db.Column(db.Float)
    max_complexity_score = db.Column(db.Float)
    high_complexity_functions = db.Column(db.JSON, default=list)
    
    # Code smells
    code_smells = db.Column(db.JSON, default=list)
    smell_categories = db.Column(db.JSON, default=dict)  # {category: count}
    
    # Duplication analysis
    duplicate_code_percentage = db.Column(db.Float)
    duplicate_blocks = db.Column(db.JSON, default=list)
    
    # Test coverage (if available)
    test_coverage_percentage = db.Column(db.Float)
    untested_functions = db.Column(db.JSON, default=list)
    
    # Security analysis
    security_issues = db.Column(db.JSON, default=list)
    security_score = db.Column(db.Float)
    
    # Performance analysis
    performance_issues = db.Column(db.JSON, default=list)
    performance_score = db.Column(db.Float)
    
    # Recommendations
    improvement_recommendations = db.Column(db.JSON, default=list)
    priority_issues = db.Column(db.JSON, default=list)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'codebase_id': self.codebase_id,
            'overall_quality_score': self.overall_quality_score,
            'maintainability_index': self.maintainability_index,
            'technical_debt_ratio': self.technical_debt_ratio,
            'average_cyclomatic_complexity': self.average_cyclomatic_complexity,
            'average_cognitive_complexity': self.average_cognitive_complexity,
            'max_complexity_score': self.max_complexity_score,
            'high_complexity_functions': self.high_complexity_functions,
            'code_smells': self.code_smells,
            'smell_categories': self.smell_categories,
            'duplicate_code_percentage': self.duplicate_code_percentage,
            'duplicate_blocks': self.duplicate_blocks,
            'test_coverage_percentage': self.test_coverage_percentage,
            'untested_functions': self.untested_functions,
            'security_issues': self.security_issues,
            'security_score': self.security_score,
            'performance_issues': self.performance_issues,
            'performance_score': self.performance_score,
            'improvement_recommendations': self.improvement_recommendations,
            'priority_issues': self.priority_issues,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ArchitecturalAnalysis(db.Model):
    """Architectural pattern recognition and design analysis"""
    __tablename__ = 'architectural_analyses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    codebase_id = db.Column(db.String(36), db.ForeignKey('parsed_codebases.id'), nullable=False)
    
    # Architectural patterns
    detected_patterns = db.Column(db.JSON, default=list)  # List of detected design patterns
    architectural_style = db.Column(db.String(100))  # MVC, MVP, MVVM, Layered, etc.
    architecture_confidence = db.Column(db.Float)  # Confidence in pattern detection
    
    # Component analysis
    components = db.Column(db.JSON, default=list)  # Identified components/modules
    component_relationships = db.Column(db.JSON, default=list)  # Component interactions
    layering_analysis = db.Column(db.JSON, default=dict)  # Layer identification and violations
    
    # Modularity metrics
    modularity_score = db.Column(db.Float)
    coupling_score = db.Column(db.Float)
    cohesion_score = db.Column(db.Float)
    
    # Architecture quality
    architecture_quality_score = db.Column(db.Float)
    design_principle_violations = db.Column(db.JSON, default=list)
    architecture_smells = db.Column(db.JSON, default=list)
    
    # Scalability analysis
    scalability_assessment = db.Column(db.JSON, default=dict)
    bottleneck_analysis = db.Column(db.JSON, default=list)
    
    # Recommendations
    architecture_recommendations = db.Column(db.JSON, default=list)
    refactoring_suggestions = db.Column(db.JSON, default=list)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'codebase_id': self.codebase_id,
            'detected_patterns': self.detected_patterns,
            'architectural_style': self.architectural_style,
            'architecture_confidence': self.architecture_confidence,
            'components': self.components,
            'component_relationships': self.component_relationships,
            'layering_analysis': self.layering_analysis,
            'modularity_score': self.modularity_score,
            'coupling_score': self.coupling_score,
            'cohesion_score': self.cohesion_score,
            'architecture_quality_score': self.architecture_quality_score,
            'design_principle_violations': self.design_principle_violations,
            'architecture_smells': self.architecture_smells,
            'scalability_assessment': self.scalability_assessment,
            'bottleneck_analysis': self.bottleneck_analysis,
            'architecture_recommendations': self.architecture_recommendations,
            'refactoring_suggestions': self.refactoring_suggestions,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

