"""
ATE Architecture Design Service - Implementation Planning
Resource allocation and project management routes
"""

from flask import Blueprint, request, jsonify
from src.models.user import db, ImplementationPlan, ArchitectureDesign
from src.utils.auth import require_auth, get_current_user, get_tenant_id
from src.analyzers.implementation_planner import ImplementationPlanner
from src.analyzers.resource_allocator import ResourceAllocator
import uuid
from datetime import datetime

implementations_bp = Blueprint('implementations', __name__)

@implementations_bp.route('/implementations', methods=['GET'])
@require_auth
def list_implementation_plans():
    """List implementation plans for the current tenant"""
    try:
        tenant_id = get_tenant_id()
        
        # Get query parameters
        plan_type = request.args.get('type')
        plan_status = request.args.get('status')
        architecture_design_id = request.args.get('design_id')
        
        # Build query
        query = ImplementationPlan.query.filter_by(tenant_id=tenant_id)
        
        if plan_type:
            query = query.filter_by(plan_type=plan_type)
        if plan_status:
            query = query.filter_by(plan_status=plan_status)
        if architecture_design_id:
            query = query.filter_by(architecture_design_id=architecture_design_id)
        
        plans = query.order_by(ImplementationPlan.created_at.desc()).all()
        
        return jsonify({
            'status': 'success',
            'implementation_plans': [plan.to_dict() for plan in plans],
            'total_count': len(plans)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@implementations_bp.route('/implementations/<plan_id>', methods=['GET'])
@require_auth
def get_implementation_plan(plan_id):
    """Get detailed implementation plan information"""
    try:
        tenant_id = get_tenant_id()
        
        plan = ImplementationPlan.query.filter_by(
            id=plan_id, 
            tenant_id=tenant_id
        ).first()
        
        if not plan:
            return jsonify({'status': 'error', 'message': 'Implementation plan not found'}), 404
        
        return jsonify({
            'status': 'success',
            'implementation_plan': plan.to_dict()
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@implementations_bp.route('/implementations/generate', methods=['POST'])
@require_auth
def generate_implementation_plan():
    """Generate implementation plan from architecture design"""
    try:
        data = request.get_json()
        tenant_id = get_tenant_id()
        current_user = get_current_user()
        
        # Validate required fields
        architecture_design_id = data.get('architecture_design_id')
        if not architecture_design_id:
            return jsonify({'status': 'error', 'message': 'architecture_design_id is required'}), 400
        
        # Get architecture design
        design = ArchitectureDesign.query.filter_by(
            id=architecture_design_id,
            tenant_id=tenant_id
        ).first()
        
        if not design:
            return jsonify({'status': 'error', 'message': 'Architecture design not found'}), 404
        
        # Generate implementation plan
        implementation_planner = ImplementationPlanner()
        plan_data = implementation_planner.generate_plan(
            design=design.to_dict(),
            planning_preferences=data.get('planning_preferences', {}),
            resource_constraints=data.get('resource_constraints', {}),
            timeline_constraints=data.get('timeline_constraints', {})
        )
        
        # Create implementation plan record
        plan = ImplementationPlan(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            architecture_design_id=architecture_design_id,
            opportunity_id=design.opportunity_id,
            plan_name=plan_data['plan_name'],
            plan_type=plan_data['plan_type'],
            plan_status='draft',
            project_phases=plan_data['project_phases'],
            work_breakdown=plan_data['work_breakdown'],
            deliverables=plan_data['deliverables'],
            milestones=plan_data['milestones'],
            timeline_estimate=plan_data['timeline_estimate'],
            critical_path=plan_data['critical_path'],
            dependencies=plan_data['dependencies'],
            schedule_buffer=plan_data['schedule_buffer'],
            resource_requirements=plan_data['resource_requirements'],
            skill_requirements=plan_data['skill_requirements'],
            team_structure=plan_data['team_structure'],
            external_resources=plan_data['external_resources'],
            cost_breakdown=plan_data['cost_breakdown'],
            budget_allocation=plan_data['budget_allocation'],
            cost_tracking=plan_data['cost_tracking'],
            risk_assessment=plan_data['risk_assessment'],
            risk_mitigation=plan_data['risk_mitigation'],
            contingency_plans=plan_data['contingency_plans'],
            quality_gates=plan_data['quality_gates'],
            governance_framework=plan_data['governance_framework'],
            approval_process=plan_data['approval_process'],
            success_criteria=plan_data['success_criteria'],
            monitoring_framework=plan_data['monitoring_framework'],
            reporting_schedule=plan_data['reporting_schedule'],
            created_by=current_user.get('username', 'system')
        )
        
        db.session.add(plan)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Implementation plan generated successfully',
            'plan_id': plan.id,
            'implementation_plan': plan.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@implementations_bp.route('/implementations/<plan_id>/resources', methods=['POST'])
@require_auth
def allocate_resources(plan_id):
    """Allocate resources for implementation plan"""
    try:
        tenant_id = get_tenant_id()
        
        plan = ImplementationPlan.query.filter_by(
            id=plan_id, 
            tenant_id=tenant_id
        ).first()
        
        if not plan:
            return jsonify({'status': 'error', 'message': 'Implementation plan not found'}), 404
        
        data = request.get_json()
        
        # Allocate resources
        resource_allocator = ResourceAllocator()
        allocation_results = resource_allocator.allocate_resources(
            plan=plan.to_dict(),
            available_resources=data.get('available_resources', {}),
            allocation_preferences=data.get('allocation_preferences', {}),
            constraints=data.get('constraints', {})
        )
        
        # Update plan with resource allocation
        plan.resource_requirements = allocation_results['updated_resource_requirements']
        plan.team_structure = allocation_results['team_structure']
        plan.external_resources = allocation_results['external_resources']
        plan.cost_breakdown = allocation_results['cost_breakdown']
        plan.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Resources allocated successfully',
            'allocation_results': allocation_results
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@implementations_bp.route('/implementations/<plan_id>/timeline', methods=['POST'])
@require_auth
def optimize_timeline(plan_id):
    """Optimize implementation timeline"""
    try:
        tenant_id = get_tenant_id()
        
        plan = ImplementationPlan.query.filter_by(
            id=plan_id, 
            tenant_id=tenant_id
        ).first()
        
        if not plan:
            return jsonify({'status': 'error', 'message': 'Implementation plan not found'}), 404
        
        data = request.get_json()
        
        # Optimize timeline
        implementation_planner = ImplementationPlanner()
        timeline_optimization = implementation_planner.optimize_timeline(
            plan=plan.to_dict(),
            optimization_criteria=data.get('optimization_criteria', {}),
            constraints=data.get('constraints', {})
        )
        
        # Update plan with optimized timeline
        plan.timeline_estimate = timeline_optimization['optimized_timeline']
        plan.critical_path = timeline_optimization['critical_path']
        plan.dependencies = timeline_optimization['dependencies']
        plan.schedule_buffer = timeline_optimization['schedule_buffer']
        plan.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Timeline optimized successfully',
            'timeline_optimization': timeline_optimization
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@implementations_bp.route('/implementations/<plan_id>/risks', methods=['POST'])
@require_auth
def assess_implementation_risks(plan_id):
    """Assess implementation risks and generate mitigation strategies"""
    try:
        tenant_id = get_tenant_id()
        
        plan = ImplementationPlan.query.filter_by(
            id=plan_id, 
            tenant_id=tenant_id
        ).first()
        
        if not plan:
            return jsonify({'status': 'error', 'message': 'Implementation plan not found'}), 404
        
        data = request.get_json()
        
        # Assess risks
        implementation_planner = ImplementationPlanner()
        risk_assessment = implementation_planner.assess_risks(
            plan=plan.to_dict(),
            risk_tolerance=data.get('risk_tolerance', 'medium'),
            additional_risks=data.get('additional_risks', [])
        )
        
        # Update plan with risk assessment
        plan.risk_assessment = risk_assessment['risk_assessment']
        plan.risk_mitigation = risk_assessment['risk_mitigation']
        plan.contingency_plans = risk_assessment['contingency_plans']
        plan.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Risk assessment completed successfully',
            'risk_assessment': risk_assessment
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@implementations_bp.route('/implementations/<plan_id>', methods=['PUT'])
@require_auth
def update_implementation_plan(plan_id):
    """Update implementation plan"""
    try:
        tenant_id = get_tenant_id()
        
        plan = ImplementationPlan.query.filter_by(
            id=plan_id, 
            tenant_id=tenant_id
        ).first()
        
        if not plan:
            return jsonify({'status': 'error', 'message': 'Implementation plan not found'}), 404
        
        data = request.get_json()
        
        # Update plan fields
        updatable_fields = [
            'plan_name', 'plan_status', 'project_phases', 'work_breakdown',
            'deliverables', 'milestones', 'timeline_estimate', 'critical_path',
            'dependencies', 'schedule_buffer', 'resource_requirements',
            'skill_requirements', 'team_structure', 'external_resources',
            'cost_breakdown', 'budget_allocation', 'cost_tracking',
            'risk_assessment', 'risk_mitigation', 'contingency_plans',
            'quality_gates', 'governance_framework', 'approval_process',
            'success_criteria', 'monitoring_framework', 'reporting_schedule'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(plan, field, data[field])
        
        plan.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Implementation plan updated successfully',
            'implementation_plan': plan.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@implementations_bp.route('/implementations/<plan_id>/approve', methods=['POST'])
@require_auth
def approve_implementation_plan(plan_id):
    """Approve implementation plan"""
    try:
        tenant_id = get_tenant_id()
        current_user = get_current_user()
        
        plan = ImplementationPlan.query.filter_by(
            id=plan_id, 
            tenant_id=tenant_id
        ).first()
        
        if not plan:
            return jsonify({'status': 'error', 'message': 'Implementation plan not found'}), 404
        
        data = request.get_json()
        approval_comments = data.get('approval_comments', '')
        
        # Update plan approval status
        plan.plan_status = 'approved'
        plan.approved_at = datetime.utcnow()
        plan.approved_by = current_user.get('username', 'system')
        plan.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Implementation plan approved successfully',
            'implementation_plan': plan.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@implementations_bp.route('/implementations/statistics', methods=['GET'])
@require_auth
def get_implementation_statistics():
    """Get implementation statistics for the current tenant"""
    try:
        tenant_id = get_tenant_id()
        
        # Get implementation statistics
        total_plans = ImplementationPlan.query.filter_by(tenant_id=tenant_id).count()
        
        # Status distribution
        status_distribution = db.session.query(
            ImplementationPlan.plan_status,
            db.func.count(ImplementationPlan.id)
        ).filter_by(tenant_id=tenant_id).group_by(ImplementationPlan.plan_status).all()
        
        # Type distribution
        type_distribution = db.session.query(
            ImplementationPlan.plan_type,
            db.func.count(ImplementationPlan.id)
        ).filter_by(tenant_id=tenant_id).group_by(ImplementationPlan.plan_type).all()
        
        # Recent plans
        recent_plans = ImplementationPlan.query.filter_by(tenant_id=tenant_id).order_by(
            ImplementationPlan.created_at.desc()
        ).limit(10).all()
        
        return jsonify({
            'status': 'success',
            'statistics': {
                'total_plans': total_plans,
                'status_distribution': {s[0]: s[1] for s in status_distribution},
                'type_distribution': {t[0]: t[1] for t in type_distribution},
                'recent_plans': [p.to_dict() for p in recent_plans]
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

