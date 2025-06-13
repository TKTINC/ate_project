"""
ATE Architecture Design Service - Architecture Design Management
Technical specification generation and blueprint creation routes
"""

from flask import Blueprint, request, jsonify
from src.models.user import db, ArchitectureDesign
from src.utils.auth import require_auth, get_current_user, get_tenant_id
from src.utils.opportunity_client import OpportunityClient
from src.analyzers.design_generator import DesignGenerator
from src.analyzers.specification_generator import SpecificationGenerator
import uuid
from datetime import datetime

designs_bp = Blueprint('designs', __name__)

@designs_bp.route('/designs', methods=['GET'])
@require_auth
def list_designs():
    """List architecture designs for the current tenant"""
    try:
        tenant_id = get_tenant_id()
        
        # Get query parameters
        design_type = request.args.get('type')
        design_status = request.args.get('status')
        opportunity_id = request.args.get('opportunity_id')
        
        # Build query
        query = ArchitectureDesign.query.filter_by(tenant_id=tenant_id)
        
        if design_type:
            query = query.filter_by(design_type=design_type)
        if design_status:
            query = query.filter_by(design_status=design_status)
        if opportunity_id:
            query = query.filter_by(opportunity_id=opportunity_id)
        
        designs = query.order_by(ArchitectureDesign.created_at.desc()).all()
        
        return jsonify({
            'status': 'success',
            'designs': [design.to_dict() for design in designs],
            'total_count': len(designs)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@designs_bp.route('/designs/<design_id>', methods=['GET'])
@require_auth
def get_design(design_id):
    """Get detailed architecture design information"""
    try:
        tenant_id = get_tenant_id()
        
        design = ArchitectureDesign.query.filter_by(
            id=design_id, 
            tenant_id=tenant_id
        ).first()
        
        if not design:
            return jsonify({'status': 'error', 'message': 'Design not found'}), 404
        
        return jsonify({
            'status': 'success',
            'design': design.to_dict()
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@designs_bp.route('/designs/generate', methods=['POST'])
@require_auth
def generate_design():
    """Generate architecture design from opportunity"""
    try:
        data = request.get_json()
        tenant_id = get_tenant_id()
        current_user = get_current_user()
        
        # Validate required fields
        opportunity_id = data.get('opportunity_id')
        if not opportunity_id:
            return jsonify({'status': 'error', 'message': 'opportunity_id is required'}), 400
        
        # Get opportunity details
        opportunity_client = OpportunityClient()
        opportunity = opportunity_client.get_opportunity(opportunity_id)
        
        if not opportunity:
            return jsonify({'status': 'error', 'message': 'Opportunity not found'}), 404
        
        # Generate architecture design
        design_generator = DesignGenerator()
        design_data = design_generator.generate_design(
            opportunity=opportunity,
            design_preferences=data.get('design_preferences', {}),
            technical_constraints=data.get('technical_constraints', {}),
            business_requirements=data.get('business_requirements', {})
        )
        
        # Create design record
        design = ArchitectureDesign(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            opportunity_id=opportunity_id,
            business_case_id=opportunity.get('business_case_id'),
            design_name=design_data['design_name'],
            design_type=opportunity['opportunity_type'],
            design_scope=design_data['design_scope'],
            design_status='draft',
            architecture_overview=design_data['architecture_overview'],
            system_architecture=design_data['system_architecture'],
            component_design=design_data['component_design'],
            data_architecture=design_data['data_architecture'],
            integration_architecture=design_data['integration_architecture'],
            security_architecture=design_data['security_architecture'],
            deployment_architecture=design_data['deployment_architecture'],
            technology_stack=design_data['technology_stack'],
            technology_rationale=design_data['technology_rationale'],
            architecture_patterns=design_data['architecture_patterns'],
            design_decisions=design_data['design_decisions'],
            implementation_phases=design_data['implementation_phases'],
            resource_requirements=design_data['resource_requirements'],
            timeline_estimate=design_data['timeline_estimate'],
            risk_assessment=design_data['risk_assessment'],
            performance_requirements=design_data['performance_requirements'],
            scalability_design=design_data['scalability_design'],
            reliability_design=design_data['reliability_design'],
            maintainability_design=design_data['maintainability_design'],
            created_by=current_user.get('username', 'system')
        )
        
        db.session.add(design)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Architecture design generated successfully',
            'design_id': design.id,
            'design': design.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@designs_bp.route('/designs/<design_id>/specifications', methods=['POST'])
@require_auth
def generate_specifications(design_id):
    """Generate detailed technical specifications for design"""
    try:
        tenant_id = get_tenant_id()
        
        design = ArchitectureDesign.query.filter_by(
            id=design_id, 
            tenant_id=tenant_id
        ).first()
        
        if not design:
            return jsonify({'status': 'error', 'message': 'Design not found'}), 404
        
        data = request.get_json()
        specification_type = data.get('specification_type', 'comprehensive')
        
        # Generate technical specifications
        spec_generator = SpecificationGenerator()
        specifications = spec_generator.generate_specifications(
            design=design.to_dict(),
            specification_type=specification_type,
            detail_level=data.get('detail_level', 'detailed')
        )
        
        # Update design with specifications
        design.technical_specifications = specifications
        design.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Technical specifications generated successfully',
            'specifications': specifications
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@designs_bp.route('/designs/<design_id>/documentation', methods=['POST'])
@require_auth
def generate_documentation(design_id):
    """Generate comprehensive design documentation"""
    try:
        tenant_id = get_tenant_id()
        
        design = ArchitectureDesign.query.filter_by(
            id=design_id, 
            tenant_id=tenant_id
        ).first()
        
        if not design:
            return jsonify({'status': 'error', 'message': 'Design not found'}), 404
        
        data = request.get_json()
        documentation_type = data.get('documentation_type', 'comprehensive')
        
        # Generate design documentation
        spec_generator = SpecificationGenerator()
        documentation = spec_generator.generate_documentation(
            design=design.to_dict(),
            documentation_type=documentation_type,
            target_audience=data.get('target_audience', 'technical')
        )
        
        # Update design with documentation
        design.design_documentation = documentation
        design.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Design documentation generated successfully',
            'documentation': documentation
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@designs_bp.route('/designs/<design_id>/diagrams', methods=['POST'])
@require_auth
def generate_diagrams(design_id):
    """Generate architecture diagrams for design"""
    try:
        tenant_id = get_tenant_id()
        
        design = ArchitectureDesign.query.filter_by(
            id=design_id, 
            tenant_id=tenant_id
        ).first()
        
        if not design:
            return jsonify({'status': 'error', 'message': 'Design not found'}), 404
        
        data = request.get_json()
        diagram_types = data.get('diagram_types', ['system', 'component', 'deployment'])
        
        # Generate architecture diagrams
        spec_generator = SpecificationGenerator()
        diagrams = spec_generator.generate_diagrams(
            design=design.to_dict(),
            diagram_types=diagram_types,
            diagram_format=data.get('diagram_format', 'mermaid')
        )
        
        # Update design with diagrams
        design.architecture_diagrams = diagrams
        design.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Architecture diagrams generated successfully',
            'diagrams': diagrams
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@designs_bp.route('/designs/<design_id>', methods=['PUT'])
@require_auth
def update_design(design_id):
    """Update architecture design"""
    try:
        tenant_id = get_tenant_id()
        
        design = ArchitectureDesign.query.filter_by(
            id=design_id, 
            tenant_id=tenant_id
        ).first()
        
        if not design:
            return jsonify({'status': 'error', 'message': 'Design not found'}), 404
        
        data = request.get_json()
        
        # Update design fields
        updatable_fields = [
            'design_name', 'design_scope', 'design_status',
            'architecture_overview', 'system_architecture', 'component_design',
            'data_architecture', 'integration_architecture', 'security_architecture',
            'deployment_architecture', 'technology_stack', 'technology_rationale',
            'architecture_patterns', 'design_decisions', 'implementation_phases',
            'resource_requirements', 'timeline_estimate', 'risk_assessment',
            'performance_requirements', 'scalability_design', 'reliability_design',
            'maintainability_design'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(design, field, data[field])
        
        design.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Design updated successfully',
            'design': design.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@designs_bp.route('/designs/<design_id>/validate', methods=['POST'])
@require_auth
def validate_design(design_id):
    """Validate architecture design against requirements and best practices"""
    try:
        tenant_id = get_tenant_id()
        
        design = ArchitectureDesign.query.filter_by(
            id=design_id, 
            tenant_id=tenant_id
        ).first()
        
        if not design:
            return jsonify({'status': 'error', 'message': 'Design not found'}), 404
        
        data = request.get_json()
        validation_type = data.get('validation_type', 'comprehensive')
        
        # Validate design
        design_generator = DesignGenerator()
        validation_results = design_generator.validate_design(
            design=design.to_dict(),
            validation_type=validation_type,
            validation_criteria=data.get('validation_criteria', {})
        )
        
        # Update design with validation results
        design.design_validation = validation_results
        design.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Design validation completed',
            'validation_results': validation_results
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@designs_bp.route('/designs/<design_id>/approve', methods=['POST'])
@require_auth
def approve_design(design_id):
    """Approve architecture design"""
    try:
        tenant_id = get_tenant_id()
        current_user = get_current_user()
        
        design = ArchitectureDesign.query.filter_by(
            id=design_id, 
            tenant_id=tenant_id
        ).first()
        
        if not design:
            return jsonify({'status': 'error', 'message': 'Design not found'}), 404
        
        data = request.get_json()
        approval_comments = data.get('approval_comments', '')
        
        # Update design approval status
        design.design_status = 'approved'
        design.approved_at = datetime.utcnow()
        design.approved_by = current_user.get('username', 'system')
        design.stakeholder_approval = {
            'approved_at': datetime.utcnow().isoformat(),
            'approved_by': current_user.get('username', 'system'),
            'approval_comments': approval_comments
        }
        design.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Design approved successfully',
            'design': design.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@designs_bp.route('/designs/statistics', methods=['GET'])
@require_auth
def get_design_statistics():
    """Get design statistics for the current tenant"""
    try:
        tenant_id = get_tenant_id()
        
        # Get design statistics
        total_designs = ArchitectureDesign.query.filter_by(tenant_id=tenant_id).count()
        
        # Status distribution
        status_distribution = db.session.query(
            ArchitectureDesign.design_status,
            db.func.count(ArchitectureDesign.id)
        ).filter_by(tenant_id=tenant_id).group_by(ArchitectureDesign.design_status).all()
        
        # Type distribution
        type_distribution = db.session.query(
            ArchitectureDesign.design_type,
            db.func.count(ArchitectureDesign.id)
        ).filter_by(tenant_id=tenant_id).group_by(ArchitectureDesign.design_type).all()
        
        # Recent designs
        recent_designs = ArchitectureDesign.query.filter_by(tenant_id=tenant_id).order_by(
            ArchitectureDesign.created_at.desc()
        ).limit(10).all()
        
        return jsonify({
            'status': 'success',
            'statistics': {
                'total_designs': total_designs,
                'status_distribution': {s[0]: s[1] for s in status_distribution},
                'type_distribution': {t[0]: t[1] for t in type_distribution},
                'recent_designs': [d.to_dict() for d in recent_designs]
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

