"""
ATE Architecture Design Service - Deployment Strategy Management
Integration design and deployment strategy generation routes
"""

from flask import Blueprint, request, jsonify
from src.models.user import db, DeploymentStrategy, ArchitectureDesign, ImplementationPlan
from src.utils.auth import require_auth, get_current_user, get_tenant_id
from src.analyzers.deployment_planner import DeploymentPlanner
import uuid
from datetime import datetime

deployments_bp = Blueprint('deployments', __name__)

@deployments_bp.route('/deployments', methods=['GET'])
@require_auth
def list_deployment_strategies():
    """List deployment strategies for the current tenant"""
    try:
        tenant_id = get_tenant_id()
        
        # Get query parameters
        deployment_type = request.args.get('type')
        environment_type = request.args.get('environment')
        strategy_status = request.args.get('status')
        architecture_design_id = request.args.get('design_id')
        
        # Build query
        query = DeploymentStrategy.query.filter_by(tenant_id=tenant_id)
        
        if deployment_type:
            query = query.filter_by(deployment_type=deployment_type)
        if environment_type:
            query = query.filter_by(environment_type=environment_type)
        if strategy_status:
            query = query.filter_by(strategy_status=strategy_status)
        if architecture_design_id:
            query = query.filter_by(architecture_design_id=architecture_design_id)
        
        strategies = query.order_by(DeploymentStrategy.created_at.desc()).all()
        
        return jsonify({
            'status': 'success',
            'deployment_strategies': [strategy.to_dict() for strategy in strategies],
            'total_count': len(strategies)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@deployments_bp.route('/deployments/<strategy_id>', methods=['GET'])
@require_auth
def get_deployment_strategy(strategy_id):
    """Get detailed deployment strategy information"""
    try:
        tenant_id = get_tenant_id()
        
        strategy = DeploymentStrategy.query.filter_by(
            id=strategy_id, 
            tenant_id=tenant_id
        ).first()
        
        if not strategy:
            return jsonify({'status': 'error', 'message': 'Deployment strategy not found'}), 404
        
        return jsonify({
            'status': 'success',
            'deployment_strategy': strategy.to_dict()
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@deployments_bp.route('/deployments/generate', methods=['POST'])
@require_auth
def generate_deployment_strategy():
    """Generate deployment strategy from architecture design and implementation plan"""
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
        
        # Get implementation plan if provided
        implementation_plan = None
        implementation_plan_id = data.get('implementation_plan_id')
        if implementation_plan_id:
            implementation_plan = ImplementationPlan.query.filter_by(
                id=implementation_plan_id,
                tenant_id=tenant_id
            ).first()
        
        # Generate deployment strategy
        deployment_planner = DeploymentPlanner()
        strategy_data = deployment_planner.generate_strategy(
            design=design.to_dict(),
            implementation_plan=implementation_plan.to_dict() if implementation_plan else None,
            deployment_preferences=data.get('deployment_preferences', {}),
            environment_constraints=data.get('environment_constraints', {}),
            compliance_requirements=data.get('compliance_requirements', {})
        )
        
        # Create deployment strategy record
        strategy = DeploymentStrategy(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            architecture_design_id=architecture_design_id,
            implementation_plan_id=implementation_plan_id,
            strategy_name=strategy_data['strategy_name'],
            deployment_type=strategy_data['deployment_type'],
            environment_type=strategy_data['environment_type'],
            strategy_status='draft',
            environment_design=strategy_data['environment_design'],
            infrastructure_requirements=strategy_data['infrastructure_requirements'],
            network_configuration=strategy_data['network_configuration'],
            security_configuration=strategy_data['security_configuration'],
            deployment_pipeline=strategy_data['deployment_pipeline'],
            automation_scripts=strategy_data['automation_scripts'],
            testing_strategy=strategy_data['testing_strategy'],
            rollback_procedures=strategy_data['rollback_procedures'],
            monitoring_setup=strategy_data['monitoring_setup'],
            logging_configuration=strategy_data['logging_configuration'],
            alerting_rules=strategy_data['alerting_rules'],
            backup_strategy=strategy_data['backup_strategy'],
            performance_targets=strategy_data['performance_targets'],
            scaling_configuration=strategy_data['scaling_configuration'],
            capacity_planning=strategy_data['capacity_planning'],
            load_testing_plan=strategy_data['load_testing_plan'],
            compliance_requirements=strategy_data['compliance_requirements'],
            governance_controls=strategy_data['governance_controls'],
            audit_configuration=strategy_data['audit_configuration'],
            created_by=current_user.get('username', 'system')
        )
        
        db.session.add(strategy)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Deployment strategy generated successfully',
            'strategy_id': strategy.id,
            'deployment_strategy': strategy.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@deployments_bp.route('/deployments/<strategy_id>/pipeline', methods=['POST'])
@require_auth
def generate_deployment_pipeline(strategy_id):
    """Generate detailed deployment pipeline configuration"""
    try:
        tenant_id = get_tenant_id()
        
        strategy = DeploymentStrategy.query.filter_by(
            id=strategy_id, 
            tenant_id=tenant_id
        ).first()
        
        if not strategy:
            return jsonify({'status': 'error', 'message': 'Deployment strategy not found'}), 404
        
        data = request.get_json()
        
        # Generate deployment pipeline
        deployment_planner = DeploymentPlanner()
        pipeline_config = deployment_planner.generate_pipeline(
            strategy=strategy.to_dict(),
            pipeline_type=data.get('pipeline_type', 'ci_cd'),
            automation_level=data.get('automation_level', 'full')
        )
        
        # Update strategy with pipeline configuration
        strategy.deployment_pipeline = pipeline_config['deployment_pipeline']
        strategy.automation_scripts = pipeline_config['automation_scripts']
        strategy.testing_strategy = pipeline_config['testing_strategy']
        strategy.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Deployment pipeline generated successfully',
            'pipeline_configuration': pipeline_config
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@deployments_bp.route('/deployments/<strategy_id>/monitoring', methods=['POST'])
@require_auth
def configure_monitoring(strategy_id):
    """Configure monitoring and observability for deployment"""
    try:
        tenant_id = get_tenant_id()
        
        strategy = DeploymentStrategy.query.filter_by(
            id=strategy_id, 
            tenant_id=tenant_id
        ).first()
        
        if not strategy:
            return jsonify({'status': 'error', 'message': 'Deployment strategy not found'}), 404
        
        data = request.get_json()
        
        # Configure monitoring
        deployment_planner = DeploymentPlanner()
        monitoring_config = deployment_planner.configure_monitoring(
            strategy=strategy.to_dict(),
            monitoring_requirements=data.get('monitoring_requirements', {}),
            observability_level=data.get('observability_level', 'comprehensive')
        )
        
        # Update strategy with monitoring configuration
        strategy.monitoring_setup = monitoring_config['monitoring_setup']
        strategy.logging_configuration = monitoring_config['logging_configuration']
        strategy.alerting_rules = monitoring_config['alerting_rules']
        strategy.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Monitoring configuration completed successfully',
            'monitoring_configuration': monitoring_config
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@deployments_bp.route('/deployments/<strategy_id>/security', methods=['POST'])
@require_auth
def configure_security(strategy_id):
    """Configure security controls for deployment"""
    try:
        tenant_id = get_tenant_id()
        
        strategy = DeploymentStrategy.query.filter_by(
            id=strategy_id, 
            tenant_id=tenant_id
        ).first()
        
        if not strategy:
            return jsonify({'status': 'error', 'message': 'Deployment strategy not found'}), 404
        
        data = request.get_json()
        
        # Configure security
        deployment_planner = DeploymentPlanner()
        security_config = deployment_planner.configure_security(
            strategy=strategy.to_dict(),
            security_requirements=data.get('security_requirements', {}),
            compliance_standards=data.get('compliance_standards', [])
        )
        
        # Update strategy with security configuration
        strategy.security_configuration = security_config['security_configuration']
        strategy.compliance_requirements = security_config['compliance_requirements']
        strategy.governance_controls = security_config['governance_controls']
        strategy.audit_configuration = security_config['audit_configuration']
        strategy.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Security configuration completed successfully',
            'security_configuration': security_config
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@deployments_bp.route('/deployments/<strategy_id>/capacity', methods=['POST'])
@require_auth
def plan_capacity(strategy_id):
    """Plan capacity and scaling for deployment"""
    try:
        tenant_id = get_tenant_id()
        
        strategy = DeploymentStrategy.query.filter_by(
            id=strategy_id, 
            tenant_id=tenant_id
        ).first()
        
        if not strategy:
            return jsonify({'status': 'error', 'message': 'Deployment strategy not found'}), 404
        
        data = request.get_json()
        
        # Plan capacity
        deployment_planner = DeploymentPlanner()
        capacity_plan = deployment_planner.plan_capacity(
            strategy=strategy.to_dict(),
            capacity_requirements=data.get('capacity_requirements', {}),
            scaling_preferences=data.get('scaling_preferences', {})
        )
        
        # Update strategy with capacity planning
        strategy.capacity_planning = capacity_plan['capacity_planning']
        strategy.scaling_configuration = capacity_plan['scaling_configuration']
        strategy.performance_targets = capacity_plan['performance_targets']
        strategy.load_testing_plan = capacity_plan['load_testing_plan']
        strategy.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Capacity planning completed successfully',
            'capacity_plan': capacity_plan
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@deployments_bp.route('/deployments/<strategy_id>', methods=['PUT'])
@require_auth
def update_deployment_strategy(strategy_id):
    """Update deployment strategy"""
    try:
        tenant_id = get_tenant_id()
        
        strategy = DeploymentStrategy.query.filter_by(
            id=strategy_id, 
            tenant_id=tenant_id
        ).first()
        
        if not strategy:
            return jsonify({'status': 'error', 'message': 'Deployment strategy not found'}), 404
        
        data = request.get_json()
        
        # Update strategy fields
        updatable_fields = [
            'strategy_name', 'deployment_type', 'environment_type', 'strategy_status',
            'environment_design', 'infrastructure_requirements', 'network_configuration',
            'security_configuration', 'deployment_pipeline', 'automation_scripts',
            'testing_strategy', 'rollback_procedures', 'monitoring_setup',
            'logging_configuration', 'alerting_rules', 'backup_strategy',
            'performance_targets', 'scaling_configuration', 'capacity_planning',
            'load_testing_plan', 'compliance_requirements', 'governance_controls',
            'audit_configuration'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(strategy, field, data[field])
        
        strategy.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Deployment strategy updated successfully',
            'deployment_strategy': strategy.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@deployments_bp.route('/deployments/statistics', methods=['GET'])
@require_auth
def get_deployment_statistics():
    """Get deployment statistics for the current tenant"""
    try:
        tenant_id = get_tenant_id()
        
        # Get deployment statistics
        total_strategies = DeploymentStrategy.query.filter_by(tenant_id=tenant_id).count()
        
        # Type distribution
        type_distribution = db.session.query(
            DeploymentStrategy.deployment_type,
            db.func.count(DeploymentStrategy.id)
        ).filter_by(tenant_id=tenant_id).group_by(DeploymentStrategy.deployment_type).all()
        
        # Environment distribution
        env_distribution = db.session.query(
            DeploymentStrategy.environment_type,
            db.func.count(DeploymentStrategy.id)
        ).filter_by(tenant_id=tenant_id).group_by(DeploymentStrategy.environment_type).all()
        
        # Recent strategies
        recent_strategies = DeploymentStrategy.query.filter_by(tenant_id=tenant_id).order_by(
            DeploymentStrategy.created_at.desc()
        ).limit(10).all()
        
        return jsonify({
            'status': 'success',
            'statistics': {
                'total_strategies': total_strategies,
                'type_distribution': {t[0]: t[1] for t in type_distribution},
                'environment_distribution': {e[0]: e[1] for e in env_distribution},
                'recent_strategies': [s.to_dict() for s in recent_strategies]
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

