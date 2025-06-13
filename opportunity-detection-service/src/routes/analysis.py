"""
ATE Opportunity Detection Service - Analysis Routes
Comprehensive analysis orchestration and management
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import uuid

from src.models.user import db, OpportunityAnalysis
from src.utils.auth import require_auth, get_current_user
from src.utils.business_intelligence_client import BusinessIntelligenceClient
from src.analyzers.opportunity_detector import OpportunityDetector
from src.analyzers.business_case_generator import BusinessCaseGenerator

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/comprehensive/<business_analysis_id>', methods=['POST'])
@require_auth
def run_comprehensive_analysis(business_analysis_id):
    """Run comprehensive opportunity detection and business case generation"""
    try:
        current_user = get_current_user()
        tenant_id = current_user['tenant_id']
        
        # Get analysis configuration
        config = request.get_json() or {}
        analysis_config = {
            'opportunity_detection': config.get('opportunity_detection', {}),
            'business_case_generation': config.get('business_case_generation', {}),
            'auto_generate_business_cases': config.get('auto_generate_business_cases', True),
            'min_opportunity_score_for_business_case': config.get('min_opportunity_score_for_business_case', 70)
        }
        
        # Get business intelligence data
        bi_client = BusinessIntelligenceClient(current_app.config['BUSINESS_INTELLIGENCE_SERVICE_URL'])
        business_data = bi_client.get_comprehensive_analysis(business_analysis_id, current_user)
        
        if not business_data:
            return jsonify({'error': 'Business analysis not found'}), 404
        
        # Create comprehensive analysis record
        analysis_id = str(uuid.uuid4())
        opportunity_analysis = OpportunityAnalysis(
            id=analysis_id,
            tenant_id=tenant_id,
            codebase_id=business_data.get('codebase_id'),
            business_analysis_id=business_analysis_id,
            analysis_name=f"Comprehensive Analysis - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            analysis_status='processing',
            analysis_config=analysis_config
        )
        
        db.session.add(opportunity_analysis)
        db.session.commit()
        
        # Phase 1: Opportunity Detection
        detector = OpportunityDetector(analysis_config.get('opportunity_detection', {}))
        detection_results = detector.detect_opportunities(business_data)
        
        # Store opportunities (simplified for comprehensive analysis)
        opportunities_created = []
        for opportunity_result in detection_results['opportunities']:
            opportunity_id = str(uuid.uuid4())
            # Create opportunity record (implementation similar to opportunities route)
            opportunities_created.append({
                'id': opportunity_id,
                'data': opportunity_result
            })
        
        # Phase 2: Business Case Generation (if enabled)
        business_cases_created = []
        if analysis_config.get('auto_generate_business_cases', True):
            generator = BusinessCaseGenerator(analysis_config.get('business_case_generation', {}))
            min_score = analysis_config.get('min_opportunity_score_for_business_case', 70)
            
            for opp in opportunities_created:
                if opp['data'].get('opportunity_score', 0) >= min_score:
                    # Generate business case (simplified)
                    business_case_data = generator.generate_business_case_from_data(opp['data'], current_user)
                    business_cases_created.append({
                        'opportunity_id': opp['id'],
                        'business_case': business_case_data
                    })
        
        # Update analysis summary
        opportunity_analysis.analysis_status = 'completed'
        opportunity_analysis.completed_at = datetime.utcnow()
        opportunity_analysis.total_opportunities = len(opportunities_created)
        opportunity_analysis.analysis_summary = {
            'comprehensive_analysis': True,
            'opportunities_detected': len(opportunities_created),
            'business_cases_generated': len(business_cases_created),
            'detection_summary': detection_results.get('summary', {}),
            'high_value_opportunities': len([opp for opp in opportunities_created if opp['data'].get('opportunity_score', 0) > 80])
        }
        
        db.session.commit()
        
        return jsonify({
            'message': 'Comprehensive analysis completed successfully',
            'analysis_id': analysis_id,
            'opportunities_detected': len(opportunities_created),
            'business_cases_generated': len(business_cases_created),
            'summary': opportunity_analysis.analysis_summary
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Comprehensive analysis failed: {str(e)}'}), 500

@analysis_bp.route('/status/<analysis_id>', methods=['GET'])
@require_auth
def get_analysis_status(analysis_id):
    """Get analysis status and progress"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    opportunity_analysis = OpportunityAnalysis.query.filter_by(
        id=analysis_id, tenant_id=tenant_id
    ).first()
    
    if not opportunity_analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    return jsonify({
        'analysis_id': analysis_id,
        'status': opportunity_analysis.analysis_status,
        'progress': {
            'created_at': opportunity_analysis.created_at.isoformat() if opportunity_analysis.created_at else None,
            'updated_at': opportunity_analysis.updated_at.isoformat() if opportunity_analysis.updated_at else None,
            'completed_at': opportunity_analysis.completed_at.isoformat() if opportunity_analysis.completed_at else None,
            'total_opportunities': opportunity_analysis.total_opportunities,
            'high_value_opportunities': opportunity_analysis.high_value_opportunities
        },
        'summary': opportunity_analysis.analysis_summary
    })

@analysis_bp.route('/list', methods=['GET'])
@require_auth
def list_analyses():
    """List all analyses for the current tenant"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Get filter parameters
    status = request.args.get('status')
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Build query
    query = OpportunityAnalysis.query.filter_by(tenant_id=tenant_id)
    
    if status:
        query = query.filter_by(analysis_status=status)
    
    # Apply pagination
    query = query.order_by(OpportunityAnalysis.created_at.desc())
    total_count = query.count()
    analyses = query.offset(offset).limit(limit).all()
    
    return jsonify({
        'analyses': [analysis.to_dict() for analysis in analyses],
        'pagination': {
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total_count
        }
    })

@analysis_bp.route('/summary', methods=['GET'])
@require_auth
def get_tenant_summary():
    """Get summary of all analyses for the tenant"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    analyses = OpportunityAnalysis.query.filter_by(tenant_id=tenant_id).all()
    
    summary = {
        'total_analyses': len(analyses),
        'completed_analyses': len([a for a in analyses if a.analysis_status == 'completed']),
        'total_opportunities': sum(a.total_opportunities or 0 for a in analyses),
        'total_estimated_value': sum(a.total_estimated_value or 0 for a in analyses),
        'average_roi': sum(a.average_roi or 0 for a in analyses) / len(analyses) if analyses else 0,
        'recent_analyses': [
            {
                'id': a.id,
                'name': a.analysis_name,
                'status': a.analysis_status,
                'created_at': a.created_at.isoformat() if a.created_at else None,
                'opportunities': a.total_opportunities
            }
            for a in sorted(analyses, key=lambda x: x.created_at or datetime.min, reverse=True)[:5]
        ]
    }
    
    return jsonify({
        'summary': summary
    })

