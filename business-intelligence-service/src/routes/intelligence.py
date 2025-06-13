"""
ATE Business Intelligence Service - Intelligence Synthesis Routes
Business intelligence aggregation and insights
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from src.models.user import db, BusinessAnalysis, BusinessIntelligence
from src.utils.auth import require_auth, get_current_user
from src.analyzers.intelligence_synthesizer import IntelligenceSynthesizer

intelligence_bp = Blueprint('intelligence', __name__)

@intelligence_bp.route('/synthesize/<analysis_id>', methods=['POST'])
@require_auth
def synthesize_business_intelligence(analysis_id):
    """Synthesize comprehensive business intelligence from analysis results"""
    try:
        current_user = get_current_user()
        tenant_id = current_user['tenant_id']
        
        # Verify business analysis exists
        business_analysis = BusinessAnalysis.query.filter_by(
            id=analysis_id, tenant_id=tenant_id
        ).first()
        
        if not business_analysis:
            return jsonify({'error': 'Business analysis not found'}), 404
        
        # Get synthesis configuration
        config = request.get_json() or {}
        synthesis_config = {
            'intelligence_types': config.get('intelligence_types', [
                'domain_summary', 'process_optimization', 'risk_assessment', 'opportunity_identification'
            ]),
            'include_stakeholder_analysis': config.get('include_stakeholder_analysis', True),
            'generate_recommendations': config.get('generate_recommendations', True),
            'assess_business_impact': config.get('assess_business_impact', True),
            'confidence_threshold': config.get('confidence_threshold', 0.6)
        }
        
        # Prepare comprehensive data for synthesis
        synthesis_data = {
            'business_analysis': business_analysis.to_dict(include_details=True),
            'domains': [domain.to_dict() for domain in business_analysis.domains],
            'processes': [process.to_dict() for process in business_analysis.processes],
            'knowledge_graphs': [kg.to_dict(include_graph_data=False) for kg in business_analysis.knowledge_graphs]
        }
        
        # Perform intelligence synthesis
        synthesizer = IntelligenceSynthesizer(synthesis_config)
        intelligence_results = synthesizer.synthesize_intelligence(synthesis_data)
        
        # Store intelligence results
        intelligence_records = []
        for intelligence_result in intelligence_results['intelligence']:
            business_intelligence = BusinessIntelligence(
                analysis_id=business_analysis.id,
                intelligence_type=intelligence_result['intelligence_type'],
                scope=intelligence_result.get('scope', 'global'),
                confidence_score=intelligence_result['confidence_score'],
                insights=intelligence_result.get('insights', []),
                recommendations=intelligence_result.get('recommendations', []),
                risk_factors=intelligence_result.get('risk_factors', []),
                opportunities=intelligence_result.get('opportunities', []),
                evidence=intelligence_result.get('evidence', []),
                metrics=intelligence_result.get('metrics', {}),
                trends=intelligence_result.get('trends', []),
                business_impact=intelligence_result.get('business_impact', 'medium'),
                technical_impact=intelligence_result.get('technical_impact', 'medium'),
                implementation_complexity=intelligence_result.get('implementation_complexity', 'medium'),
                affected_stakeholders=intelligence_result.get('affected_stakeholders', []),
                required_expertise=intelligence_result.get('required_expertise', [])
            )
            
            db.session.add(business_intelligence)
            intelligence_records.append(business_intelligence)
        
        # Update business analysis with intelligence summary
        business_analysis.business_summary.update({
            'intelligence_synthesized': True,
            'intelligence_types_generated': len(intelligence_records),
            'high_impact_opportunities': len([i for i in intelligence_records if i.business_impact == 'high']),
            'synthesis_confidence': intelligence_results.get('overall_confidence', 0.0)
        })
        
        db.session.commit()
        
        return jsonify({
            'message': 'Business intelligence synthesis completed',
            'analysis_id': business_analysis.id,
            'intelligence_generated': len(intelligence_records),
            'overall_confidence': intelligence_results.get('overall_confidence', 0.0),
            'summary': intelligence_results.get('summary', {})
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Intelligence synthesis failed: {str(e)}'}), 500

@intelligence_bp.route('/results/<analysis_id>', methods=['GET'])
@require_auth
def get_intelligence_results(analysis_id):
    """Get business intelligence synthesis results"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Verify access
    business_analysis = BusinessAnalysis.query.filter_by(
        id=analysis_id, tenant_id=tenant_id
    ).first()
    
    if not business_analysis:
        return jsonify({'error': 'Business analysis not found'}), 404
    
    intelligence_type = request.args.get('type')
    scope = request.args.get('scope')
    
    # Build query
    query = BusinessIntelligence.query.filter_by(analysis_id=analysis_id)
    if intelligence_type:
        query = query.filter_by(intelligence_type=intelligence_type)
    if scope:
        query = query.filter_by(scope=scope)
    
    intelligence_records = query.all()
    
    return jsonify({
        'business_intelligence': [intel.to_dict() for intel in intelligence_records],
        'summary': {
            'total_intelligence': len(intelligence_records),
            'intelligence_types': list(set(intel.intelligence_type for intel in intelligence_records)),
            'high_impact_items': len([intel for intel in intelligence_records if intel.business_impact == 'high']),
            'recommendations_count': sum(len(intel.recommendations or []) for intel in intelligence_records),
            'opportunities_count': sum(len(intel.opportunities or []) for intel in intelligence_records)
        }
    })

