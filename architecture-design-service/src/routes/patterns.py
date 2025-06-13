"""
ATE Architecture Design Service - Architecture Patterns Management
Comprehensive pattern library and template engine routes
"""

from flask import Blueprint, request, jsonify
from src.models.user import db, ArchitecturePattern
from src.utils.auth import require_auth, get_current_user
from src.analyzers.pattern_matcher import PatternMatcher
import uuid
from datetime import datetime

patterns_bp = Blueprint('patterns', __name__)

@patterns_bp.route('/patterns', methods=['GET'])
@require_auth
def list_patterns():
    """List all available architecture patterns with filtering"""
    try:
        # Get query parameters
        pattern_type = request.args.get('type')
        pattern_category = request.args.get('category')
        complexity_level = request.args.get('complexity')
        industry_focus = request.args.get('industry')
        
        # Build query
        query = ArchitecturePattern.query.filter_by(is_active=True)
        
        if pattern_type:
            query = query.filter_by(pattern_type=pattern_type)
        if pattern_category:
            query = query.filter_by(pattern_category=pattern_category)
        if complexity_level:
            query = query.filter_by(complexity_level=complexity_level)
        
        patterns = query.all()
        
        # Filter by industry if specified
        if industry_focus:
            patterns = [p for p in patterns if industry_focus in (p.industry_focus or [])]
        
        return jsonify({
            'status': 'success',
            'patterns': [pattern.to_dict() for pattern in patterns],
            'total_count': len(patterns)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@patterns_bp.route('/patterns/<pattern_id>', methods=['GET'])
@require_auth
def get_pattern(pattern_id):
    """Get detailed pattern information"""
    try:
        pattern = ArchitecturePattern.query.get(pattern_id)
        if not pattern or not pattern.is_active:
            return jsonify({'status': 'error', 'message': 'Pattern not found'}), 404
        
        return jsonify({
            'status': 'success',
            'pattern': pattern.to_dict()
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@patterns_bp.route('/patterns', methods=['POST'])
@require_auth
def create_pattern():
    """Create a new architecture pattern"""
    try:
        data = request.get_json()
        current_user = get_current_user()
        
        # Validate required fields
        required_fields = ['pattern_name', 'pattern_type', 'pattern_category', 'pattern_description']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
        
        # Create new pattern
        pattern = ArchitecturePattern(
            id=str(uuid.uuid4()),
            pattern_name=data['pattern_name'],
            pattern_type=data['pattern_type'],
            pattern_category=data['pattern_category'],
            pattern_description=data['pattern_description'],
            pattern_definition=data.get('pattern_definition', {}),
            technology_stack=data.get('technology_stack', {}),
            design_principles=data.get('design_principles', {}),
            implementation_guidelines=data.get('implementation_guidelines', {}),
            complexity_level=data.get('complexity_level', 'medium'),
            maturity_level=data.get('maturity_level', 'stable'),
            industry_focus=data.get('industry_focus', []),
            use_cases=data.get('use_cases', []),
            compatible_patterns=data.get('compatible_patterns', []),
            alternative_patterns=data.get('alternative_patterns', []),
            prerequisite_patterns=data.get('prerequisite_patterns', []),
            average_implementation_time=data.get('average_implementation_time'),
            created_by=current_user.get('username', 'system')
        )
        
        db.session.add(pattern)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Pattern created successfully',
            'pattern_id': pattern.id,
            'pattern': pattern.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@patterns_bp.route('/patterns/<pattern_id>', methods=['PUT'])
@require_auth
def update_pattern(pattern_id):
    """Update an existing architecture pattern"""
    try:
        pattern = ArchitecturePattern.query.get(pattern_id)
        if not pattern:
            return jsonify({'status': 'error', 'message': 'Pattern not found'}), 404
        
        data = request.get_json()
        
        # Update pattern fields
        updatable_fields = [
            'pattern_name', 'pattern_description', 'pattern_definition',
            'technology_stack', 'design_principles', 'implementation_guidelines',
            'complexity_level', 'maturity_level', 'industry_focus', 'use_cases',
            'compatible_patterns', 'alternative_patterns', 'prerequisite_patterns',
            'average_implementation_time'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(pattern, field, data[field])
        
        pattern.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Pattern updated successfully',
            'pattern': pattern.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@patterns_bp.route('/patterns/<pattern_id>/usage', methods=['POST'])
@require_auth
def record_pattern_usage(pattern_id):
    """Record pattern usage for learning and optimization"""
    try:
        pattern = ArchitecturePattern.query.get(pattern_id)
        if not pattern:
            return jsonify({'status': 'error', 'message': 'Pattern not found'}), 404
        
        data = request.get_json()
        success = data.get('success', True)
        implementation_time = data.get('implementation_time')
        
        # Update usage statistics
        pattern.usage_count += 1
        
        if success and implementation_time:
            # Update success rate and average implementation time
            total_successes = pattern.usage_count * pattern.success_rate
            if success:
                total_successes += 1
            pattern.success_rate = total_successes / pattern.usage_count
            
            if pattern.average_implementation_time:
                pattern.average_implementation_time = (
                    (pattern.average_implementation_time * (pattern.usage_count - 1) + implementation_time) / 
                    pattern.usage_count
                )
            else:
                pattern.average_implementation_time = implementation_time
        
        pattern.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Pattern usage recorded successfully',
            'updated_statistics': {
                'usage_count': pattern.usage_count,
                'success_rate': pattern.success_rate,
                'average_implementation_time': pattern.average_implementation_time
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@patterns_bp.route('/patterns/recommend', methods=['POST'])
@require_auth
def recommend_patterns():
    """Recommend patterns based on opportunity requirements"""
    try:
        data = request.get_json()
        
        # Get opportunity context
        opportunity_type = data.get('opportunity_type')
        business_domain = data.get('business_domain')
        technical_requirements = data.get('technical_requirements', {})
        complexity_preference = data.get('complexity_preference', 'medium')
        
        # Use pattern matcher to find suitable patterns
        pattern_matcher = PatternMatcher()
        recommendations = pattern_matcher.recommend_patterns(
            opportunity_type=opportunity_type,
            business_domain=business_domain,
            technical_requirements=technical_requirements,
            complexity_preference=complexity_preference
        )
        
        return jsonify({
            'status': 'success',
            'recommendations': recommendations,
            'recommendation_count': len(recommendations)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@patterns_bp.route('/patterns/types', methods=['GET'])
@require_auth
def get_pattern_types():
    """Get available pattern types and categories"""
    try:
        # Get distinct pattern types and categories
        types = db.session.query(ArchitecturePattern.pattern_type).distinct().all()
        categories = db.session.query(ArchitecturePattern.pattern_category).distinct().all()
        complexity_levels = db.session.query(ArchitecturePattern.complexity_level).distinct().all()
        
        return jsonify({
            'status': 'success',
            'pattern_types': [t[0] for t in types if t[0]],
            'pattern_categories': [c[0] for c in categories if c[0]],
            'complexity_levels': [l[0] for l in complexity_levels if l[0]]
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@patterns_bp.route('/patterns/statistics', methods=['GET'])
@require_auth
def get_pattern_statistics():
    """Get pattern usage statistics and analytics"""
    try:
        # Get pattern statistics
        total_patterns = ArchitecturePattern.query.filter_by(is_active=True).count()
        
        # Most used patterns
        most_used = ArchitecturePattern.query.filter_by(is_active=True).order_by(
            ArchitecturePattern.usage_count.desc()
        ).limit(10).all()
        
        # Highest success rate patterns
        highest_success = ArchitecturePattern.query.filter_by(is_active=True).order_by(
            ArchitecturePattern.success_rate.desc()
        ).limit(10).all()
        
        # Pattern type distribution
        type_distribution = db.session.query(
            ArchitecturePattern.pattern_type,
            db.func.count(ArchitecturePattern.id)
        ).filter_by(is_active=True).group_by(ArchitecturePattern.pattern_type).all()
        
        return jsonify({
            'status': 'success',
            'statistics': {
                'total_patterns': total_patterns,
                'most_used_patterns': [p.to_dict() for p in most_used],
                'highest_success_patterns': [p.to_dict() for p in highest_success],
                'type_distribution': {t[0]: t[1] for t in type_distribution}
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

