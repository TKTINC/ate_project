"""
ATE Opportunity Detection Service - Opportunity Detection Routes
AI-powered opportunity identification and scoring
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import uuid

from src.models.user import db, OpportunityAnalysis, TransformationOpportunity
from src.utils.auth import require_auth, get_current_user
from src.utils.business_intelligence_client import BusinessIntelligenceClient
from src.analyzers.opportunity_detector import OpportunityDetector

opportunities_bp = Blueprint('opportunities', __name__)

@opportunities_bp.route('/detect/<business_analysis_id>', methods=['POST'])
@require_auth
def detect_opportunities(business_analysis_id):
    """Detect transformation opportunities from business analysis"""
    try:
        current_user = get_current_user()
        tenant_id = current_user['tenant_id']
        
        # Get detection configuration
        config = request.get_json() or {}
        detection_config = {
            'opportunity_types': config.get('opportunity_types', [
                'automation', 'modernization', 'optimization', 'integration'
            ]),
            'confidence_threshold': config.get('confidence_threshold', 
                current_app.config['OPPORTUNITY_DETECTION_CONFIDENCE_THRESHOLD']),
            'max_opportunities': config.get('max_opportunities',
                current_app.config['MAX_OPPORTUNITIES_PER_ANALYSIS']),
            'include_financial_analysis': config.get('include_financial_analysis', True),
            'include_risk_assessment': config.get('include_risk_assessment', True),
            'scope_filter': config.get('scope_filter', [])  # Empty means all scopes
        }
        
        # Get business intelligence data
        bi_client = BusinessIntelligenceClient(current_app.config['BUSINESS_INTELLIGENCE_SERVICE_URL'])
        business_data = bi_client.get_comprehensive_analysis(business_analysis_id, current_user)
        
        if not business_data:
            return jsonify({'error': 'Business analysis not found'}), 404
        
        # Create opportunity analysis record
        analysis_id = str(uuid.uuid4())
        opportunity_analysis = OpportunityAnalysis(
            id=analysis_id,
            tenant_id=tenant_id,
            codebase_id=business_data.get('codebase_id'),
            business_analysis_id=business_analysis_id,
            analysis_name=f"Opportunity Analysis - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            analysis_status='processing',
            analysis_config=detection_config
        )
        
        db.session.add(opportunity_analysis)
        db.session.commit()
        
        # Perform opportunity detection
        detector = OpportunityDetector(detection_config)
        detection_results = detector.detect_opportunities(business_data)
        
        # Store detected opportunities
        opportunities_created = []
        total_estimated_value = 0.0
        high_value_count = 0
        roi_values = []
        
        for opportunity_result in detection_results['opportunities']:
            opportunity_id = str(uuid.uuid4())
            
            # Calculate financial metrics
            estimated_annual_value = opportunity_result.get('estimated_annual_value', 0.0)
            estimated_cost = opportunity_result.get('estimated_cost', 0.0)
            estimated_roi = ((estimated_annual_value - estimated_cost) / max(estimated_cost, 1)) * 100 if estimated_cost > 0 else 0
            
            transformation_opportunity = TransformationOpportunity(
                id=opportunity_id,
                analysis_id=analysis_id,
                opportunity_name=opportunity_result['opportunity_name'],
                opportunity_type=opportunity_result['opportunity_type'],
                opportunity_category=opportunity_result.get('opportunity_category', 'process'),
                opportunity_scope=opportunity_result.get('opportunity_scope', 'component'),
                source_domain=opportunity_result.get('source_domain'),
                source_processes=opportunity_result.get('source_processes', []),
                source_components=opportunity_result.get('source_components', []),
                affected_stakeholders=opportunity_result.get('affected_stakeholders', []),
                opportunity_score=opportunity_result['opportunity_score'],
                confidence_score=opportunity_result['confidence_score'],
                priority_score=opportunity_result.get('priority_score', 0.0),
                estimated_annual_value=estimated_annual_value,
                estimated_cost_savings=opportunity_result.get('estimated_cost_savings', 0.0),
                estimated_revenue_impact=opportunity_result.get('estimated_revenue_impact', 0.0),
                estimated_efficiency_gain=opportunity_result.get('estimated_efficiency_gain', 0.0),
                implementation_complexity=opportunity_result.get('implementation_complexity', 'medium'),
                estimated_effort_months=opportunity_result.get('estimated_effort_months', 0.0),
                estimated_cost=estimated_cost,
                required_skills=opportunity_result.get('required_skills', []),
                implementation_risk=opportunity_result.get('implementation_risk', 'medium'),
                business_risk=opportunity_result.get('business_risk', 'medium'),
                technical_risk=opportunity_result.get('technical_risk', 'medium'),
                risk_factors=opportunity_result.get('risk_factors', []),
                mitigation_strategies=opportunity_result.get('mitigation_strategies', []),
                estimated_roi=estimated_roi,
                payback_period_months=opportunity_result.get('payback_period_months', 0.0),
                npv=opportunity_result.get('npv', 0.0),
                irr=opportunity_result.get('irr', 0.0),
                opportunity_description=opportunity_result.get('opportunity_description'),
                current_state_analysis=opportunity_result.get('current_state_analysis', {}),
                proposed_solution=opportunity_result.get('proposed_solution', {}),
                implementation_approach=opportunity_result.get('implementation_approach', {}),
                success_metrics=opportunity_result.get('success_metrics', []),
                dependencies=opportunity_result.get('dependencies', []),
                prerequisites=opportunity_result.get('prerequisites', []),
                estimated_timeline=opportunity_result.get('estimated_timeline', {}),
                key_milestones=opportunity_result.get('key_milestones', [])
            )
            
            db.session.add(transformation_opportunity)
            opportunities_created.append(transformation_opportunity)
            
            # Aggregate metrics
            total_estimated_value += estimated_annual_value
            if estimated_annual_value > 100000:  # High value threshold
                high_value_count += 1
            if estimated_roi > 0:
                roi_values.append(estimated_roi)
        
        # Update opportunity analysis summary
        average_roi = sum(roi_values) / len(roi_values) if roi_values else 0.0
        
        opportunity_analysis.analysis_status = 'completed'
        opportunity_analysis.completed_at = datetime.utcnow()
        opportunity_analysis.total_opportunities = len(opportunities_created)
        opportunity_analysis.high_value_opportunities = high_value_count
        opportunity_analysis.total_estimated_value = total_estimated_value
        opportunity_analysis.average_roi = average_roi
        opportunity_analysis.confidence_score = detection_results.get('overall_confidence', 0.0)
        opportunity_analysis.analysis_summary = {
            'detection_summary': detection_results.get('summary', {}),
            'opportunity_types_found': list(set(opp.opportunity_type for opp in opportunities_created)),
            'total_estimated_annual_value': total_estimated_value,
            'average_opportunity_score': sum(opp.opportunity_score for opp in opportunities_created) / len(opportunities_created) if opportunities_created else 0,
            'high_priority_opportunities': len([opp for opp in opportunities_created if opp.priority_score > 80])
        }
        
        db.session.commit()
        
        return jsonify({
            'message': 'Opportunity detection completed successfully',
            'analysis_id': analysis_id,
            'opportunities_detected': len(opportunities_created),
            'high_value_opportunities': high_value_count,
            'total_estimated_value': total_estimated_value,
            'average_roi': average_roi,
            'overall_confidence': detection_results.get('overall_confidence', 0.0),
            'summary': detection_results.get('summary', {})
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Opportunity detection failed: {str(e)}'}), 500

@opportunities_bp.route('/analysis/<analysis_id>', methods=['GET'])
@require_auth
def get_opportunity_analysis(analysis_id):
    """Get opportunity analysis results"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    opportunity_analysis = OpportunityAnalysis.query.filter_by(
        id=analysis_id, tenant_id=tenant_id
    ).first()
    
    if not opportunity_analysis:
        return jsonify({'error': 'Opportunity analysis not found'}), 404
    
    include_details = request.args.get('include_details', 'false').lower() == 'true'
    
    return jsonify({
        'opportunity_analysis': opportunity_analysis.to_dict(include_details=include_details)
    })

