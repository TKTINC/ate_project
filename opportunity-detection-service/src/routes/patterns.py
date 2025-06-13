"""
ATE Opportunity Detection Service - Patterns Routes
Opportunity pattern management and learning
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid

from src.models.user import db, OpportunityPattern
from src.utils.auth import require_auth, get_current_user

patterns_bp = Blueprint('patterns', __name__)

@patterns_bp.route('/', methods=['GET'])
@require_auth
def list_patterns():
    """List all opportunity detection patterns"""
    # Get filter parameters
    pattern_type = request.args.get('type')
    pattern_category = request.args.get('category')
    is_active = request.args.get('active', type=bool)
    
    # Build query
    query = OpportunityPattern.query
    
    if pattern_type:
        query = query.filter_by(pattern_type=pattern_type)
    if pattern_category:
        query = query.filter_by(pattern_category=pattern_category)
    if is_active is not None:
        query = query.filter_by(is_active=is_active)
    
    patterns = query.order_by(OpportunityPattern.success_rate.desc()).all()
    
    return jsonify({
        'patterns': [pattern.to_dict() for pattern in patterns],
        'summary': {
            'total_patterns': len(patterns),
            'active_patterns': len([p for p in patterns if p.is_active]),
            'pattern_types': list(set(p.pattern_type for p in patterns)),
            'pattern_categories': list(set(p.pattern_category for p in patterns))
        }
    })

@patterns_bp.route('/', methods=['POST'])
@require_auth
def create_pattern():
    """Create a new opportunity detection pattern"""
    current_user = get_current_user()
    
    pattern_data = request.get_json()
    
    pattern_id = str(uuid.uuid4())
    pattern = OpportunityPattern(
        id=pattern_id,
        pattern_name=pattern_data['pattern_name'],
        pattern_type=pattern_data['pattern_type'],
        pattern_category=pattern_data['pattern_category'],
        pattern_description=pattern_data.get('pattern_description'),
        detection_criteria=pattern_data.get('detection_criteria', {}),
        pattern_indicators=pattern_data.get('pattern_indicators', []),
        pattern_weight=pattern_data.get('pattern_weight', 1.0),
        confidence_threshold=pattern_data.get('confidence_threshold', 0.7),
        created_by=current_user['username']
    )
    
    db.session.add(pattern)
    db.session.commit()
    
    return jsonify({
        'message': 'Pattern created successfully',
        'pattern_id': pattern_id,
        'pattern': pattern.to_dict()
    }), 201

@patterns_bp.route('/<pattern_id>', methods=['GET'])
@require_auth
def get_pattern(pattern_id):
    """Get pattern details"""
    pattern = OpportunityPattern.query.get(pattern_id)
    
    if not pattern:
        return jsonify({'error': 'Pattern not found'}), 404
    
    return jsonify({
        'pattern': pattern.to_dict()
    })

@patterns_bp.route('/<pattern_id>', methods=['PUT'])
@require_auth
def update_pattern(pattern_id):
    """Update pattern"""
    pattern = OpportunityPattern.query.get(pattern_id)
    
    if not pattern:
        return jsonify({'error': 'Pattern not found'}), 404
    
    update_data = request.get_json()
    
    # Update fields
    for field in ['pattern_name', 'pattern_description', 'detection_criteria', 
                  'pattern_indicators', 'pattern_weight', 'confidence_threshold', 'is_active']:
        if field in update_data:
            setattr(pattern, field, update_data[field])
    
    pattern.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Pattern updated successfully',
        'pattern': pattern.to_dict()
    })

@patterns_bp.route('/<pattern_id>/usage', methods=['POST'])
@require_auth
def record_pattern_usage(pattern_id):
    """Record pattern usage and update effectiveness metrics"""
    pattern = OpportunityPattern.query.get(pattern_id)
    
    if not pattern:
        return jsonify({'error': 'Pattern not found'}), 404
    
    usage_data = request.get_json()
    success = usage_data.get('success', False)
    
    # Update usage statistics
    pattern.usage_count += 1
    
    if success:
        # Update success rate using exponential moving average
        alpha = 0.1  # Learning rate
        pattern.success_rate = (1 - alpha) * pattern.success_rate + alpha * 1.0
    else:
        pattern.success_rate = (1 - alpha) * pattern.success_rate + alpha * 0.0
    
    pattern.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Pattern usage recorded successfully',
        'pattern': pattern.to_dict()
    })

