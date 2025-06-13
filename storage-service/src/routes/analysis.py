"""
ATE Storage Service - Analysis Management Routes
Analysis result storage and retrieval
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

from src.models.user import db, AnalysisResult, CodebaseProject
from src.utils.auth import require_auth, get_current_user

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/results', methods=['POST'])
@require_auth
def store_analysis_result():
    """Store analysis result for a project"""
    try:
        current_user = get_current_user()
        tenant_id = current_user['tenant_id']
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['project_id', 'analysis_type', 'results']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Verify project access
        project = CodebaseProject.query.filter_by(
            id=data['project_id'], tenant_id=tenant_id
        ).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Create analysis result
        analysis = AnalysisResult(
            project_id=data['project_id'],
            analysis_type=data['analysis_type'],
            analysis_version=data.get('analysis_version', '1.0'),
            status=data.get('status', 'completed'),
            results=data['results'],
            metrics=data.get('metrics', {}),
            recommendations=data.get('recommendations', []),
            processing_time_seconds=data.get('processing_time_seconds'),
            memory_usage_mb=data.get('memory_usage_mb'),
            completed_at=datetime.utcnow() if data.get('status') == 'completed' else None
        )
        
        db.session.add(analysis)
        
        # Update project last analyzed timestamp
        if data.get('status') == 'completed':
            project.last_analyzed = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Analysis result stored successfully',
            'analysis': analysis.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to store analysis result: {str(e)}'}), 500

@analysis_bp.route('/results/<analysis_id>', methods=['GET'])
@require_auth
def get_analysis_result(analysis_id):
    """Get specific analysis result"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Get analysis and verify access through project
    analysis = db.session.query(AnalysisResult).join(CodebaseProject).filter(
        AnalysisResult.id == analysis_id,
        CodebaseProject.tenant_id == tenant_id
    ).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis result not found'}), 404
    
    return jsonify({
        'analysis': analysis.to_dict()
    })

@analysis_bp.route('/results/<analysis_id>', methods=['PUT'])
@require_auth
def update_analysis_result(analysis_id):
    """Update analysis result"""
    try:
        current_user = get_current_user()
        tenant_id = current_user['tenant_id']
        
        # Get analysis and verify access through project
        analysis = db.session.query(AnalysisResult).join(CodebaseProject).filter(
            AnalysisResult.id == analysis_id,
            CodebaseProject.tenant_id == tenant_id
        ).first()
        
        if not analysis:
            return jsonify({'error': 'Analysis result not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'status' in data:
            analysis.status = data['status']
            if data['status'] == 'completed':
                analysis.completed_at = datetime.utcnow()
        
        if 'results' in data:
            analysis.results = data['results']
        
        if 'metrics' in data:
            analysis.metrics = data['metrics']
        
        if 'recommendations' in data:
            analysis.recommendations = data['recommendations']
        
        if 'processing_time_seconds' in data:
            analysis.processing_time_seconds = data['processing_time_seconds']
        
        if 'memory_usage_mb' in data:
            analysis.memory_usage_mb = data['memory_usage_mb']
        
        if 'error_message' in data:
            analysis.error_message = data['error_message']
        
        if 'error_details' in data:
            analysis.error_details = data['error_details']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Analysis result updated successfully',
            'analysis': analysis.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update analysis result: {str(e)}'}), 500

@analysis_bp.route('/results/<analysis_id>', methods=['DELETE'])
@require_auth
def delete_analysis_result(analysis_id):
    """Delete analysis result"""
    try:
        current_user = get_current_user()
        tenant_id = current_user['tenant_id']
        
        # Get analysis and verify access through project
        analysis = db.session.query(AnalysisResult).join(CodebaseProject).filter(
            AnalysisResult.id == analysis_id,
            CodebaseProject.tenant_id == tenant_id
        ).first()
        
        if not analysis:
            return jsonify({'error': 'Analysis result not found'}), 404
        
        db.session.delete(analysis)
        db.session.commit()
        
        return jsonify({
            'message': 'Analysis result deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete analysis result: {str(e)}'}), 500

@analysis_bp.route('/types', methods=['GET'])
@require_auth
def get_analysis_types():
    """Get available analysis types"""
    analysis_types = [
        {
            'type': 'parsing',
            'name': 'Code Parsing',
            'description': 'Basic code structure and syntax analysis'
        },
        {
            'type': 'dependencies',
            'name': 'Dependency Analysis',
            'description': 'Analysis of code dependencies and relationships'
        },
        {
            'type': 'quality',
            'name': 'Code Quality',
            'description': 'Code quality metrics and technical debt assessment'
        },
        {
            'type': 'architecture',
            'name': 'Architecture Analysis',
            'description': 'Architectural pattern recognition and design analysis'
        },
        {
            'type': 'business_domain',
            'name': 'Business Domain',
            'description': 'Business domain and functional area identification'
        },
        {
            'type': 'data_flow',
            'name': 'Data Flow',
            'description': 'Data flow and process mapping analysis'
        },
        {
            'type': 'opportunities',
            'name': 'Agentic Opportunities',
            'description': 'Identification of agentic transformation opportunities'
        },
        {
            'type': 'business_case',
            'name': 'Business Case',
            'description': 'Business value and ROI analysis for opportunities'
        }
    ]
    
    return jsonify({
        'analysis_types': analysis_types
    })

@analysis_bp.route('/summary/<project_id>', methods=['GET'])
@require_auth
def get_analysis_summary(project_id):
    """Get analysis summary for a project"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Verify project access
    project = CodebaseProject.query.filter_by(
        id=project_id, tenant_id=tenant_id
    ).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Get analysis summary
    analyses = AnalysisResult.query.filter_by(project_id=project_id).all()
    
    summary = {
        'project_id': project_id,
        'total_analyses': len(analyses),
        'completed_analyses': len([a for a in analyses if a.status == 'completed']),
        'failed_analyses': len([a for a in analyses if a.status == 'failed']),
        'running_analyses': len([a for a in analyses if a.status == 'running']),
        'analysis_types': {}
    }
    
    # Group by analysis type
    for analysis in analyses:
        if analysis.analysis_type not in summary['analysis_types']:
            summary['analysis_types'][analysis.analysis_type] = {
                'total': 0,
                'completed': 0,
                'failed': 0,
                'running': 0,
                'latest_result': None
            }
        
        summary['analysis_types'][analysis.analysis_type]['total'] += 1
        summary['analysis_types'][analysis.analysis_type][analysis.status] += 1
        
        # Keep track of latest result for each type
        if (analysis.status == 'completed' and 
            (summary['analysis_types'][analysis.analysis_type]['latest_result'] is None or
             analysis.completed_at > summary['analysis_types'][analysis.analysis_type]['latest_result']['completed_at'])):
            summary['analysis_types'][analysis.analysis_type]['latest_result'] = {
                'id': analysis.id,
                'completed_at': analysis.completed_at.isoformat(),
                'processing_time_seconds': analysis.processing_time_seconds,
                'has_recommendations': len(analysis.recommendations) > 0
            }
    
    return jsonify({
        'summary': summary
    })

