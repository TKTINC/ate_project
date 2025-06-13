"""
ATE Business Intelligence Service - Domain Classifier
Business domain classification and mapping
"""

import re
from typing import Dict, List, Any
from collections import defaultdict

class DomainClassifier:
    """Classifies business domains from code analysis"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
        
        # Domain classification patterns
        self.domain_patterns = {
            'finance': {
                'keywords': ['payment', 'transaction', 'account', 'balance', 'invoice', 'billing', 'currency', 'money', 'bank', 'credit', 'debit'],
                'class_patterns': [r'.*Payment.*', r'.*Account.*', r'.*Transaction.*', r'.*Invoice.*', r'.*Billing.*'],
                'function_patterns': [r'.*pay.*', r'.*charge.*', r'.*refund.*', r'.*transfer.*', r'.*calculate.*cost.*']
            },
            'ecommerce': {
                'keywords': ['product', 'cart', 'order', 'customer', 'shipping', 'inventory', 'catalog', 'checkout', 'purchase'],
                'class_patterns': [r'.*Product.*', r'.*Cart.*', r'.*Order.*', r'.*Customer.*', r'.*Shipping.*'],
                'function_patterns': [r'.*add.*cart.*', r'.*checkout.*', r'.*ship.*', r'.*order.*']
            },
            'healthcare': {
                'keywords': ['patient', 'doctor', 'appointment', 'medical', 'diagnosis', 'treatment', 'prescription', 'hospital'],
                'class_patterns': [r'.*Patient.*', r'.*Doctor.*', r'.*Appointment.*', r'.*Medical.*'],
                'function_patterns': [r'.*schedule.*', r'.*diagnose.*', r'.*treat.*', r'.*prescribe.*']
            },
            'hr': {
                'keywords': ['employee', 'payroll', 'benefits', 'recruitment', 'performance', 'training', 'department'],
                'class_patterns': [r'.*Employee.*', r'.*Payroll.*', r'.*Benefits.*', r'.*Department.*'],
                'function_patterns': [r'.*hire.*', r'.*evaluate.*', r'.*train.*', r'.*promote.*']
            },
            'inventory': {
                'keywords': ['stock', 'warehouse', 'supplier', 'procurement', 'item', 'quantity', 'location'],
                'class_patterns': [r'.*Stock.*', r'.*Warehouse.*', r'.*Supplier.*', r'.*Item.*'],
                'function_patterns': [r'.*stock.*', r'.*reorder.*', r'.*supply.*', r'.*inventory.*']
            }
        }
    
    def classify_domains(self, codebase_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify business domains from codebase analysis"""
        try:
            domains = []
            entities = []
            
            # Extract relevant data
            parsed_files = codebase_data.get('parsed_files', [])
            
            # Analyze each domain category
            for domain_category, patterns in self.domain_patterns.items():
                domain_result = self._analyze_domain(domain_category, patterns, parsed_files)
                
                if domain_result['confidence_score'] >= self.confidence_threshold:
                    domains.append(domain_result)
                    
                    # Extract entities for this domain
                    domain_entities = self._extract_domain_entities(domain_category, patterns, parsed_files)
                    entities.extend(domain_entities)
            
            # Calculate overall confidence
            overall_confidence = sum(d['confidence_score'] for d in domains) / len(domains) if domains else 0.0
            
            return {
                'domains': domains,
                'entities': entities,
                'overall_confidence': overall_confidence,
                'summary': {
                    'domains_identified': len(domains),
                    'entities_extracted': len(entities),
                    'primary_domain': domains[0]['domain_category'] if domains else None
                }
            }
            
        except Exception as e:
            return {
                'domains': [],
                'entities': [],
                'overall_confidence': 0.0,
                'errors': [str(e)]
            }
    
    def _analyze_domain(self, domain_category: str, patterns: Dict[str, List[str]], parsed_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a specific domain category"""
        keyword_matches = 0
        class_matches = 0
        function_matches = 0
        total_elements = 0
        
        related_files = []
        related_functions = []
        related_classes = []
        domain_vocabulary = set()
        
        for file_data in parsed_files:
            file_matches = 0
            
            # Check classes
            for class_info in file_data.get('classes', []):
                total_elements += 1
                class_name = class_info.get('name', '')
                
                # Check class name patterns
                for pattern in patterns['class_patterns']:
                    if re.match(pattern, class_name, re.IGNORECASE):
                        class_matches += 1
                        file_matches += 1
                        related_classes.append({
                            'name': class_name,
                            'file': file_data.get('file_path', ''),
                            'confidence': 0.8
                        })
                        break
                
                # Check for keywords in class name
                for keyword in patterns['keywords']:
                    if keyword.lower() in class_name.lower():
                        keyword_matches += 1
                        file_matches += 1
                        domain_vocabulary.add(keyword)
            
            # Check functions
            for function_info in file_data.get('functions', []):
                total_elements += 1
                function_name = function_info.get('name', '')
                
                # Check function name patterns
                for pattern in patterns['function_patterns']:
                    if re.match(pattern, function_name, re.IGNORECASE):
                        function_matches += 1
                        file_matches += 1
                        related_functions.append({
                            'name': function_name,
                            'file': file_data.get('file_path', ''),
                            'confidence': 0.7
                        })
                        break
                
                # Check for keywords in function name
                for keyword in patterns['keywords']:
                    if keyword.lower() in function_name.lower():
                        keyword_matches += 1
                        file_matches += 1
                        domain_vocabulary.add(keyword)
            
            # If file has matches, add to related files
            if file_matches > 0:
                related_files.append({
                    'path': file_data.get('file_path', ''),
                    'matches': file_matches,
                    'confidence': min(file_matches / 5.0, 1.0)  # Normalize to 0-1
                })
        
        # Calculate confidence score
        total_matches = keyword_matches + class_matches + function_matches
        confidence_score = min(total_matches / max(total_elements * 0.1, 1), 1.0) if total_elements > 0 else 0.0
        
        # Calculate coverage percentage
        coverage_percentage = (len(related_files) / max(len(parsed_files), 1)) * 100
        
        return {
            'domain_name': f"{domain_category.title()} Domain",
            'domain_category': domain_category,
            'confidence_score': confidence_score,
            'business_entities': [],  # Will be populated separately
            'business_rules': self._extract_business_rules(domain_category, patterns),
            'domain_vocabulary': list(domain_vocabulary),
            'related_files': related_files,
            'related_functions': related_functions,
            'related_classes': related_classes,
            'complexity_score': min(total_matches / 10.0, 1.0),
            'coverage_percentage': coverage_percentage
        }
    
    def _extract_domain_entities(self, domain_category: str, patterns: Dict[str, List[str]], parsed_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract business entities for a domain"""
        entities = []
        
        # Entity extraction patterns based on domain
        entity_patterns = {
            'finance': ['Account', 'Transaction', 'Payment', 'Invoice', 'Customer'],
            'ecommerce': ['Product', 'Order', 'Customer', 'Cart', 'Category'],
            'healthcare': ['Patient', 'Doctor', 'Appointment', 'Prescription', 'Treatment'],
            'hr': ['Employee', 'Department', 'Position', 'Payroll', 'Benefits'],
            'inventory': ['Item', 'Stock', 'Warehouse', 'Supplier', 'Location']
        }
        
        target_entities = entity_patterns.get(domain_category, [])
        
        for file_data in parsed_files:
            for class_info in file_data.get('classes', []):
                class_name = class_info.get('name', '')
                
                # Check if class represents a business entity
                for entity_type in target_entities:
                    if entity_type.lower() in class_name.lower():
                        entities.append({
                            'entity_name': class_name,
                            'entity_type': entity_type.lower(),
                            'entity_category': domain_category,
                            'confidence_score': 0.8,
                            'domain_name': f"{domain_category.title()} Domain",
                            'attributes': [method.get('name', '') for method in class_info.get('methods', [])[:5]],
                            'source_files': [file_data.get('file_path', '')],
                            'source_classes': [class_name],
                            'usage_frequency': 1,
                            'complexity_score': min(len(class_info.get('methods', [])) / 10.0, 1.0),
                            'importance_score': 0.7
                        })
                        break
        
        return entities
    
    def _extract_business_rules(self, domain_category: str, patterns: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Extract business rules for a domain"""
        # Simplified business rule extraction
        rule_templates = {
            'finance': [
                {'rule': 'Payment validation required', 'type': 'validation'},
                {'rule': 'Transaction logging mandatory', 'type': 'audit'},
                {'rule': 'Balance verification before debit', 'type': 'business_logic'}
            ],
            'ecommerce': [
                {'rule': 'Inventory check before order', 'type': 'validation'},
                {'rule': 'Customer authentication required', 'type': 'security'},
                {'rule': 'Order confirmation email', 'type': 'notification'}
            ],
            'healthcare': [
                {'rule': 'Patient consent required', 'type': 'compliance'},
                {'rule': 'Medical record privacy', 'type': 'security'},
                {'rule': 'Appointment scheduling rules', 'type': 'business_logic'}
            ]
        }
        
        return rule_templates.get(domain_category, [])

