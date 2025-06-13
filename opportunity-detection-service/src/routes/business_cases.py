"""
ATE Opportunity Detection Service - Business Cases Routes
Comprehensive business case generation and management
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import uuid

from src.models.user import db, OpportunityAnalysis, TransformationOpportunity, BusinessCase
from src.utils.auth import require_auth, get_current_user
from src.analyzers.business_case_generator import BusinessCaseGenerator

business_cases_bp = Blueprint('business_cases', __name__)

@business_cases_bp.route('/generate/<opportunity_id>', methods=['POST'])
@require_auth
def generate_business_case(opportunity_id):
    """Generate comprehensive business case for an opportunity"""
    try:
        current_user = get_current_user()
        tenant_id = current_user['tenant_id']
        
        # Get opportunity and verify access
        opportunity = db.session.query(TransformationOpportunity).join(OpportunityAnalysis).filter(
            TransformationOpportunity.id == opportunity_id,
            OpportunityAnalysis.tenant_id == tenant_id
        ).first()
        
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        # Get generation configuration
        config = request.get_json() or {}
        generation_config = {
            'case_type': config.get('case_type', 'single_opportunity'),
            'include_financial_models': config.get('include_financial_models', True),
            'include_risk_analysis': config.get('include_risk_analysis', True),
            'include_implementation_plan': config.get('include_implementation_plan', True),
            'include_stakeholder_analysis': config.get('include_stakeholder_analysis', True),
            'financial_assumptions': config.get('financial_assumptions', {}),
            'template_version': config.get('template_version', current_app.config['BUSINESS_CASE_TEMPLATE_VERSION'])
        }
        
        # Generate business case
        generator = BusinessCaseGenerator(generation_config)
        business_case_data = generator.generate_business_case(opportunity, current_user)
        
        # Create business case record
        case_id = str(uuid.uuid4())
        business_case = BusinessCase(
            id=case_id,
            analysis_id=opportunity.analysis_id,
            opportunity_id=opportunity_id,
            case_name=business_case_data['case_name'],
            case_type=generation_config['case_type'],
            case_status='draft',
            executive_summary=business_case_data['executive_summary'],
            problem_statement=business_case_data['problem_statement'],
            proposed_solution=business_case_data['proposed_solution'],
            key_benefits=business_case_data['key_benefits'],
            financial_summary=business_case_data['financial_summary'],
            cost_breakdown=business_case_data['cost_breakdown'],
            benefit_analysis=business_case_data['benefit_analysis'],
            roi_analysis=business_case_data['roi_analysis'],
            sensitivity_analysis=business_case_data['sensitivity_analysis'],
            implementation_strategy=business_case_data['implementation_strategy'],
            project_timeline=business_case_data['project_timeline'],
            resource_requirements=business_case_data['resource_requirements'],
            risk_management_plan=business_case_data['risk_management_plan'],
            success_criteria=business_case_data['success_criteria'],
            kpis=business_case_data['kpis'],
            measurement_plan=business_case_data['measurement_plan'],
            stakeholder_analysis=business_case_data['stakeholder_analysis'],
            change_management_plan=business_case_data['change_management_plan'],
            communication_plan=business_case_data['communication_plan'],
            recommendations=business_case_data['recommendations'],
            next_steps=business_case_data['next_steps'],
            decision_criteria=business_case_data['decision_criteria']
        )
        
        db.session.add(business_case)
        db.session.commit()
        
        return jsonify({
            'message': 'Business case generated successfully',
            'business_case_id': case_id,
            'business_case': business_case.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Business case generation failed: {str(e)}'}), 500

@business_cases_bp.route('/<case_id>', methods=['GET'])
@require_auth
def get_business_case(case_id):
    """Get business case details"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Get business case and verify access
    business_case = db.session.query(BusinessCase).join(OpportunityAnalysis).filter(
        BusinessCase.id == case_id,
        OpportunityAnalysis.tenant_id == tenant_id
    ).first()
    
    if not business_case:
        return jsonify({'error': 'Business case not found'}), 404
    
    return jsonify({
        'business_case': business_case.to_dict()
    })

@business_cases_bp.route('/analysis/<analysis_id>', methods=['GET'])
@require_auth
def get_analysis_business_cases(analysis_id):
    """Get all business cases for an analysis"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Verify access to analysis
    opportunity_analysis = OpportunityAnalysis.query.filter_by(
        id=analysis_id, tenant_id=tenant_id
    ).first()
    
    if not opportunity_analysis:
        return jsonify({'error': 'Opportunity analysis not found'}), 404
    
    business_cases = BusinessCase.query.filter_by(analysis_id=analysis_id).all()
    
    return jsonify({
        'business_cases': [bc.to_dict() for bc in business_cases],
        'summary': {
            'total_cases': len(business_cases),
            'draft_cases': len([bc for bc in business_cases if bc.case_status == 'draft']),
            'approved_cases': len([bc for bc in business_cases if bc.approval_status == 'approved'])
        }
    })

@business_cases_bp.route('/<case_id>/approve', methods=['POST'])
@require_auth
def approve_business_case(case_id):
    """Approve a business case"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Get business case and verify access
    business_case = db.session.query(BusinessCase).join(OpportunityAnalysis).filter(
        BusinessCase.id == case_id,
        OpportunityAnalysis.tenant_id == tenant_id
    ).first()
    
    if not business_case:
        return jsonify({'error': 'Business case not found'}), 404
    
    approval_data = request.get_json() or {}
    
    business_case.approval_status = 'approved'
    business_case.approved_by = current_user['username']
    business_case.approved_at = datetime.utcnow()
    business_case.approval_notes = approval_data.get('notes', '')
    business_case.case_status = 'approved'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Business case approved successfully',
        'business_case': business_case.to_dict()
    })

@business_cases_bp.route('/<case_id>/export', methods=['GET'])
@require_auth
def export_business_case(case_id):
    """Export business case in various formats"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Get business case and verify access
    business_case = db.session.query(BusinessCase).join(OpportunityAnalysis).filter(
        BusinessCase.id == case_id,
        OpportunityAnalysis.tenant_id == tenant_id
    ).first()
    
    if not business_case:
        return jsonify({'error': 'Business case not found'}), 404
    
    export_format = request.args.get('format', 'json')
    
    if export_format == 'json':
        return jsonify({
            'business_case': business_case.to_dict(),
            'export_metadata': {
                'exported_at': datetime.utcnow().isoformat(),
                'exported_by': current_user['username'],
                'format': 'json'
            }
        })
    
    # For other formats, return structured data that can be processed by frontend
    return jsonify({
        'message': f'Export format {export_format} not yet implemented',
        'available_formats': ['json', 'pdf', 'docx', 'pptx']
    }), 501

