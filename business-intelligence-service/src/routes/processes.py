"""
ATE Business Intelligence Service - Process Analysis Routes
Business process identification and workflow analysis
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from src.models.user import db, BusinessAnalysis, BusinessProcess
from src.utils.auth import require_auth, get_current_user
from src.utils.analysis_client import AnalysisClient
from src.analyzers.process_analyzer import ProcessAnalyzer

processes_bp = Blueprint('processes', __name__)

@processes_bp.route('/analyze/<analysis_id>', methods=['POST'])
@require_auth
def analyze_business_processes(analysis_id):
    """Analyze business processes in a codebase"""
    try:
        current_user = get_current_user()
        tenant_id = current_user['tenant_id']
        
        # Verify business analysis exists and belongs to tenant
        business_analysis = BusinessAnalysis.query.filter_by(
            id=analysis_id, tenant_id=tenant_id
        ).first()
        
        if not business_analysis:
            return jsonify({'error': 'Business analysis not found'}), 404
        
        # Get analysis configuration
        config = request.get_json() or {}
        process_config = {
            'confidence_threshold': config.get('confidence_threshold', 
                current_app.config['PROCESS_IDENTIFICATION_CONFIDENCE_THRESHOLD']),
            'include_subprocesses': config.get('include_subprocesses', True),
            'analyze_data_flows': config.get('analyze_data_flows', True),
            'identify_bottlenecks': config.get('identify_bottlenecks', True),
            'process_types': config.get('process_types', [])  # Empty means all types
        }
        
        # Get codebase data and domain analysis results
        analysis_client = AnalysisClient(current_app.config['ANALYSIS_SERVICE_URL'])
        codebase_data = analysis_client.get_parsing_results(business_analysis.codebase_id, current_user)
        
        if not codebase_data:
            return jsonify({'error': 'Codebase analysis not found'}), 404
        
        # Get domain analysis results for context
        domain_context = {
            'domains': [domain.to_dict() for domain in business_analysis.domains],
            'business_summary': business_analysis.business_summary
        }
        
        # Perform process analysis
        process_analyzer = ProcessAnalyzer(process_config)
        process_results = process_analyzer.analyze_processes(codebase_data, domain_context)
        
        # Store process analysis results
        processes_created = []
        for process_result in process_results['processes']:
            # Find associated domain if specified
            domain_id = None
            if process_result.get('domain_name'):
                for domain in business_analysis.domains:
                    if domain.domain_name == process_result['domain_name']:
                        domain_id = domain.id
                        break
            
            business_process = BusinessProcess(
                analysis_id=business_analysis.id,
                domain_id=domain_id,
                process_name=process_result['process_name'],
                process_type=process_result.get('process_type'),
                process_category=process_result.get('process_category'),
                confidence_score=process_result['confidence_score'],
                process_steps=process_result.get('process_steps', []),
                decision_points=process_result.get('decision_points', []),
                data_flows=process_result.get('data_flows', []),
                entry_points=process_result.get('entry_points', []),
                exit_points=process_result.get('exit_points', []),
                involved_functions=process_result.get('involved_functions', []),
                involved_classes=process_result.get('involved_classes', []),
                complexity_score=process_result.get('complexity_score', 0.0),
                estimated_duration=process_result.get('estimated_duration', 0.0),
                error_handling_score=process_result.get('error_handling_score', 0.0),
                bottlenecks=process_result.get('bottlenecks', []),
                optimization_opportunities=process_result.get('optimization_opportunities', []),
                automation_potential=process_result.get('automation_potential', 0.0),
                process_dependencies=process_result.get('process_dependencies', [])
            )
            
            db.session.add(business_process)
            processes_created.append(business_process)
        
        # Update business analysis summary
        business_analysis.business_summary.update({
            'processes_identified': len(processes_created),
            'process_analysis_confidence': process_results.get('overall_confidence', 0.0),
            'process_optimization_opportunities': len([p for p in process_results['processes'] 
                                                     if p.get('optimization_opportunities')])
        })
        
        db.session.commit()
        
        return jsonify({
            'message': 'Business process analysis completed',
            'analysis_id': business_analysis.id,
            'processes_identified': len(processes_created),
            'overall_confidence': process_results.get('overall_confidence', 0.0),
            'summary': process_results.get('summary', {})
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Process analysis failed: {str(e)}'}), 500

@processes_bp.route('/results/<analysis_id>', methods=['GET'])
@require_auth
def get_process_analysis_results(analysis_id):
    """Get business process analysis results"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    business_analysis = BusinessAnalysis.query.filter_by(
        id=analysis_id, tenant_id=tenant_id
    ).first()
    
    if not business_analysis:
        return jsonify({'error': 'Business analysis not found'}), 404
    
    processes = BusinessProcess.query.filter_by(analysis_id=analysis_id).all()
    
    return jsonify({
        'processes': [process.to_dict() for process in processes],
        'summary': {
            'total_processes': len(processes),
            'process_types': list(set(p.process_type for p in processes if p.process_type)),
            'average_complexity': sum(p.complexity_score or 0 for p in processes) / len(processes) if processes else 0,
            'automation_candidates': len([p for p in processes if (p.automation_potential or 0) > 0.7])
        }
    })

@processes_bp.route('/process/<process_id>', methods=['GET'])
@require_auth
def get_process_details(process_id):
    """Get detailed information about a specific business process"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Get process and verify access through business analysis
    business_process = db.session.query(BusinessProcess).join(BusinessAnalysis).filter(
        BusinessProcess.id == process_id,
        BusinessAnalysis.tenant_id == tenant_id
    ).first()
    
    if not business_process:
        return jsonify({'error': 'Business process not found'}), 404
    
    return jsonify({
        'process': business_process.to_dict()
    })

@processes_bp.route('/optimization/<process_id>', methods=['GET'])
@require_auth
def get_process_optimization(process_id):
    """Get optimization recommendations for a specific process"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    business_process = db.session.query(BusinessProcess).join(BusinessAnalysis).filter(
        BusinessProcess.id == process_id,
        BusinessAnalysis.tenant_id == tenant_id
    ).first()
    
    if not business_process:
        return jsonify({'error': 'Business process not found'}), 404
    
    # Generate detailed optimization recommendations
    optimization_analysis = {
        'process_id': process_id,
        'process_name': business_process.process_name,
        'current_metrics': {
            'complexity_score': business_process.complexity_score,
            'automation_potential': business_process.automation_potential,
            'error_handling_score': business_process.error_handling_score,
            'estimated_duration': business_process.estimated_duration
        },
        'bottlenecks': business_process.bottlenecks,
        'optimization_opportunities': business_process.optimization_opportunities,
        'recommendations': [
            {
                'type': 'automation',
                'priority': 'high' if (business_process.automation_potential or 0) > 0.8 else 'medium',
                'description': 'Consider automating repetitive steps in this process',
                'estimated_impact': 'high',
                'implementation_effort': 'medium'
            },
            {
                'type': 'error_handling',
                'priority': 'high' if (business_process.error_handling_score or 0) < 0.5 else 'low',
                'description': 'Improve error handling and recovery mechanisms',
                'estimated_impact': 'medium',
                'implementation_effort': 'low'
            }
        ]
    }
    
    return jsonify(optimization_analysis)