@intelligence_bp.route('/intelligence/<intelligence_id>', methods=['GET'])
@require_auth
def get_intelligence_details(intelligence_id):
    """Get detailed information about specific business intelligence"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Get intelligence and verify access
    business_intelligence = db.session.query(BusinessIntelligence).join(BusinessAnalysis).filter(
        BusinessIntelligence.id == intelligence_id,
        BusinessAnalysis.tenant_id == tenant_id
    ).first()
    
    if not business_intelligence:
        return jsonify({'error': 'Business intelligence not found'}), 404
    
    return jsonify({
        'business_intelligence': business_intelligence.to_dict()
    })

@intelligence_bp.route('/dashboard/<analysis_id>', methods=['GET'])
@require_auth
def get_intelligence_dashboard(analysis_id):
    """Get comprehensive business intelligence dashboard"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Verify access
    business_analysis = BusinessAnalysis.query.filter_by(
        id=analysis_id, tenant_id=tenant_id
    ).first()
    
    if not business_analysis:
        return jsonify({'error': 'Business analysis not found'}), 404
    
    # Get all intelligence
    intelligence_records = BusinessIntelligence.query.filter_by(analysis_id=analysis_id).all()
    
    # Aggregate dashboard data
    dashboard = {
        'overview': {
            'analysis_id': analysis_id,
            'codebase_id': business_analysis.codebase_id,
            'analysis_status': business_analysis.analysis_status,
            'overall_confidence': business_analysis.confidence_score,
            'domains_identified': len(business_analysis.domains),
            'processes_identified': len(business_analysis.processes),
            'knowledge_graphs_created': len(business_analysis.knowledge_graphs),
            'intelligence_items': len(intelligence_records)
        },
        'key_insights': [],
        'top_recommendations': [],
        'high_priority_opportunities': [],
        'risk_factors': [],
        'business_impact_summary': {
            'high': 0,
            'medium': 0,
            'low': 0
        },
        'intelligence_by_type': {}
    }
    
    # Process intelligence records
    for intel in intelligence_records:
        # Aggregate insights
        dashboard['key_insights'].extend(intel.insights or [])
        
        # Aggregate recommendations
        dashboard['top_recommendations'].extend(intel.recommendations or [])
        
        # Aggregate opportunities
        if intel.business_impact == 'high':
            dashboard['high_priority_opportunities'].extend(intel.opportunities or [])
        
        # Aggregate risk factors
        dashboard['risk_factors'].extend(intel.risk_factors or [])
        
        # Count business impact
        if intel.business_impact in dashboard['business_impact_summary']:
            dashboard['business_impact_summary'][intel.business_impact] += 1
        
        # Group by intelligence type
        if intel.intelligence_type not in dashboard['intelligence_by_type']:
            dashboard['intelligence_by_type'][intel.intelligence_type] = []
        dashboard['intelligence_by_type'][intel.intelligence_type].append(intel.to_dict())
    
    # Limit lists for dashboard display
    dashboard['key_insights'] = dashboard['key_insights'][:10]
    dashboard['top_recommendations'] = dashboard['top_recommendations'][:10]
    dashboard['high_priority_opportunities'] = dashboard['high_priority_opportunities'][:10]
    dashboard['risk_factors'] = dashboard['risk_factors'][:10]
    
    return jsonify({
        'dashboard': dashboard
    })

@intelligence_bp.route('/export/<analysis_id>', methods=['GET'])
@require_auth
def export_intelligence_report(analysis_id):
    """Export comprehensive business intelligence report"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Verify access
    business_analysis = BusinessAnalysis.query.filter_by(
        id=analysis_id, tenant_id=tenant_id
    ).first()
    
    if not business_analysis:
        return jsonify({'error': 'Business analysis not found'}), 404
    
    # Generate comprehensive report
    report = {
        'report_metadata': {
            'generated_at': datetime.utcnow().isoformat(),
            'analysis_id': analysis_id,
            'codebase_id': business_analysis.codebase_id,
            'tenant_id': tenant_id,
            'report_version': '1.0'
        },
        'executive_summary': business_analysis.business_summary,
        'business_analysis': business_analysis.to_dict(include_details=True),
        'business_intelligence': [intel.to_dict() for intel in BusinessIntelligence.query.filter_by(analysis_id=analysis_id).all()],
        'recommendations_summary': {
            'total_recommendations': 0,
            'high_priority': 0,
            'medium_priority': 0,
            'low_priority': 0
        },
        'implementation_roadmap': {
            'immediate_actions': [],
            'short_term_goals': [],
            'long_term_objectives': []
        }
    }
    
    # Process recommendations for summary
    for intel in BusinessIntelligence.query.filter_by(analysis_id=analysis_id).all():
        report['recommendations_summary']['total_recommendations'] += len(intel.recommendations or [])
        
        if intel.business_impact == 'high':
            report['recommendations_summary']['high_priority'] += len(intel.recommendations or [])
            report['implementation_roadmap']['immediate_actions'].extend(intel.recommendations or [])
        elif intel.business_impact == 'medium':
            report['recommendations_summary']['medium_priority'] += len(intel.recommendations or [])
            report['implementation_roadmap']['short_term_goals'].extend(intel.recommendations or [])
        else:
            report['recommendations_summary']['low_priority'] += len(intel.recommendations or [])
            report['implementation_roadmap']['long_term_objectives'].extend(intel.recommendations or [])
    
    return jsonify({
        'intelligence_report': report
    })

