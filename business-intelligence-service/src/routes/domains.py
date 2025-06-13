"""
ATE Business Intelligence Service - Domain Classification Routes
Business domain mapping and classification
"""

import time
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from src.models.user import db, BusinessAnalysis, BusinessDomain, BusinessEntity
from src.utils.auth import require_auth, get_current_user
from src.utils.analysis_client import AnalysisClient
from src.analyzers.domain_classifier import DomainClassifier

domains_bp = Blueprint('domains', __name__)

@domains_bp.route('/analyze/<codebase_id>', methods=['POST'])
@require_auth
def analyze_business_domains(codebase_id):
    """Analyze and classify business domains in a codebase"""
    try:
        current_user = get_current_user()
        tenant_id = current_user['tenant_id']
        
        # Get analysis configuration
        config = request.get_json() or {}
        analysis_config = {
            'confidence_threshold': config.get('confidence_threshold', 
                current_app.config['DOMAIN_CLASSIFICATION_CONFIDENCE_THRESHOLD']),
            'include_subdomains': config.get('include_subdomains', True),
            'extract_entities': config.get('extract_entities', True),
            'identify_business_rules': config.get('identify_business_rules', True),
            'domain_categories': config.get('domain_categories', [])  # Empty means all categories
        }
        
        # Check if analysis already exists
        existing_analysis = BusinessAnalysis.query.filter_by(
            codebase_id=codebase_id,
            tenant_id=tenant_id
        ).first()
        
        if existing_analysis and existing_analysis.analysis_status == 'analyzing':
            return jsonify({
                'error': 'Business analysis already in progress',
                'existing_analysis_id': existing_analysis.id
            }), 409
        
        # Get parsed codebase data from analysis service
        analysis_client = AnalysisClient(current_app.config['ANALYSIS_SERVICE_URL'])
        codebase_data = analysis_client.get_parsing_results(codebase_id, current_user)
        
        if not codebase_data:
            return jsonify({'error': 'Codebase analysis not found or access denied'}), 404
        
        # Create or update business analysis record
        if existing_analysis:
            business_analysis = existing_analysis
            business_analysis.analysis_status = 'analyzing'
            business_analysis.analysis_started_at = datetime.utcnow()
            business_analysis.analysis_config = analysis_config
        else:
            business_analysis = BusinessAnalysis(
                codebase_id=codebase_id,
                tenant_id=tenant_id,
                analysis_status='analyzing',
                analysis_config=analysis_config
            )
            db.session.add(business_analysis)
        
        db.session.commit()
        
        # Perform domain classification
        domain_classifier = DomainClassifier(analysis_config)
        classification_results = domain_classifier.classify_domains(codebase_data)
        
        # Store domain classification results
        domains_created = []
        for domain_result in classification_results['domains']:
            business_domain = BusinessDomain(
                analysis_id=business_analysis.id,
                domain_name=domain_result['domain_name'],
                domain_category=domain_result['domain_category'],
                domain_subcategory=domain_result.get('domain_subcategory'),
                confidence_score=domain_result['confidence_score'],
                business_entities=domain_result.get('business_entities', []),
                business_rules=domain_result.get('business_rules', []),
                domain_vocabulary=domain_result.get('domain_vocabulary', []),
                related_files=domain_result.get('related_files', []),
                related_functions=domain_result.get('related_functions', []),
                related_classes=domain_result.get('related_classes', []),
                complexity_score=domain_result.get('complexity_score', 0.0),
                coverage_percentage=domain_result.get('coverage_percentage', 0.0)
            )
            
            db.session.add(business_domain)
            domains_created.append(business_domain)
        
        # Store business entities if requested
        entities_created = []
        if analysis_config['extract_entities']:
            for entity_result in classification_results.get('entities', []):
                # Find the domain this entity belongs to
                domain_id = None
                for domain in domains_created:
                    if entity_result.get('domain_name') == domain.domain_name:
                        domain_id = domain.id
                        break
                
                if domain_id:
                    business_entity = BusinessEntity(
                        domain_id=domain_id,
                        entity_name=entity_result['entity_name'],
                        entity_type=entity_result.get('entity_type'),
                        entity_category=entity_result.get('entity_category'),
                        confidence_score=entity_result['confidence_score'],
                        attributes=entity_result.get('attributes', []),
                        relationships=entity_result.get('relationships', []),
                        business_rules=entity_result.get('business_rules', []),
                        source_files=entity_result.get('source_files', []),
                        source_classes=entity_result.get('source_classes', []),
                        source_functions=entity_result.get('source_functions', []),
                        usage_frequency=entity_result.get('usage_frequency', 0),
                        complexity_score=entity_result.get('complexity_score', 0.0),
                        importance_score=entity_result.get('importance_score', 0.0)
                    )
                    
                    db.session.add(business_entity)
                    entities_created.append(business_entity)
        
        # Update business analysis with results
        business_analysis.analysis_status = 'completed'
        business_analysis.analysis_completed_at = datetime.utcnow()
        business_analysis.analysis_duration_seconds = (
            business_analysis.analysis_completed_at - business_analysis.analysis_started_at
        ).total_seconds()
        business_analysis.business_summary = classification_results.get('summary', {})
        business_analysis.confidence_score = classification_results.get('overall_confidence', 0.0)
        business_analysis.analysis_errors = classification_results.get('errors', [])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Business domain analysis completed',
            'analysis_id': business_analysis.id,
            'domains_identified': len(domains_created),
            'entities_extracted': len(entities_created),
            'overall_confidence': classification_results.get('overall_confidence', 0.0),
            'summary': classification_results.get('summary', {})
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Domain analysis failed: {str(e)}'}), 500