@opportunities_bp.route('/analysis/<analysis_id>/opportunities', methods=['GET'])
@require_auth
def get_opportunities(analysis_id):
    """Get opportunities for an analysis"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Verify access to analysis
    opportunity_analysis = OpportunityAnalysis.query.filter_by(
        id=analysis_id, tenant_id=tenant_id
    ).first()
    
    if not opportunity_analysis:
        return jsonify({'error': 'Opportunity analysis not found'}), 404
    
    # Get filter parameters
    opportunity_type = request.args.get('type')
    min_score = request.args.get('min_score', type=float)
    max_complexity = request.args.get('max_complexity')
    sort_by = request.args.get('sort_by', 'opportunity_score')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Build query
    query = TransformationOpportunity.query.filter_by(analysis_id=analysis_id)
    
    if opportunity_type:
        query = query.filter_by(opportunity_type=opportunity_type)
    if min_score:
        query = query.filter(TransformationOpportunity.opportunity_score >= min_score)
    if max_complexity:
        complexity_order = {'low': 1, 'medium': 2, 'high': 3}
        max_complexity_value = complexity_order.get(max_complexity, 3)
        query = query.filter(
            db.case(
                (TransformationOpportunity.implementation_complexity == 'low', 1),
                (TransformationOpportunity.implementation_complexity == 'medium', 2),
                (TransformationOpportunity.implementation_complexity == 'high', 3),
                else_=3
            ) <= max_complexity_value
        )
    
    # Apply sorting
    if hasattr(TransformationOpportunity, sort_by):
        sort_column = getattr(TransformationOpportunity, sort_by)
        if sort_order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
    
    opportunities = query.all()
    
    return jsonify({
        'opportunities': [opp.to_dict() for opp in opportunities],
        'summary': {
            'total_opportunities': len(opportunities),
            'opportunity_types': list(set(opp.opportunity_type for opp in opportunities)),
            'average_score': sum(opp.opportunity_score for opp in opportunities) / len(opportunities) if opportunities else 0,
            'total_estimated_value': sum(opp.estimated_annual_value or 0 for opp in opportunities)
        }
    })

@opportunities_bp.route('/opportunity/<opportunity_id>', methods=['GET'])
@require_auth
def get_opportunity_details(opportunity_id):
    """Get detailed information about a specific opportunity"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Get opportunity and verify access through analysis
    opportunity = db.session.query(TransformationOpportunity).join(OpportunityAnalysis).filter(
        TransformationOpportunity.id == opportunity_id,
        OpportunityAnalysis.tenant_id == tenant_id
    ).first()
    
    if not opportunity:
        return jsonify({'error': 'Opportunity not found'}), 404
    
    return jsonify({
        'opportunity': opportunity.to_dict()
    })

