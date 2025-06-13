"""
ATE Opportunity Detection Service - Opportunity Detector
AI-powered opportunity detection and pattern recognition
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Any, Tuple
import re

class OpportunityDetector:
    """AI-powered opportunity detection engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
        self.max_opportunities = config.get('max_opportunities', 50)
        self.opportunity_types = config.get('opportunity_types', [
            'automation', 'modernization', 'optimization', 'integration'
        ])
        
        # Initialize detection patterns
        self.automation_patterns = self._load_automation_patterns()
        self.modernization_patterns = self._load_modernization_patterns()
        self.optimization_patterns = self._load_optimization_patterns()
        self.integration_patterns = self._load_integration_patterns()
    
    def detect_opportunities(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect transformation opportunities from business intelligence data"""
        opportunities = []
        detection_summary = {
            'total_patterns_evaluated': 0,
            'opportunities_by_type': {},
            'confidence_distribution': [],
            'processing_time': 0
        }
        
        # Extract relevant data
        domains = business_data.get('domain_analysis', {}).get('domains', [])
        processes = business_data.get('process_analysis', {}).get('processes', [])
        knowledge_graphs = business_data.get('knowledge_graphs', {})
        intelligence_summary = business_data.get('intelligence_summary', {})
        
        # Detect automation opportunities
        if 'automation' in self.opportunity_types:
            automation_opps = self._detect_automation_opportunities(domains, processes, intelligence_summary)
            opportunities.extend(automation_opps)
            detection_summary['opportunities_by_type']['automation'] = len(automation_opps)
        
        # Detect modernization opportunities
        if 'modernization' in self.opportunity_types:
            modernization_opps = self._detect_modernization_opportunities(domains, processes, intelligence_summary)
            opportunities.extend(modernization_opps)
            detection_summary['opportunities_by_type']['modernization'] = len(modernization_opps)
        
        # Detect optimization opportunities
        if 'optimization' in self.opportunity_types:
            optimization_opps = self._detect_optimization_opportunities(domains, processes, intelligence_summary)
            opportunities.extend(optimization_opps)
            detection_summary['opportunities_by_type']['optimization'] = len(optimization_opps)
        
        # Detect integration opportunities
        if 'integration' in self.opportunity_types:
            integration_opps = self._detect_integration_opportunities(domains, processes, knowledge_graphs)
            opportunities.extend(integration_opps)
            detection_summary['opportunities_by_type']['integration'] = len(integration_opps)
        
        # Filter by confidence and limit results
        filtered_opportunities = [
            opp for opp in opportunities 
            if opp['confidence_score'] >= self.confidence_threshold
        ]
        
        # Sort by opportunity score and limit
        filtered_opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        final_opportunities = filtered_opportunities[:self.max_opportunities]
        
        # Calculate overall confidence
        overall_confidence = np.mean([opp['confidence_score'] for opp in final_opportunities]) if final_opportunities else 0.0
        
        detection_summary['confidence_distribution'] = [opp['confidence_score'] for opp in final_opportunities]
        detection_summary['total_patterns_evaluated'] = len(opportunities)
        
        return {
            'opportunities': final_opportunities,
            'summary': detection_summary,
            'overall_confidence': overall_confidence,
            'total_opportunities_found': len(final_opportunities)
        }
    
    def _detect_automation_opportunities(self, domains: List[Dict], processes: List[Dict], intelligence: Dict) -> List[Dict]:
        """Detect automation opportunities"""
        opportunities = []
        
        for process in processes:
            # Check for automation patterns
            automation_score = self._calculate_automation_score(process)
            
            if automation_score > 0.5:
                opportunity = {
                    'opportunity_name': f"Automate {process.get('process_name', 'Process')}",
                    'opportunity_type': 'automation',
                    'opportunity_category': 'process',
                    'opportunity_scope': 'component',
                    'source_domain': process.get('domain'),
                    'source_processes': [process.get('process_id')],
                    'opportunity_score': min(automation_score * 100, 100),
                    'confidence_score': self._calculate_confidence(automation_score, process),
                    'priority_score': self._calculate_priority(automation_score, process),
                    'estimated_annual_value': self._estimate_automation_value(process),
                    'estimated_cost_savings': self._estimate_cost_savings(process, 'automation'),
                    'estimated_efficiency_gain': automation_score * 50,  # Up to 50% efficiency gain
                    'implementation_complexity': self._assess_automation_complexity(process),
                    'estimated_effort_months': self._estimate_automation_effort(process),
                    'estimated_cost': self._estimate_automation_cost(process),
                    'required_skills': ['process_automation', 'workflow_design', 'integration'],
                    'implementation_risk': self._assess_implementation_risk(process, 'automation'),
                    'business_risk': 'low',
                    'technical_risk': self._assess_technical_risk(process, 'automation'),
                    'opportunity_description': f"Automate the {process.get('process_name')} process to reduce manual effort and improve efficiency",
                    'current_state_analysis': {
                        'manual_steps': process.get('manual_steps', 0),
                        'automation_potential': automation_score,
                        'current_efficiency': process.get('efficiency_score', 0.5)
                    },
                    'proposed_solution': {
                        'solution_type': 'process_automation',
                        'automation_level': 'high' if automation_score > 0.8 else 'medium',
                        'technologies': ['workflow_engine', 'rpa', 'api_integration']
                    },
                    'success_metrics': [
                        'processing_time_reduction',
                        'error_rate_reduction',
                        'cost_per_transaction'
                    ]
                }
                opportunities.append(opportunity)
        
        return opportunities
    
    def _detect_modernization_opportunities(self, domains: List[Dict], processes: List[Dict], intelligence: Dict) -> List[Dict]:
        """Detect modernization opportunities"""
        opportunities = []
        
        # Look for legacy technology indicators
        for domain in domains:
            modernization_score = self._calculate_modernization_score(domain)
            
            if modernization_score > 0.6:
                opportunity = {
                    'opportunity_name': f"Modernize {domain.get('domain_name', 'Domain')} Architecture",
                    'opportunity_type': 'modernization',
                    'opportunity_category': 'architecture',
                    'opportunity_scope': 'domain',
                    'source_domain': domain.get('domain_name'),
                    'opportunity_score': min(modernization_score * 100, 100),
                    'confidence_score': self._calculate_confidence(modernization_score, domain),
                    'priority_score': self._calculate_priority(modernization_score, domain),
                    'estimated_annual_value': self._estimate_modernization_value(domain),
                    'estimated_cost_savings': self._estimate_cost_savings(domain, 'modernization'),
                    'estimated_efficiency_gain': modernization_score * 40,
                    'implementation_complexity': 'high',
                    'estimated_effort_months': self._estimate_modernization_effort(domain),
                    'estimated_cost': self._estimate_modernization_cost(domain),
                    'required_skills': ['cloud_architecture', 'microservices', 'devops'],
                    'implementation_risk': 'medium',
                    'business_risk': 'medium',
                    'technical_risk': 'high',
                    'opportunity_description': f"Modernize the {domain.get('domain_name')} domain to improve scalability and maintainability",
                    'current_state_analysis': {
                        'legacy_indicators': domain.get('legacy_indicators', []),
                        'technical_debt': domain.get('technical_debt_score', 0.5),
                        'modernization_readiness': modernization_score
                    },
                    'proposed_solution': {
                        'solution_type': 'architecture_modernization',
                        'target_architecture': 'microservices',
                        'technologies': ['containers', 'api_gateway', 'cloud_services']
                    },
                    'success_metrics': [
                        'deployment_frequency',
                        'system_reliability',
                        'development_velocity'
                    ]
                }
                opportunities.append(opportunity)
        
        return opportunities
    
    def _detect_optimization_opportunities(self, domains: List[Dict], processes: List[Dict], intelligence: Dict) -> List[Dict]:
        """Detect optimization opportunities"""
        opportunities = []
        
        for process in processes:
            optimization_score = self._calculate_optimization_score(process)
            
            if optimization_score > 0.5:
                opportunity = {
                    'opportunity_name': f"Optimize {process.get('process_name', 'Process')} Performance",
                    'opportunity_type': 'optimization',
                    'opportunity_category': 'performance',
                    'opportunity_scope': 'component',
                    'source_domain': process.get('domain'),
                    'source_processes': [process.get('process_id')],
                    'opportunity_score': min(optimization_score * 100, 100),
                    'confidence_score': self._calculate_confidence(optimization_score, process),
                    'priority_score': self._calculate_priority(optimization_score, process),
                    'estimated_annual_value': self._estimate_optimization_value(process),
                    'estimated_cost_savings': self._estimate_cost_savings(process, 'optimization'),
                    'estimated_efficiency_gain': optimization_score * 30,
                    'implementation_complexity': 'medium',
                    'estimated_effort_months': self._estimate_optimization_effort(process),
                    'estimated_cost': self._estimate_optimization_cost(process),
                    'required_skills': ['performance_tuning', 'data_analysis', 'system_optimization'],
                    'implementation_risk': 'low',
                    'business_risk': 'low',
                    'technical_risk': 'medium',
                    'opportunity_description': f"Optimize the {process.get('process_name')} process to improve performance and reduce resource consumption",
                    'current_state_analysis': {
                        'performance_bottlenecks': process.get('bottlenecks', []),
                        'resource_utilization': process.get('resource_utilization', 0.7),
                        'optimization_potential': optimization_score
                    },
                    'proposed_solution': {
                        'solution_type': 'performance_optimization',
                        'optimization_areas': ['algorithm_improvement', 'caching', 'resource_management'],
                        'technologies': ['caching_layer', 'load_balancer', 'monitoring']
                    },
                    'success_metrics': [
                        'response_time_improvement',
                        'resource_utilization_efficiency',
                        'throughput_increase'
                    ]
                }
                opportunities.append(opportunity)
        
        return opportunities
    
    def _detect_integration_opportunities(self, domains: List[Dict], processes: List[Dict], knowledge_graphs: Dict) -> List[Dict]:
        """Detect integration opportunities"""
        opportunities = []
        
        # Look for integration patterns in knowledge graphs
        entity_relationships = knowledge_graphs.get('entity_relationships', {})
        
        if entity_relationships:
            integration_score = self._calculate_integration_score(entity_relationships)
            
            if integration_score > 0.6:
                opportunity = {
                    'opportunity_name': "Implement Cross-Domain Integration Platform",
                    'opportunity_type': 'integration',
                    'opportunity_category': 'architecture',
                    'opportunity_scope': 'system',
                    'source_domain': 'cross_domain',
                    'opportunity_score': min(integration_score * 100, 100),
                    'confidence_score': self._calculate_confidence(integration_score, entity_relationships),
                    'priority_score': self._calculate_priority(integration_score, entity_relationships),
                    'estimated_annual_value': self._estimate_integration_value(entity_relationships),
                    'estimated_cost_savings': self._estimate_cost_savings(entity_relationships, 'integration'),
                    'estimated_efficiency_gain': integration_score * 35,
                    'implementation_complexity': 'high',
                    'estimated_effort_months': self._estimate_integration_effort(entity_relationships),
                    'estimated_cost': self._estimate_integration_cost(entity_relationships),
                    'required_skills': ['integration_architecture', 'api_design', 'data_modeling'],
                    'implementation_risk': 'medium',
                    'business_risk': 'medium',
                    'technical_risk': 'high',
                    'opportunity_description': "Implement a comprehensive integration platform to connect disparate systems and improve data flow",
                    'current_state_analysis': {
                        'integration_gaps': entity_relationships.get('disconnected_entities', []),
                        'data_silos': entity_relationships.get('isolated_domains', []),
                        'integration_readiness': integration_score
                    },
                    'proposed_solution': {
                        'solution_type': 'integration_platform',
                        'integration_pattern': 'api_gateway',
                        'technologies': ['api_management', 'message_queue', 'data_pipeline']
                    },
                    'success_metrics': [
                        'data_consistency',
                        'integration_latency',
                        'system_interoperability'
                    ]
                }
                opportunities.append(opportunity)
        
        return opportunities
    
    # Helper methods for scoring and estimation
    def _calculate_automation_score(self, process: Dict) -> float:
        """Calculate automation potential score"""
        score = 0.0
        
        # High repetition indicates good automation potential
        if process.get('repetitive_tasks', 0) > 5:
            score += 0.3
        
        # Manual steps that can be automated
        manual_steps = process.get('manual_steps', 0)
        total_steps = process.get('total_steps', 1)
        if manual_steps / total_steps > 0.5:
            score += 0.4
        
        # Rule-based processes are easier to automate
        if process.get('rule_based', False):
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_modernization_score(self, domain: Dict) -> float:
        """Calculate modernization potential score"""
        score = 0.0
        
        # Legacy technology indicators
        legacy_indicators = domain.get('legacy_indicators', [])
        if len(legacy_indicators) > 3:
            score += 0.4
        
        # Technical debt
        technical_debt = domain.get('technical_debt_score', 0.0)
        if technical_debt > 0.7:
            score += 0.3
        
        # Maintenance burden
        maintenance_burden = domain.get('maintenance_burden', 0.0)
        if maintenance_burden > 0.6:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_optimization_score(self, process: Dict) -> float:
        """Calculate optimization potential score"""
        score = 0.0
        
        # Performance issues
        if process.get('performance_issues', False):
            score += 0.4
        
        # Resource inefficiency
        resource_utilization = process.get('resource_utilization', 0.5)
        if resource_utilization > 0.8 or resource_utilization < 0.3:
            score += 0.3
        
        # Bottlenecks
        bottlenecks = process.get('bottlenecks', [])
        if len(bottlenecks) > 2:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_integration_score(self, relationships: Dict) -> float:
        """Calculate integration potential score"""
        score = 0.0
        
        # Disconnected entities
        disconnected = len(relationships.get('disconnected_entities', []))
        if disconnected > 5:
            score += 0.4
        
        # Data silos
        silos = len(relationships.get('isolated_domains', []))
        if silos > 2:
            score += 0.3
        
        # Integration complexity
        complexity = relationships.get('integration_complexity', 0.5)
        if complexity > 0.6:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_confidence(self, base_score: float, data: Dict) -> float:
        """Calculate confidence in opportunity detection"""
        confidence = base_score
        
        # Adjust based on data quality
        data_quality = data.get('data_quality', 0.7)
        confidence *= data_quality
        
        # Adjust based on pattern match strength
        pattern_strength = data.get('pattern_match_strength', 0.8)
        confidence *= pattern_strength
        
        return min(confidence, 1.0)
    
    def _calculate_priority(self, score: float, data: Dict) -> float:
        """Calculate opportunity priority"""
        priority = score * 100
        
        # Adjust based on business impact
        business_impact = data.get('business_impact', 0.5)
        priority *= (1 + business_impact * 0.5)
        
        return min(priority, 100.0)
    
    # Value estimation methods
    def _estimate_automation_value(self, process: Dict) -> float:
        """Estimate annual value from automation"""
        base_value = 50000  # Base automation value
        
        # Scale by process volume
        volume = process.get('transaction_volume', 1000)
        value_per_transaction = 5  # $5 savings per automated transaction
        
        return min(base_value + (volume * value_per_transaction), 500000)
    
    def _estimate_modernization_value(self, domain: Dict) -> float:
        """Estimate annual value from modernization"""
        base_value = 100000  # Base modernization value
        
        # Scale by domain size and complexity
        complexity = domain.get('complexity_score', 0.5)
        size_factor = domain.get('size_factor', 1.0)
        
        return base_value * complexity * size_factor
    
    def _estimate_optimization_value(self, process: Dict) -> float:
        """Estimate annual value from optimization"""
        base_value = 30000  # Base optimization value
        
        # Scale by performance improvement potential
        improvement_potential = process.get('improvement_potential', 0.3)
        
        return base_value * (1 + improvement_potential)
    
    def _estimate_integration_value(self, relationships: Dict) -> float:
        """Estimate annual value from integration"""
        base_value = 75000  # Base integration value
        
        # Scale by number of systems to integrate
        systems_count = len(relationships.get('systems', []))
        
        return base_value * max(systems_count / 5, 1.0)
    
    def _estimate_cost_savings(self, data: Dict, opportunity_type: str) -> float:
        """Estimate cost savings"""
        if opportunity_type == 'automation':
            return self._estimate_automation_value(data) * 0.7
        elif opportunity_type == 'modernization':
            return self._estimate_modernization_value(data) * 0.4
        elif opportunity_type == 'optimization':
            return self._estimate_optimization_value(data) * 0.8
        elif opportunity_type == 'integration':
            return self._estimate_integration_value(data) * 0.5
        
        return 0.0
    
    # Complexity and effort estimation
    def _assess_automation_complexity(self, process: Dict) -> str:
        """Assess automation implementation complexity"""
        complexity_score = process.get('complexity_score', 0.5)
        
        if complexity_score < 0.3:
            return 'low'
        elif complexity_score < 0.7:
            return 'medium'
        else:
            return 'high'
    
    def _estimate_automation_effort(self, process: Dict) -> float:
        """Estimate automation implementation effort in months"""
        base_effort = 3  # 3 months base
        complexity = process.get('complexity_score', 0.5)
        
        return base_effort * (1 + complexity)
    
    def _estimate_automation_cost(self, process: Dict) -> float:
        """Estimate automation implementation cost"""
        effort_months = self._estimate_automation_effort(process)
        cost_per_month = 15000  # $15k per month
        
        return effort_months * cost_per_month
    
    def _estimate_modernization_effort(self, domain: Dict) -> float:
        """Estimate modernization effort in months"""
        base_effort = 12  # 12 months base
        complexity = domain.get('complexity_score', 0.5)
        
        return base_effort * (1 + complexity * 2)
    
    def _estimate_modernization_cost(self, domain: Dict) -> float:
        """Estimate modernization cost"""
        effort_months = self._estimate_modernization_effort(domain)
        cost_per_month = 25000  # $25k per month
        
        return effort_months * cost_per_month
    
    def _estimate_optimization_effort(self, process: Dict) -> float:
        """Estimate optimization effort in months"""
        base_effort = 2  # 2 months base
        complexity = process.get('complexity_score', 0.5)
        
        return base_effort * (1 + complexity * 0.5)
    
    def _estimate_optimization_cost(self, process: Dict) -> float:
        """Estimate optimization cost"""
        effort_months = self._estimate_optimization_effort(process)
        cost_per_month = 12000  # $12k per month
        
        return effort_months * cost_per_month
    
    def _estimate_integration_effort(self, relationships: Dict) -> float:
        """Estimate integration effort in months"""
        base_effort = 8  # 8 months base
        systems_count = len(relationships.get('systems', []))
        
        return base_effort * max(systems_count / 3, 1.0)
    
    def _estimate_integration_cost(self, relationships: Dict) -> float:
        """Estimate integration cost"""
        effort_months = self._estimate_integration_effort(relationships)
        cost_per_month = 20000  # $20k per month
        
        return effort_months * cost_per_month
    
    # Risk assessment
    def _assess_implementation_risk(self, data: Dict, opportunity_type: str) -> str:
        """Assess implementation risk"""
        risk_factors = data.get('risk_factors', [])
        
        if len(risk_factors) < 2:
            return 'low'
        elif len(risk_factors) < 4:
            return 'medium'
        else:
            return 'high'
    
    def _assess_technical_risk(self, data: Dict, opportunity_type: str) -> str:
        """Assess technical risk"""
        technical_complexity = data.get('technical_complexity', 0.5)
        
        if technical_complexity < 0.3:
            return 'low'
        elif technical_complexity < 0.7:
            return 'medium'
        else:
            return 'high'
    
    # Pattern loading methods
    def _load_automation_patterns(self) -> List[Dict]:
        """Load automation detection patterns"""
        return [
            {
                'name': 'repetitive_manual_process',
                'indicators': ['manual_steps', 'repetitive_tasks', 'rule_based'],
                'weight': 1.0
            },
            {
                'name': 'data_entry_process',
                'indicators': ['data_input', 'form_processing', 'validation_rules'],
                'weight': 0.8
            }
        ]
    
    def _load_modernization_patterns(self) -> List[Dict]:
        """Load modernization detection patterns"""
        return [
            {
                'name': 'legacy_technology',
                'indicators': ['old_frameworks', 'deprecated_apis', 'maintenance_burden'],
                'weight': 1.0
            },
            {
                'name': 'monolithic_architecture',
                'indicators': ['tight_coupling', 'single_deployment', 'scalability_issues'],
                'weight': 0.9
            }
        ]
    
    def _load_optimization_patterns(self) -> List[Dict]:
        """Load optimization detection patterns"""
        return [
            {
                'name': 'performance_bottleneck',
                'indicators': ['slow_response', 'high_resource_usage', 'bottlenecks'],
                'weight': 1.0
            },
            {
                'name': 'inefficient_algorithm',
                'indicators': ['high_complexity', 'redundant_operations', 'poor_caching'],
                'weight': 0.8
            }
        ]
    
    def _load_integration_patterns(self) -> List[Dict]:
        """Load integration detection patterns"""
        return [
            {
                'name': 'data_silos',
                'indicators': ['isolated_systems', 'manual_data_transfer', 'inconsistent_data'],
                'weight': 1.0
            },
            {
                'name': 'point_to_point_integration',
                'indicators': ['direct_connections', 'tight_coupling', 'integration_complexity'],
                'weight': 0.9
            }
        ]