@domains_bp.route('/results/<analysis_id>', methods=['GET'])
@require_auth
def get_domain_analysis_results(analysis_id):
    """Get business domain analysis results"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    business_analysis = BusinessAnalysis.query.filter_by(
        id=analysis_id, tenant_id=tenant_id
    ).first()
    
    if not business_analysis:
        return jsonify({'error': 'Business analysis not found'}), 404
    
    include_entities = request.args.get('include_entities', 'false').lower() == 'true'
    
    result = business_analysis.to_dict(include_details=True)
    
    if include_entities:
        # Add detailed entity information
        for domain in result['domains']:
            domain_entities = BusinessEntity.query.filter_by(domain_id=domain['id']).all()
            domain['entities'] = [entity.to_dict() for entity in domain_entities]
    
    return jsonify({
        'business_analysis': result
    })

@domains_bp.route('/domain/<domain_id>', methods=['GET'])
@require_auth
def get_domain_details(domain_id):
    """Get detailed information about a specific business domain"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Get domain and verify access through business analysis
    business_domain = db.session.query(BusinessDomain).join(BusinessAnalysis).filter(
        BusinessDomain.id == domain_id,
        BusinessAnalysis.tenant_id == tenant_id
    ).first()
    
    if not business_domain:
        return jsonify({'error': 'Business domain not found'}), 404
    
    # Get entities in this domain
    domain_entities = BusinessEntity.query.filter_by(domain_id=domain_id).all()
    
    domain_data = business_domain.to_dict()
    domain_data['entities'] = [entity.to_dict() for entity in domain_entities]
    
    return jsonify({
        'domain': domain_data
    })

@domains_bp.route('/entity/<entity_id>', methods=['GET'])
@require_auth
def get_entity_details(entity_id):
    """Get detailed information about a specific business entity"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Get entity and verify access through domain and business analysis
    business_entity = db.session.query(BusinessEntity).join(BusinessDomain).join(BusinessAnalysis).filter(
        BusinessEntity.id == entity_id,
        BusinessAnalysis.tenant_id == tenant_id
    ).first()
    
    if not business_entity:
        return jsonify({'error': 'Business entity not found'}), 404
    
    return jsonify({
        'entity': business_entity.to_dict()
    })

@domains_bp.route('/categories', methods=['GET'])
def get_domain_categories():
    """Get list of supported business domain categories"""
    return jsonify({
        'domain_categories': [
            {
                'category': 'finance',
                'subcategories': ['banking', 'insurance', 'investment', 'accounting', 'payments'],
                'description': 'Financial services and money management'
            },
            {
                'category': 'healthcare',
                'subcategories': ['patient_management', 'medical_records', 'billing', 'pharmacy', 'diagnostics'],
                'description': 'Healthcare and medical services'
            },
            {
                'category': 'ecommerce',
                'subcategories': ['catalog', 'shopping_cart', 'payments', 'shipping', 'customer_service'],
                'description': 'Online retail and commerce'
            },
            {
                'category': 'manufacturing',
                'subcategories': ['production', 'quality_control', 'supply_chain', 'inventory', 'maintenance'],
                'description': 'Manufacturing and production'
            },
            {
                'category': 'education',
                'subcategories': ['student_management', 'curriculum', 'grading', 'scheduling', 'library'],
                'description': 'Educational institutions and learning'
            },
            {
                'category': 'logistics',
                'subcategories': ['shipping', 'warehousing', 'tracking', 'routing', 'fleet_management'],
                'description': 'Transportation and logistics'
            },
            {
                'category': 'hr',
                'subcategories': ['recruitment', 'payroll', 'benefits', 'performance', 'training'],
                'description': 'Human resources management'
            },
            {
                'category': 'crm',
                'subcategories': ['lead_management', 'sales', 'customer_service', 'marketing', 'analytics'],
                'description': 'Customer relationship management'
            },
            {
                'category': 'inventory',
                'subcategories': ['stock_management', 'procurement', 'suppliers', 'warehousing', 'forecasting'],
                'description': 'Inventory and supply management'
            }
        ]
    })