@opportunities_bp.route('/opportunity/<opportunity_id>/score', methods=['PUT'])
@require_auth
def update_opportunity_score(opportunity_id):
    """Update opportunity scoring"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Get opportunity and verify access
    opportunity = db.session.query(TransformationOpportunity).join(OpportunityAnalysis).filter(
        TransformationOpportunity.id == opportunity_id,
        OpportunityAnalysis.tenant_id == tenant_id
    ).first()
    
    if not opportunity:
        return jsonify({'error': 'Opportunity not found'}), 404
    
    # Get update data
    update_data = request.get_json()
    
    # Update scoring fields
    if 'opportunity_score' in update_data:
        opportunity.opportunity_score = update_data['opportunity_score']
    if 'priority_score' in update_data:
        opportunity.priority_score = update_data['priority_score']
    if 'confidence_score' in update_data:
        opportunity.confidence_score = update_data['confidence_score']
    
    # Update financial estimates
    if 'estimated_annual_value' in update_data:
        opportunity.estimated_annual_value = update_data['estimated_annual_value']
    if 'estimated_cost' in update_data:
        opportunity.estimated_cost = update_data['estimated_cost']
        # Recalculate ROI
        if opportunity.estimated_cost > 0:
            opportunity.estimated_roi = ((opportunity.estimated_annual_value - opportunity.estimated_cost) / opportunity.estimated_cost) * 100
    
    # Update implementation assessment
    if 'implementation_complexity' in update_data:
        opportunity.implementation_complexity = update_data['implementation_complexity']
    if 'estimated_effort_months' in update_data:
        opportunity.estimated_effort_months = update_data['estimated_effort_months']
    
    opportunity.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Opportunity scoring updated successfully',
        'opportunity': opportunity.to_dict()
    })

@opportunities_bp.route('/dashboard/<analysis_id>', methods=['GET'])
@require_auth
def get_opportunities_dashboard(analysis_id):
    """Get comprehensive opportunities dashboard"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Verify access
    opportunity_analysis = OpportunityAnalysis.query.filter_by(
        id=analysis_id, tenant_id=tenant_id
    ).first()
    
    if not opportunity_analysis:
        return jsonify({'error': 'Opportunity analysis not found'}), 404
    
    # Get all opportunities
    opportunities = TransformationOpportunity.query.filter_by(analysis_id=analysis_id).all()
    
    # Build dashboard data
    dashboard = {
        'overview': {
            'analysis_id': analysis_id,
            'total_opportunities': len(opportunities),
            'analysis_status': opportunity_analysis.analysis_status,
            'total_estimated_value': opportunity_analysis.total_estimated_value,
            'average_roi': opportunity_analysis.average_roi,
            'overall_confidence': opportunity_analysis.confidence_score
        },
        'opportunity_breakdown': {
            'by_type': {},
            'by_complexity': {'low': 0, 'medium': 0, 'high': 0},
            'by_risk': {'low': 0, 'medium': 0, 'high': 0},
            'by_value_range': {'low': 0, 'medium': 0, 'high': 0}
        },
        'top_opportunities': [],
        'quick_wins': [],
        'strategic_initiatives': [],
        'financial_summary': {
            'total_investment_required': 0,
            'total_annual_value': 0,
            'average_payback_months': 0,
            'roi_distribution': []
        }
    }
    
    # Process opportunities
    total_investment = 0
    payback_periods = []
    roi_values = []
    
    for opp in opportunities:
        # Type breakdown
        opp_type = opp.opportunity_type
        if opp_type not in dashboard['opportunity_breakdown']['by_type']:
            dashboard['opportunity_breakdown']['by_type'][opp_type] = 0
        dashboard['opportunity_breakdown']['by_type'][opp_type] += 1
        
        # Complexity breakdown
        dashboard['opportunity_breakdown']['by_complexity'][opp.implementation_complexity] += 1
        
        # Risk breakdown
        dashboard['opportunity_breakdown']['by_risk'][opp.implementation_risk] += 1
        
        # Value range breakdown
        annual_value = opp.estimated_annual_value or 0
        if annual_value < 50000:
            dashboard['opportunity_breakdown']['by_value_range']['low'] += 1
        elif annual_value < 200000:
            dashboard['opportunity_breakdown']['by_value_range']['medium'] += 1
        else:
            dashboard['opportunity_breakdown']['by_value_range']['high'] += 1
        
        # Financial aggregation
        total_investment += opp.estimated_cost or 0
        if opp.payback_period_months and opp.payback_period_months > 0:
            payback_periods.append(opp.payback_period_months)
        if opp.estimated_roi and opp.estimated_roi > 0:
            roi_values.append(opp.estimated_roi)
        
        # Categorize opportunities
        if opp.opportunity_score >= 80:
            dashboard['top_opportunities'].append({
                'id': opp.id,
                'name': opp.opportunity_name,
                'score': opp.opportunity_score,
                'estimated_value': opp.estimated_annual_value,
                'roi': opp.estimated_roi
            })
        
        # Quick wins: high value, low complexity, low risk
        if (opp.implementation_complexity == 'low' and 
            opp.implementation_risk == 'low' and 
            (opp.estimated_annual_value or 0) > 25000):
            dashboard['quick_wins'].append({
                'id': opp.id,
                'name': opp.opportunity_name,
                'estimated_value': opp.estimated_annual_value,
                'effort_months': opp.estimated_effort_months
            })
        
        # Strategic initiatives: high value, potentially high complexity
        if (opp.estimated_annual_value or 0) > 100000:
            dashboard['strategic_initiatives'].append({
                'id': opp.id,
                'name': opp.opportunity_name,
                'estimated_value': opp.estimated_annual_value,
                'complexity': opp.implementation_complexity,
                'effort_months': opp.estimated_effort_months
            })
    
    # Complete financial summary
    dashboard['financial_summary']['total_investment_required'] = total_investment
    dashboard['financial_summary']['total_annual_value'] = opportunity_analysis.total_estimated_value
    dashboard['financial_summary']['average_payback_months'] = sum(payback_periods) / len(payback_periods) if payback_periods else 0
    dashboard['financial_summary']['roi_distribution'] = roi_values
    
    # Limit lists for dashboard display
    dashboard['top_opportunities'] = sorted(dashboard['top_opportunities'], key=lambda x: x['score'], reverse=True)[:10]
    dashboard['quick_wins'] = sorted(dashboard['quick_wins'], key=lambda x: x['estimated_value'], reverse=True)[:5]
    dashboard['strategic_initiatives'] = sorted(dashboard['strategic_initiatives'], key=lambda x: x['estimated_value'], reverse=True)[:5]
    
    return jsonify({
        'dashboard': dashboard
    })

