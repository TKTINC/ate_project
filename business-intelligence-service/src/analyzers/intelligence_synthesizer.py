"""
ATE Business Intelligence Service - Intelligence Synthesizer
Business intelligence aggregation and insights generation
"""

from typing import Dict, List, Any
from collections import defaultdict

class IntelligenceSynthesizer:
    """Synthesizes comprehensive business intelligence from analysis results"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.intelligence_types = config.get('intelligence_types', [])
        self.confidence_threshold = config.get('confidence_threshold', 0.6)
    
    def synthesize_intelligence(self, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize comprehensive business intelligence"""
        try:
            intelligence = []
            
            # Generate different types of intelligence
            if 'domain_summary' in self.intelligence_types:
                domain_intelligence = self._generate_domain_summary(synthesis_data)
                intelligence.append(domain_intelligence)
            
            if 'process_optimization' in self.intelligence_types:
                process_intelligence = self._generate_process_optimization(synthesis_data)
                intelligence.append(process_intelligence)
            
            if 'risk_assessment' in self.intelligence_types:
                risk_intelligence = self._generate_risk_assessment(synthesis_data)
                intelligence.append(risk_intelligence)
            
            if 'opportunity_identification' in self.intelligence_types:
                opportunity_intelligence = self._generate_opportunity_identification(synthesis_data)
                intelligence.append(opportunity_intelligence)
            
            # Calculate overall confidence
            overall_confidence = sum(intel['confidence_score'] for intel in intelligence) / len(intelligence) if intelligence else 0.0
            
            return {
                'intelligence': intelligence,
                'overall_confidence': overall_confidence,
                'summary': {
                    'intelligence_generated': len(intelligence),
                    'high_confidence_items': len([i for i in intelligence if i['confidence_score'] > 0.8]),
                    'actionable_recommendations': sum(len(i.get('recommendations', [])) for i in intelligence)
                }
            }
            
        except Exception as e:
            return {
                'intelligence': [],
                'overall_confidence': 0.0,
                'errors': [str(e)]
            }
    
    def _generate_domain_summary(self, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate domain summary intelligence"""
        domains = synthesis_data.get('domains', [])
        business_analysis = synthesis_data.get('business_analysis', {})
        
        # Analyze domain distribution
        domain_categories = defaultdict(int)
        total_coverage = 0
        high_confidence_domains = 0
        
        for domain in domains:
            domain_categories[domain.get('domain_category', 'unknown')] += 1
            total_coverage += domain.get('coverage_percentage', 0)
            if domain.get('confidence_score', 0) > 0.8:
                high_confidence_domains += 1
        
        # Generate insights
        insights = [
            f"Identified {len(domains)} distinct business domains",
            f"Primary domain categories: {', '.join(list(domain_categories.keys())[:3])}",
            f"Average domain coverage: {total_coverage / len(domains):.1f}%" if domains else "No domains identified",
            f"High confidence domains: {high_confidence_domains}/{len(domains)}"
        ]
        
        # Generate recommendations
        recommendations = []
        if len(domains) < 2:
            recommendations.append({
                'type': 'domain_expansion',
                'priority': 'medium',
                'description': 'Consider expanding domain analysis to identify additional business areas',
                'action': 'Review codebase for additional domain-specific patterns'
            })
        
        if total_coverage / len(domains) < 50 if domains else True:
            recommendations.append({
                'type': 'coverage_improvement',
                'priority': 'high',
                'description': 'Low domain coverage indicates potential gaps in business logic identification',
                'action': 'Enhance domain classification algorithms and patterns'
            })
        
        # Identify opportunities
        opportunities = []
        for category, count in domain_categories.items():
            if count > 1:
                opportunities.append({
                    'type': 'domain_consolidation',
                    'description': f'Multiple {category} domains could be consolidated for better organization',
                    'impact': 'medium',
                    'effort': 'low'
                })
        
        return {
            'intelligence_type': 'domain_summary',
            'scope': 'global',
            'confidence_score': 0.85,
            'insights': insights,
            'recommendations': recommendations,
            'opportunities': opportunities,
            'risk_factors': [],
            'evidence': [
                f"Domain analysis of {len(domains)} domains",
                f"Coverage analysis across {len(domain_categories)} categories"
            ],
            'metrics': {
                'total_domains': len(domains),
                'domain_categories': len(domain_categories),
                'average_coverage': total_coverage / len(domains) if domains else 0,
                'high_confidence_ratio': high_confidence_domains / len(domains) if domains else 0
            },
            'business_impact': 'medium',
            'technical_impact': 'low',
            'implementation_complexity': 'low',
            'affected_stakeholders': ['business_analysts', 'architects', 'developers'],
            'required_expertise': ['business_analysis', 'domain_modeling']
        }
    
    def _generate_process_optimization(self, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate process optimization intelligence"""
        processes = synthesis_data.get('processes', [])
        
        # Analyze process characteristics
        high_complexity_processes = [p for p in processes if p.get('complexity_score', 0) > 0.7]
        automation_candidates = [p for p in processes if p.get('automation_potential', 0) > 0.7]
        bottleneck_processes = [p for p in processes if p.get('bottlenecks', [])]
        
        # Calculate metrics
        avg_complexity = sum(p.get('complexity_score', 0) for p in processes) / len(processes) if processes else 0
        avg_automation_potential = sum(p.get('automation_potential', 0) for p in processes) / len(processes) if processes else 0
        
        # Generate insights
        insights = [
            f"Analyzed {len(processes)} business processes",
            f"Average process complexity: {avg_complexity:.2f}",
            f"Automation potential: {avg_automation_potential:.2f}",
            f"High complexity processes: {len(high_complexity_processes)}",
            f"Automation candidates: {len(automation_candidates)}"
        ]
        
        # Generate recommendations
        recommendations = []
        for process in automation_candidates[:3]:  # Top 3 automation candidates
            recommendations.append({
                'type': 'process_automation',
                'priority': 'high',
                'description': f"Automate '{process['process_name']}' process",
                'action': f"Implement automation for {process['process_type']} process",
                'estimated_impact': 'high',
                'estimated_effort': 'medium'
            })
        
        for process in high_complexity_processes[:2]:  # Top 2 complex processes
            recommendations.append({
                'type': 'process_simplification',
                'priority': 'medium',
                'description': f"Simplify '{process['process_name']}' process",
                'action': 'Break down complex process into smaller, manageable steps',
                'estimated_impact': 'medium',
                'estimated_effort': 'high'
            })
        
        # Identify opportunities
        opportunities = []
        if len(automation_candidates) > 0:
            opportunities.append({
                'type': 'automation_program',
                'description': f'Implement automation program for {len(automation_candidates)} processes',
                'impact': 'high',
                'effort': 'medium',
                'estimated_savings': f'{len(automation_candidates) * 20}% efficiency improvement'
            })
        
        # Identify risks
        risk_factors = []
        if len(high_complexity_processes) > len(processes) * 0.3:
            risk_factors.append({
                'type': 'process_complexity',
                'severity': 'medium',
                'description': 'High number of complex processes may impact maintainability',
                'mitigation': 'Implement process simplification program'
            })
        
        return {
            'intelligence_type': 'process_optimization',
            'scope': 'process',
            'confidence_score': 0.8,
            'insights': insights,
            'recommendations': recommendations,
            'opportunities': opportunities,
            'risk_factors': risk_factors,
            'evidence': [
                f"Process complexity analysis of {len(processes)} processes",
                f"Automation potential assessment",
                f"Bottleneck identification in {len(bottleneck_processes)} processes"
            ],
            'metrics': {
                'total_processes': len(processes),
                'high_complexity_count': len(high_complexity_processes),
                'automation_candidates': len(automation_candidates),
                'average_complexity': avg_complexity,
                'average_automation_potential': avg_automation_potential
            },
            'business_impact': 'high',
            'technical_impact': 'medium',
            'implementation_complexity': 'medium',
            'affected_stakeholders': ['process_owners', 'operations_team', 'automation_team'],
            'required_expertise': ['process_analysis', 'automation', 'workflow_design']
        }
    
    def _generate_risk_assessment(self, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate risk assessment intelligence"""
        domains = synthesis_data.get('domains', [])
        processes = synthesis_data.get('processes', [])
        knowledge_graphs = synthesis_data.get('knowledge_graphs', [])
        
        # Identify various risk factors
        risk_factors = []
        
        # Domain-related risks
        low_confidence_domains = [d for d in domains if d.get('confidence_score', 0) < 0.6]
        if low_confidence_domains:
            risk_factors.append({
                'type': 'domain_uncertainty',
                'severity': 'medium',
                'description': f'{len(low_confidence_domains)} domains have low confidence scores',
                'impact': 'Business logic may be misunderstood or incomplete',
                'probability': 'medium',
                'mitigation': 'Conduct additional domain analysis and validation'
            })
        
        # Process-related risks
        error_prone_processes = [p for p in processes if p.get('error_handling_score', 1.0) < 0.5]
        if error_prone_processes:
            risk_factors.append({
                'type': 'process_reliability',
                'severity': 'high',
                'description': f'{len(error_prone_processes)} processes have poor error handling',
                'impact': 'System failures and data inconsistency',
                'probability': 'high',
                'mitigation': 'Implement comprehensive error handling and monitoring'
            })
        
        # Knowledge graph risks
        incomplete_graphs = [kg for kg in knowledge_graphs if kg.get('completeness_score', 0) < 0.7]
        if incomplete_graphs:
            risk_factors.append({
                'type': 'knowledge_gaps',
                'severity': 'medium',
                'description': f'{len(incomplete_graphs)} knowledge graphs are incomplete',
                'impact': 'Missing business relationships and dependencies',
                'probability': 'medium',
                'mitigation': 'Enhance knowledge extraction and validation processes'
            })
        
        # Generate insights
        insights = [
            f"Identified {len(risk_factors)} risk categories",
            f"High severity risks: {len([r for r in risk_factors if r['severity'] == 'high'])}",
            f"Medium severity risks: {len([r for r in risk_factors if r['severity'] == 'medium'])}",
            "Risk assessment covers domains, processes, and knowledge completeness"
        ]
        
        # Generate recommendations
        recommendations = []
        for risk in risk_factors:
            if risk['severity'] == 'high':
                recommendations.append({
                    'type': 'risk_mitigation',
                    'priority': 'high',
                    'description': f"Address {risk['type']} risk",
                    'action': risk['mitigation'],
                    'timeline': 'immediate'
                })
        
        # Calculate overall risk score
        risk_score = len([r for r in risk_factors if r['severity'] == 'high']) * 0.3 + \
                    len([r for r in risk_factors if r['severity'] == 'medium']) * 0.2
        risk_level = 'high' if risk_score > 0.6 else 'medium' if risk_score > 0.3 else 'low'
        
        return {
            'intelligence_type': 'risk_assessment',
            'scope': 'global',
            'confidence_score': 0.75,
            'insights': insights,
            'recommendations': recommendations,
            'opportunities': [],
            'risk_factors': risk_factors,
            'evidence': [
                f"Domain confidence analysis of {len(domains)} domains",
                f"Process reliability assessment of {len(processes)} processes",
                f"Knowledge graph completeness analysis"
            ],
            'metrics': {
                'total_risks': len(risk_factors),
                'high_severity_risks': len([r for r in risk_factors if r['severity'] == 'high']),
                'medium_severity_risks': len([r for r in risk_factors if r['severity'] == 'medium']),
                'overall_risk_score': risk_score,
                'risk_level': risk_level
            },
            'business_impact': 'high',
            'technical_impact': 'high',
            'implementation_complexity': 'medium',
            'affected_stakeholders': ['risk_management', 'operations', 'development_team'],
            'required_expertise': ['risk_analysis', 'system_architecture', 'quality_assurance']
        }
    
    def _generate_opportunity_identification(self, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate opportunity identification intelligence"""
        domains = synthesis_data.get('domains', [])
        processes = synthesis_data.get('processes', [])
        business_analysis = synthesis_data.get('business_analysis', {})
        
        # Identify various opportunities
        opportunities = []
        
        # Domain consolidation opportunities
        domain_categories = defaultdict(list)
        for domain in domains:
            domain_categories[domain.get('domain_category', 'unknown')].append(domain)
        
        for category, domain_list in domain_categories.items():
            if len(domain_list) > 1:
                opportunities.append({
                    'type': 'domain_consolidation',
                    'description': f'Consolidate {len(domain_list)} {category} domains',
                    'impact': 'medium',
                    'effort': 'low',
                    'estimated_benefit': 'Improved code organization and maintainability',
                    'timeline': '1-2 months'
                })
        
        # Automation opportunities
        automation_candidates = [p for p in processes if p.get('automation_potential', 0) > 0.8]
        if automation_candidates:
            total_automation_value = len(automation_candidates) * 25  # Estimated percentage improvement
            opportunities.append({
                'type': 'process_automation',
                'description': f'Automate {len(automation_candidates)} high-potential processes',
                'impact': 'high',
                'effort': 'medium',
                'estimated_benefit': f'{total_automation_value}% efficiency improvement',
                'timeline': '3-6 months'
            })
        
        # Modernization opportunities
        legacy_indicators = 0
        for domain in domains:
            if domain.get('complexity_score', 0) > 0.8:
                legacy_indicators += 1
        
        if legacy_indicators > len(domains) * 0.4:
            opportunities.append({
                'type': 'modernization',
                'description': 'Modernize legacy business logic components',
                'impact': 'high',
                'effort': 'high',
                'estimated_benefit': 'Improved maintainability and performance',
                'timeline': '6-12 months'
            })
        
        # Integration opportunities
        if len(domains) > 3:
            opportunities.append({
                'type': 'integration_platform',
                'description': 'Implement unified integration platform for cross-domain operations',
                'impact': 'high',
                'effort': 'high',
                'estimated_benefit': 'Reduced integration complexity and improved data flow',
                'timeline': '4-8 months'
            })
        
        # Generate insights
        insights = [
            f"Identified {len(opportunities)} strategic opportunities",
            f"High impact opportunities: {len([o for o in opportunities if o['impact'] == 'high'])}",
            f"Quick wins (low effort): {len([o for o in opportunities if o['effort'] == 'low'])}",
            "Opportunities span automation, consolidation, and modernization"
        ]
        
        # Generate recommendations
        recommendations = []
        
        # Prioritize high impact, low effort opportunities
        quick_wins = [o for o in opportunities if o['impact'] == 'high' and o['effort'] == 'low']
        for opportunity in quick_wins:
            recommendations.append({
                'type': 'quick_win',
                'priority': 'high',
                'description': f"Implement {opportunity['type']} opportunity",
                'action': opportunity['description'],
                'expected_outcome': opportunity['estimated_benefit']
            })
        
        # High impact opportunities
        high_impact = [o for o in opportunities if o['impact'] == 'high' and o['effort'] != 'low']
        for opportunity in high_impact[:2]:  # Top 2 high impact
            recommendations.append({
                'type': 'strategic_initiative',
                'priority': 'medium',
                'description': f"Plan {opportunity['type']} initiative",
                'action': opportunity['description'],
                'expected_outcome': opportunity['estimated_benefit']
            })
        
        return {
            'intelligence_type': 'opportunity_identification',
            'scope': 'global',
            'confidence_score': 0.8,
            'insights': insights,
            'recommendations': recommendations,
            'opportunities': opportunities,
            'risk_factors': [],
            'evidence': [
                f"Domain analysis of {len(domains)} domains",
                f"Process automation assessment of {len(processes)} processes",
                "Cross-domain integration analysis"
            ],
            'metrics': {
                'total_opportunities': len(opportunities),
                'high_impact_opportunities': len([o for o in opportunities if o['impact'] == 'high']),
                'quick_wins': len([o for o in opportunities if o['effort'] == 'low']),
                'automation_candidates': len([p for p in processes if p.get('automation_potential', 0) > 0.8])
            },
            'business_impact': 'high',
            'technical_impact': 'medium',
            'implementation_complexity': 'medium',
            'affected_stakeholders': ['business_owners', 'product_managers', 'development_team'],
            'required_expertise': ['business_strategy', 'process_optimization', 'system_architecture']
        }

