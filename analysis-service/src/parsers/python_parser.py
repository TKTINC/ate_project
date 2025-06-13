"""
ATE Analysis Service - Python Code Parser
Advanced Python AST parsing with semantic analysis
"""

import ast
import inspect
import time
from typing import Dict, List, Any, Optional
from radon.complexity import cc_visit
from radon.metrics import mi_visit, h_visit
from lizard import analyze_file

class PythonParser:
    """Advanced Python code parser with AST and semantic analysis"""
    
    def __init__(self):
        self.language_name = "Python"
        self.file_extensions = ['.py', '.pyw', '.pyi']
        self.supported_features = [
            'ast_generation', 'semantic_analysis', 'complexity_metrics',
            'function_extraction', 'class_extraction', 'import_analysis',
            'variable_analysis', 'decorator_analysis', 'docstring_extraction'
        ]
        self.parser_version = "1.0.0"
    
    def parse_file(self, content: str, file_path: str, 
                   include_ast: bool = True, 
                   include_semantic_analysis: bool = True) -> Dict[str, Any]:
        """Parse Python file and extract comprehensive information"""
        
        start_time = time.time()
        result = {
            'language': 'python',
            'file_path': file_path,
            'parsing_timestamp': time.time(),
            'line_count': len(content.splitlines()),
            'character_count': len(content),
            'functions': [],
            'classes': [],
            'imports': [],
            'exports': [],
            'variables': [],
            'decorators': [],
            'docstrings': [],
            'complexity_metrics': {},
            'quality_metrics': {},
            'errors': [],
            'syntax_errors': []
        }
        
        try:
            # Parse AST
            tree = ast.parse(content, filename=file_path)
            
            if include_ast:
                result['ast_data'] = self._serialize_ast(tree)
            
            # Extract basic code elements
            self._extract_imports(tree, result)
            self._extract_functions(tree, result)
            self._extract_classes(tree, result)
            self._extract_variables(tree, result)
            self._extract_decorators(tree, result)
            self._extract_docstrings(tree, result)
            
            # Calculate complexity metrics
            result['complexity_metrics'] = self._calculate_complexity_metrics(content, file_path)
            
            # Calculate quality metrics
            result['quality_metrics'] = self._calculate_quality_metrics(content, tree)
            
            if include_semantic_analysis:
                result['semantic_data'] = self._perform_semantic_analysis(tree, content)
            
        except SyntaxError as e:
            result['syntax_errors'].append({
                'type': 'SyntaxError',
                'message': str(e),
                'line': e.lineno,
                'column': e.offset,
                'text': e.text
            })
        except Exception as e:
            result['errors'].append({
                'type': type(e).__name__,
                'message': str(e)
            })
        
        result['parsing_duration_ms'] = (time.time() - start_time) * 1000
        return result
    
    def _serialize_ast(self, tree: ast.AST) -> Dict[str, Any]:
        """Serialize AST to JSON-compatible format"""
        def ast_to_dict(node):
            if isinstance(node, ast.AST):
                result = {'_type': node.__class__.__name__}
                for field, value in ast.iter_fields(node):
                    if isinstance(value, list):
                        result[field] = [ast_to_dict(item) for item in value]
                    elif isinstance(value, ast.AST):
                        result[field] = ast_to_dict(value)
                    else:
                        result[field] = value
                
                # Add position information if available
                if hasattr(node, 'lineno'):
                    result['lineno'] = node.lineno
                if hasattr(node, 'col_offset'):
                    result['col_offset'] = node.col_offset
                
                return result
            else:
                return value
        
        return ast_to_dict(tree)
    
    def _extract_imports(self, tree: ast.AST, result: Dict[str, Any]):
        """Extract import statements"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result['imports'].append({
                        'type': 'import',
                        'module': alias.name,
                        'alias': alias.asname,
                        'line': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    result['imports'].append({
                        'type': 'from_import',
                        'module': module,
                        'name': alias.name,
                        'alias': alias.asname,
                        'level': node.level,
                        'line': node.lineno
                    })
    
    def _extract_functions(self, tree: ast.AST, result: Dict[str, Any]):
        """Extract function definitions"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = {
                    'name': node.name,
                    'line_start': node.lineno,
                    'line_end': getattr(node, 'end_lineno', node.lineno),
                    'is_async': isinstance(node, ast.AsyncFunctionDef),
                    'is_method': self._is_method(node),
                    'arguments': self._extract_function_args(node),
                    'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
                    'returns': self._get_annotation_string(node.returns) if node.returns else None,
                    'docstring': ast.get_docstring(node),
                    'complexity': self._calculate_function_complexity(node)
                }
                result['functions'].append(func_info)
    
    def _extract_classes(self, tree: ast.AST, result: Dict[str, Any]):
        """Extract class definitions"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'line_start': node.lineno,
                    'line_end': getattr(node, 'end_lineno', node.lineno),
                    'bases': [self._get_name_string(base) for base in node.bases],
                    'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
                    'methods': self._extract_class_methods(node),
                    'attributes': self._extract_class_attributes(node),
                    'docstring': ast.get_docstring(node),
                    'is_abstract': self._is_abstract_class(node)
                }
                result['classes'].append(class_info)
    
    def _extract_variables(self, tree: ast.AST, result: Dict[str, Any]):
        """Extract variable assignments"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        result['variables'].append({
                            'name': target.id,
                            'line': node.lineno,
                            'type': 'assignment',
                            'annotation': None
                        })
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                result['variables'].append({
                    'name': node.target.id,
                    'line': node.lineno,
                    'type': 'annotated_assignment',
                    'annotation': self._get_annotation_string(node.annotation)
                })
    
    def _extract_decorators(self, tree: ast.AST, result: Dict[str, Any]):
        """Extract decorator usage"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                for decorator in node.decorator_list:
                    result['decorators'].append({
                        'name': self._get_decorator_name(decorator),
                        'target': node.name,
                        'target_type': 'function' if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else 'class',
                        'line': decorator.lineno
                    })
    
    def _extract_docstrings(self, tree: ast.AST, result: Dict[str, Any]):
        """Extract docstrings from modules, classes, and functions"""
        # Module docstring
        module_docstring = ast.get_docstring(tree)
        if module_docstring:
            result['docstrings'].append({
                'type': 'module',
                'content': module_docstring,
                'line': 1
            })
        
        # Function and class docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                docstring = ast.get_docstring(node)
                if docstring:
                    result['docstrings'].append({
                        'type': 'function' if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else 'class',
                        'name': node.name,
                        'content': docstring,
                        'line': node.lineno
                    })
    
    def _calculate_complexity_metrics(self, content: str, file_path: str) -> Dict[str, Any]:
        """Calculate various complexity metrics"""
        metrics = {}
        
        try:
            # Cyclomatic complexity using radon
            cc_results = cc_visit(content)
            metrics['cyclomatic_complexity'] = {
                'average': sum(result.complexity for result in cc_results) / len(cc_results) if cc_results else 0,
                'max': max(result.complexity for result in cc_results) if cc_results else 0,
                'functions': [
                    {
                        'name': result.name,
                        'complexity': result.complexity,
                        'line': result.lineno
                    } for result in cc_results
                ]
            }
            
            # Maintainability index using radon
            mi_results = mi_visit(content, multi=True)
            if mi_results:
                metrics['maintainability_index'] = mi_results
            
            # Halstead metrics using radon
            h_results = h_visit(content)
            if h_results:
                metrics['halstead_metrics'] = {
                    'vocabulary': h_results.vocabulary,
                    'length': h_results.length,
                    'calculated_length': h_results.calculated_length,
                    'volume': h_results.volume,
                    'difficulty': h_results.difficulty,
                    'effort': h_results.effort,
                    'time': h_results.time,
                    'bugs': h_results.bugs
                }
            
            # Lizard metrics for additional complexity analysis
            try:
                with open('/tmp/temp_analysis.py', 'w') as f:
                    f.write(content)
                
                lizard_results = analyze_file('/tmp/temp_analysis.py')
                metrics['lizard_metrics'] = {
                    'nloc': lizard_results.nloc,
                    'average_nloc': lizard_results.average_nloc,
                    'average_ccn': lizard_results.average_ccn,
                    'average_token': lizard_results.average_token,
                    'function_count': len(lizard_results.function_list)
                }
                
                import os
                os.remove('/tmp/temp_analysis.py')
                
            except Exception:
                pass  # Lizard analysis failed, continue without it
            
        except Exception as e:
            metrics['error'] = str(e)
        
        return metrics
    
    def _calculate_quality_metrics(self, content: str, tree: ast.AST) -> Dict[str, Any]:
        """Calculate code quality metrics"""
        metrics = {
            'lines_of_code': len(content.splitlines()),
            'blank_lines': len([line for line in content.splitlines() if not line.strip()]),
            'comment_lines': len([line for line in content.splitlines() if line.strip().startswith('#')]),
            'docstring_coverage': 0,
            'function_count': 0,
            'class_count': 0,
            'average_function_length': 0
        }
        
        functions = []
        classes = []
        documented_items = 0
        total_documentable_items = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node)
                total_documentable_items += 1
                if ast.get_docstring(node):
                    documented_items += 1
            elif isinstance(node, ast.ClassDef):
                classes.append(node)
                total_documentable_items += 1
                if ast.get_docstring(node):
                    documented_items += 1
        
        metrics['function_count'] = len(functions)
        metrics['class_count'] = len(classes)
        
        if functions:
            total_function_lines = sum(
                getattr(func, 'end_lineno', func.lineno) - func.lineno + 1 
                for func in functions
            )
            metrics['average_function_length'] = total_function_lines / len(functions)
        
        if total_documentable_items > 0:
            metrics['docstring_coverage'] = (documented_items / total_documentable_items) * 100
        
        return metrics
    
    def _perform_semantic_analysis(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """Perform semantic analysis on the AST"""
        semantic_data = {
            'symbol_table': {},
            'call_graph': [],
            'data_flow': [],
            'scope_analysis': {},
            'type_inference': {}
        }
        
        # Build symbol table
        semantic_data['symbol_table'] = self._build_symbol_table(tree)
        
        # Analyze function calls
        semantic_data['call_graph'] = self._analyze_function_calls(tree)
        
        # Analyze variable usage and data flow
        semantic_data['data_flow'] = self._analyze_data_flow(tree)
        
        return semantic_data
    
    def _build_symbol_table(self, tree: ast.AST) -> Dict[str, Any]:
        """Build symbol table for the module"""
        symbols = {
            'functions': {},
            'classes': {},
            'variables': {},
            'imports': {}
        }
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                symbols['functions'][node.name] = {
                    'line': node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'is_async': isinstance(node, ast.AsyncFunctionDef)
                }
            elif isinstance(node, ast.ClassDef):
                symbols['classes'][node.name] = {
                    'line': node.lineno,
                    'bases': [self._get_name_string(base) for base in node.bases]
                }
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        symbols['variables'][target.id] = {
                            'line': node.lineno,
                            'type': 'assignment'
                        }
        
        return symbols
    
    def _analyze_function_calls(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Analyze function calls in the code"""
        calls = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_info = {
                    'line': node.lineno,
                    'function': self._get_call_name(node.func),
                    'args_count': len(node.args),
                    'kwargs_count': len(node.keywords)
                }
                calls.append(call_info)
        
        return calls
    
    def _analyze_data_flow(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Analyze data flow in the code"""
        data_flow = []
        
        # This is a simplified data flow analysis
        # In a full implementation, this would track variable assignments and usage
        
        return data_flow
    
    # Helper methods
    def _is_method(self, node: ast.FunctionDef) -> bool:
        """Check if function is a method (inside a class)"""
        # This is a simplified check - in practice, you'd need to track the AST context
        return len(node.args.args) > 0 and node.args.args[0].arg in ['self', 'cls']
    
    def _extract_function_args(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract function arguments with type annotations"""
        args = []
        
        for arg in node.args.args:
            arg_info = {
                'name': arg.arg,
                'annotation': self._get_annotation_string(arg.annotation) if arg.annotation else None,
                'default': None
            }
            args.append(arg_info)
        
        # Add defaults
        defaults = node.args.defaults
        if defaults:
            for i, default in enumerate(defaults):
                arg_index = len(args) - len(defaults) + i
                if arg_index >= 0:
                    args[arg_index]['default'] = self._get_value_string(default)
        
        return args
    
    def _extract_class_methods(self, class_node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Extract methods from a class"""
        methods = []
        
        for node in class_node.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = {
                    'name': node.name,
                    'line': node.lineno,
                    'is_async': isinstance(node, ast.AsyncFunctionDef),
                    'is_static': any(self._get_decorator_name(d) == 'staticmethod' for d in node.decorator_list),
                    'is_class_method': any(self._get_decorator_name(d) == 'classmethod' for d in node.decorator_list),
                    'is_property': any(self._get_decorator_name(d) == 'property' for d in node.decorator_list)
                }
                methods.append(method_info)
        
        return methods
    
    def _extract_class_attributes(self, class_node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Extract class attributes"""
        attributes = []
        
        for node in class_node.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        attributes.append({
                            'name': target.id,
                            'line': node.lineno,
                            'type': 'class_variable'
                        })
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                attributes.append({
                    'name': node.target.id,
                    'line': node.lineno,
                    'type': 'annotated_class_variable',
                    'annotation': self._get_annotation_string(node.annotation)
                })
        
        return attributes
    
    def _is_abstract_class(self, class_node: ast.ClassDef) -> bool:
        """Check if class is abstract"""
        # Check for ABC inheritance or abstractmethod decorators
        for base in class_node.bases:
            if self._get_name_string(base) in ['ABC', 'abc.ABC']:
                return True
        
        for node in class_node.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for decorator in node.decorator_list:
                    if self._get_decorator_name(decorator) in ['abstractmethod', 'abc.abstractmethod']:
                        return True
        
        return False
    
    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a single function"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Get decorator name as string"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{self._get_name_string(decorator.value)}.{decorator.attr}"
        elif isinstance(decorator, ast.Call):
            return self._get_name_string(decorator.func)
        else:
            return str(decorator)
    
    def _get_annotation_string(self, annotation: ast.expr) -> str:
        """Get type annotation as string"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Attribute):
            return f"{self._get_name_string(annotation.value)}.{annotation.attr}"
        elif isinstance(annotation, ast.Constant):
            return repr(annotation.value)
        else:
            return str(annotation)
    
    def _get_name_string(self, node: ast.expr) -> str:
        """Get name from AST node as string"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name_string(node.value)}.{node.attr}"
        else:
            return str(node)
    
    def _get_value_string(self, node: ast.expr) -> str:
        """Get value from AST node as string"""
        if isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        else:
            return str(node)
    
    def _get_call_name(self, node: ast.expr) -> str:
        """Get function call name as string"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name_string(node.value)}.{node.attr}"
        else:
            return str(node)

