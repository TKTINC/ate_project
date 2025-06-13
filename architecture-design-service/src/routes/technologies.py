"""
ATE Architecture Design Service - Technology Stack Management
Technology recommendations and stack management routes
"""

from flask import Blueprint, request, jsonify
from src.models.user import db, TechnologyStack
from src.utils.auth import require_auth, get_current_user
from src.analyzers.technology_recommender import TechnologyRecommender
import uuid
from datetime import datetime

technologies_bp = Blueprint('technologies', __name__)

@technologies_bp.route('/technologies', methods=['GET'])
@require_auth
def list_technology_stacks():
    """List all available technology stacks with filtering"""
    try:
        # Get query parameters
        stack_type = request.args.get('type')
        stack_category = request.args.get('category')
        complexity_level = request.args.get('complexity')
        enterprise_readiness = request.args.get('enterprise_readiness')
        
        # Build query
        query = TechnologyStack.query.filter_by(is_active=True)
        
        if stack_type:
            query = query.filter_by(stack_type=stack_type)
        if stack_category:
            query = query.filter_by(stack_category=stack_category)
        if complexity_level:
            query = query.filter_by(complexity_level=complexity_level)
        if enterprise_readiness:
            query = query.filter_by(enterprise_readiness=enterprise_readiness)
        
        stacks = query.all()
        
        return jsonify({
            'status': 'success',
            'technology_stacks': [stack.to_dict() for stack in stacks],
            'total_count': len(stacks)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@technologies_bp.route('/technologies/<stack_id>', methods=['GET'])
@require_auth
def get_technology_stack(stack_id):
    """Get detailed technology stack information"""
    try:
        stack = TechnologyStack.query.get(stack_id)
        if not stack or not stack.is_active:
            return jsonify({'status': 'error', 'message': 'Technology stack not found'}), 404
        
        return jsonify({
            'status': 'success',
            'technology_stack': stack.to_dict()
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@technologies_bp.route('/technologies', methods=['POST'])
@require_auth
def create_technology_stack():
    """Create a new technology stack"""
    try:
        data = request.get_json()
        current_user = get_current_user()
        
        # Validate required fields
        required_fields = ['stack_name', 'stack_type', 'stack_category']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
        
        # Create new technology stack
        stack = TechnologyStack(
            id=str(uuid.uuid4()),
            stack_name=data['stack_name'],
            stack_type=data['stack_type'],
            stack_category=data['stack_category'],
            technologies=data.get('technologies', []),
            technology_versions=data.get('technology_versions', {}),
            compatibility_matrix=data.get('compatibility_matrix', {}),
            configuration_templates=data.get('configuration_templates', {}),
            complexity_level=data.get('complexity_level', 'medium'),
            learning_curve=data.get('learning_curve', 'medium'),
            community_support=data.get('community_support', 'good'),
            enterprise_readiness=data.get('enterprise_readiness', 'production'),
            licensing_model=data.get('licensing_model', 'open_source'),
            estimated_cost=data.get('estimated_cost', {}),
            vendor_dependencies=data.get('vendor_dependencies', {}),
            performance_characteristics=data.get('performance_characteristics', {}),
            scalability_limits=data.get('scalability_limits', {}),
            resource_requirements=data.get('resource_requirements', {}),
            suitable_for=data.get('suitable_for', []),
            not_suitable_for=data.get('not_suitable_for', []),
            industry_adoption=data.get('industry_adoption', {}),
            created_by=current_user.get('username', 'system')
        )
        
        db.session.add(stack)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Technology stack created successfully',
            'stack_id': stack.id,
            'technology_stack': stack.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@technologies_bp.route('/technologies/<stack_id>', methods=['PUT'])
@require_auth
def update_technology_stack(stack_id):
    """Update an existing technology stack"""
    try:
        stack = TechnologyStack.query.get(stack_id)
        if not stack:
            return jsonify({'status': 'error', 'message': 'Technology stack not found'}), 404
        
        data = request.get_json()
        
        # Update stack fields
        updatable_fields = [
            'stack_name', 'technologies', 'technology_versions', 'compatibility_matrix',
            'configuration_templates', 'complexity_level', 'learning_curve',
            'community_support', 'enterprise_readiness', 'licensing_model',
            'estimated_cost', 'vendor_dependencies', 'performance_characteristics',
            'scalability_limits', 'resource_requirements', 'suitable_for',
            'not_suitable_for', 'industry_adoption'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(stack, field, data[field])
        
        stack.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Technology stack updated successfully',
            'technology_stack': stack.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@technologies_bp.route('/technologies/recommend', methods=['POST'])
@require_auth
def recommend_technology_stack():
    """Recommend technology stacks based on requirements"""
    try:
        data = request.get_json()
        
        # Get requirements
        project_requirements = data.get('project_requirements', {})
        technical_constraints = data.get('technical_constraints', {})
        business_constraints = data.get('business_constraints', {})
        
        # Use technology recommender
        tech_recommender = TechnologyRecommender()
        recommendations = tech_recommender.recommend_stacks(
            project_requirements=project_requirements,
            technical_constraints=technical_constraints,
            business_constraints=business_constraints,
            recommendation_criteria=data.get('recommendation_criteria', {})
        )
        
        return jsonify({
            'status': 'success',
            'recommendations': recommendations,
            'recommendation_count': len(recommendations)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@technologies_bp.route('/technologies/compare', methods=['POST'])
@require_auth
def compare_technology_stacks():
    """Compare multiple technology stacks"""
    try:
        data = request.get_json()
        stack_ids = data.get('stack_ids', [])
        
        if len(stack_ids) < 2:
            return jsonify({'status': 'error', 'message': 'At least 2 stacks required for comparison'}), 400
        
        # Get technology stacks
        stacks = TechnologyStack.query.filter(TechnologyStack.id.in_(stack_ids)).all()
        
        if len(stacks) != len(stack_ids):
            return jsonify({'status': 'error', 'message': 'One or more stacks not found'}), 404
        
        # Compare stacks
        tech_recommender = TechnologyRecommender()
        comparison = tech_recommender.compare_stacks(
            stacks=[stack.to_dict() for stack in stacks],
            comparison_criteria=data.get('comparison_criteria', {})
        )
        
        return jsonify({
            'status': 'success',
            'comparison': comparison
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@technologies_bp.route('/technologies/compatibility', methods=['POST'])
@require_auth
def check_compatibility():
    """Check compatibility between technologies"""
    try:
        data = request.get_json()
        technologies = data.get('technologies', [])
        
        if len(technologies) < 2:
            return jsonify({'status': 'error', 'message': 'At least 2 technologies required for compatibility check'}), 400
        
        # Check compatibility
        tech_recommender = TechnologyRecommender()
        compatibility = tech_recommender.check_compatibility(
            technologies=technologies,
            compatibility_criteria=data.get('compatibility_criteria', {})
        )
        
        return jsonify({
            'status': 'success',
            'compatibility': compatibility
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@technologies_bp.route('/technologies/categories', methods=['GET'])
@require_auth
def get_technology_categories():
    """Get available technology categories and types"""
    try:
        # Get distinct categories and types
        types = db.session.query(TechnologyStack.stack_type).distinct().all()
        categories = db.session.query(TechnologyStack.stack_category).distinct().all()
        complexity_levels = db.session.query(TechnologyStack.complexity_level).distinct().all()
        enterprise_readiness = db.session.query(TechnologyStack.enterprise_readiness).distinct().all()
        
        return jsonify({
            'status': 'success',
            'stack_types': [t[0] for t in types if t[0]],
            'stack_categories': [c[0] for c in categories if c[0]],
            'complexity_levels': [l[0] for l in complexity_levels if l[0]],
            'enterprise_readiness_levels': [e[0] for e in enterprise_readiness if e[0]]
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@technologies_bp.route('/technologies/statistics', methods=['GET'])
@require_auth
def get_technology_statistics():
    """Get technology stack statistics and analytics"""
    try:
        # Get technology statistics
        total_stacks = TechnologyStack.query.filter_by(is_active=True).count()
        
        # Type distribution
        type_distribution = db.session.query(
            TechnologyStack.stack_type,
            db.func.count(TechnologyStack.id)
        ).filter_by(is_active=True).group_by(TechnologyStack.stack_type).all()
        
        # Category distribution
        category_distribution = db.session.query(
            TechnologyStack.stack_category,
            db.func.count(TechnologyStack.id)
        ).filter_by(is_active=True).group_by(TechnologyStack.stack_category).all()
        
        # Enterprise readiness distribution
        enterprise_distribution = db.session.query(
            TechnologyStack.enterprise_readiness,
            db.func.count(TechnologyStack.id)
        ).filter_by(is_active=True).group_by(TechnologyStack.enterprise_readiness).all()
        
        return jsonify({
            'status': 'success',
            'statistics': {
                'total_stacks': total_stacks,
                'type_distribution': {t[0]: t[1] for t in type_distribution},
                'category_distribution': {c[0]: c[1] for c in category_distribution},
                'enterprise_distribution': {e[0]: e[1] for e in enterprise_distribution}
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

