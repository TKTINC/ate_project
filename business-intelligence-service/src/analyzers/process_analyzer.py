"""
ATE Business Intelligence Service - Process Analyzer
Business process identification and workflow analysis
"""

from typing import Dict, List, Any
import re

class ProcessAnalyzer:
    """Analyzes business processes from code structure"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.confidence_threshold = config.get('confidence_threshold', 0.6)
        
        # Process identification patterns
        self.process_patterns = {
            'workflow': {
                'keywords': ['workflow', 'process', 'step', 'stage', 'phase', 'approve', 'review'],
                'function_patterns': [r'.*process.*', r'.*workflow.*', r'.*execute.*', r'.*handle.*']
            },
            'transaction': {
                'keywords': ['transaction', 'commit', 'rollback', 'begin', 'end', 'atomic'],
                'function_patterns': [r'.*transaction.*', r'.*commit.*', r'.*rollback.*', r'.*process.*payment.*']
            },
            'batch': {
                'keywords': ['batch', 'bulk', 'mass', 'import', 'export', 'sync'],
                'function_patterns': [r'.*batch.*', r'.*bulk.*', r'.*import.*', r'.*export.*', r'.*sync.*']
            },
            'notification': {
                'keywords': ['notify', 'alert', 'email', 'message', 'send', 'notification'],
                'function_patterns': [r'.*notify.*', r'.*send.*', r'.*alert.*', r'.*email.*']
            }
        }
    
    def analyze_processes(self, codebase_data: Dict[str, Any], domain_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze business processes from codebase and domain context"""
        try:
            processes = []
            
            # Extract relevant data
            parsed_files = codebase_data.get('parsed_files', [])
            domains = domain_context.get('domains', [])
            
            # Analyze each process type
            for process_type, patterns in self.process_patterns.items():
                process_results = self._identify_processes(process_type, patterns, parsed_files, domains)
                processes.extend(process_results)
            
            # Calculate overall confidence
            overall_confidence = sum(p['confidence_score'] for p in processes) / len(processes) if processes else 0.0
            
            return {
                'processes': processes,
                'overall_confidence': overall_confidence,
                'summary': {
                    'processes_identified': len(processes),
                    'process_types': list(set(p['process_type'] for p in processes)),
                    'high_automation_potential': len([p for p in processes if p.get('automation_potential', 0) > 0.7])
                }
            }
            
        except Exception as e:
            return {
                'processes': [],
                'overall_confidence': 0.0,
                'errors': [str(e)]
            }
    
    def _identify_processes(self, process_type: str, patterns: Dict[str, List[str]], 
                          parsed_files: List[Dict[str, Any]], domains: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify processes of a specific type"""
        processes = []
        
        for file_data in parsed_files:
            # Analyze functions for process patterns
            for function_info in file_data.get('functions', []):
                function_name = function_info.get('name', '')
                
                # Check if function matches process patterns
                matches = self._check_process_patterns(function_name, patterns)
                
                if matches > 0:
                    process = self._create_process_record(
                        function_info, file_data, process_type, matches, domains
                    )
                    if process['confidence_score'] >= self.confidence_threshold:
                        processes.append(process)
        
        return processes
    
    def _check_process_patterns(self, function_name: str, patterns: Dict[str, List[str]]) -> int:
        """Check how many patterns a function matches"""
        matches = 0
        
        # Check keywords
        for keyword in patterns['keywords']:
            if keyword.lower() in function_name.lower():
                matches += 1
        
        # Check function patterns
        for pattern in patterns['function_patterns']:
            if re.match(pattern, function_name, re.IGNORECASE):
                matches += 2  # Pattern matches are weighted higher
        
        return matches
    
    def _create_process_record(self, function_info: Dict[str, Any], file_data: Dict[str, Any], 
                             process_type: str, matches: int, domains: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a process record from function analysis"""
        function_name = function_info.get('name', '')
        
        # Determine associated domain
        domain_name = self._determine_process_domain(file_data, domains)
        
        # Analyze process characteristics
        process_steps = self._extract_process_steps(function_info)
        decision_points = self._extract_decision_points(function_info)
        
        # Calculate metrics
        complexity_score = min(matches / 5.0, 1.0)
        automation_potential = self._calculate_automation_potential(function_info, process_type)
        
        return {
            'process_name': self._generate_process_name(function_name, process_type),
            'process_type': process_type,
            'process_category': self._determine_process_category(function_name, process_type),
            'confidence_score': min(matches / 3.0, 1.0),
            'domain_name': domain_name,
            'process_steps': process_steps,
            'decision_points': decision_points,
            'data_flows': self._extract_data_flows(function_info),
            'entry_points': [function_name],
            'exit_points': self._extract_exit_points(function_info),
            'involved_functions': [function_name],
            'involved_classes': [file_data.get('file_path', '').split('/')[-1].replace('.py', '')],
            'complexity_score': complexity_score,
            'estimated_duration': self._estimate_process_duration(function_info, process_type),
            'error_handling_score': self._assess_error_handling(function_info),
            'bottlenecks': self._identify_bottlenecks(function_info),
            'optimization_opportunities': self._identify_optimization_opportunities(function_info, process_type),
            'automation_potential': automation_potential,
            'process_dependencies': self._extract_process_dependencies(function_info)
        }
    
    def _determine_process_domain(self, file_data: Dict[str, Any], domains: List[Dict[str, Any]]) -> str:
        """Determine which domain a process belongs to"""
        file_path = file_data.get('file_path', '')
        
        for domain in domains:
            for related_file in domain.get('related_files', []):
                if related_file.get('path') == file_path:
                    return domain.get('domain_name', 'Unknown')
        
        return 'General'
    
    def _generate_process_name(self, function_name: str, process_type: str) -> str:
        """Generate a human-readable process name"""
        # Convert camelCase/snake_case to readable name
        readable_name = re.sub(r'([A-Z])', r' \1', function_name)
        readable_name = readable_name.replace('_', ' ').strip().title()
        
        return f"{readable_name} {process_type.title()}"
    
    def _determine_process_category(self, function_name: str, process_type: str) -> str:
        """Determine the category of the process"""
        categories = {
            'workflow': 'business_workflow',
            'transaction': 'data_transaction',
            'batch': 'data_processing',
            'notification': 'communication'
        }
        return categories.get(process_type, 'general')
    
    def _extract_process_steps(self, function_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract process steps from function analysis"""
        # Simplified step extraction based on function complexity
        complexity = function_info.get('complexity', {}).get('cyclomatic_complexity', 1)
        
        steps = []
        for i in range(min(complexity, 5)):  # Limit to 5 steps for simplicity
            steps.append({
                'step_number': i + 1,
                'step_name': f"Step {i + 1}",
                'step_type': 'processing',
                'estimated_duration': 1.0
            })
        
        return steps
    
    def _extract_decision_points(self, function_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract decision points from function analysis"""
        complexity = function_info.get('complexity', {}).get('cyclomatic_complexity', 1)
        
        decision_points = []
        if complexity > 2:
            for i in range(min(complexity - 1, 3)):  # Limit decision points
                decision_points.append({
                    'decision_id': f"decision_{i + 1}",
                    'decision_type': 'conditional',
                    'criteria': f"Business rule {i + 1}",
                    'outcomes': ['continue', 'alternative_path']
                })
        
        return decision_points
    
    def _extract_data_flows(self, function_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract data flows from function analysis"""
        # Simplified data flow extraction
        return [
            {
                'flow_id': 'input_data',
                'flow_type': 'input',
                'data_source': 'user_input',
                'data_destination': 'processing'
            },
            {
                'flow_id': 'output_data',
                'flow_type': 'output',
                'data_source': 'processing',
                'data_destination': 'result'
            }
        ]
    
    def _extract_exit_points(self, function_info: Dict[str, Any]) -> List[str]:
        """Extract process exit points"""
        return ['success', 'error']
    
    def _estimate_process_duration(self, function_info: Dict[str, Any], process_type: str) -> float:
        """Estimate process execution duration"""
        base_durations = {
            'workflow': 300.0,  # 5 minutes
            'transaction': 5.0,  # 5 seconds
            'batch': 1800.0,    # 30 minutes
            'notification': 10.0  # 10 seconds
        }
        
        base_duration = base_durations.get(process_type, 60.0)
        complexity_multiplier = function_info.get('complexity', {}).get('cyclomatic_complexity', 1)
        
        return base_duration * min(complexity_multiplier / 5.0, 3.0)
    
    def _assess_error_handling(self, function_info: Dict[str, Any]) -> float:
        """Assess the quality of error handling in the process"""
        # Simplified assessment - in real implementation, would analyze try/catch blocks
        return 0.7  # Default moderate error handling score
    
    def _identify_bottlenecks(self, function_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential bottlenecks in the process"""
        complexity = function_info.get('complexity', {}).get('cyclomatic_complexity', 1)
        
        bottlenecks = []
        if complexity > 5:
            bottlenecks.append({
                'bottleneck_type': 'complexity',
                'description': 'High cyclomatic complexity may cause performance issues',
                'severity': 'medium',
                'location': function_info.get('name', 'unknown')
            })
        
        return bottlenecks
    
    def _identify_optimization_opportunities(self, function_info: Dict[str, Any], process_type: str) -> List[Dict[str, Any]]:
        """Identify optimization opportunities"""
        opportunities = []
        
        # Check for automation opportunities
        if process_type in ['batch', 'notification']:
            opportunities.append({
                'opportunity_type': 'automation',
                'description': f'{process_type.title()} processes are good candidates for automation',
                'priority': 'high',
                'estimated_impact': 'high'
            })
        
        return opportunities
    
    def _calculate_automation_potential(self, function_info: Dict[str, Any], process_type: str) -> float:
        """Calculate automation potential for the process"""
        base_potential = {
            'workflow': 0.6,
            'transaction': 0.8,
            'batch': 0.9,
            'notification': 0.9
        }
        
        potential = base_potential.get(process_type, 0.5)
        
        # Adjust based on complexity
        complexity = function_info.get('complexity', {}).get('cyclomatic_complexity', 1)
        if complexity > 10:
            potential *= 0.7  # High complexity reduces automation potential
        
        return min(potential, 1.0)
    
    def _extract_process_dependencies(self, function_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract process dependencies"""
        # Simplified dependency extraction
        return [
            {
                'dependency_type': 'data',
                'dependency_name': 'input_validation',
                'dependency_description': 'Requires valid input data'
            }
        ]

