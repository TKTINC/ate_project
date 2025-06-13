"""
Python-specific code parser implementation
"""

import ast
import os
from typing import Dict, List, Any, Optional
from .base_parser import BaseParser, ParseResult, FunctionInfo, ClassInfo

class PythonParser(BaseParser):
    """Parser for Python source code files."""
    
    def get_language(self) -> str:
        return "python"
    
    def get_file_extensions(self) -> List[str]:
        return ['.py', '.pyw', '.pyi']
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a Python file and extract comprehensive information.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Dictionary containing parsing results
        """
        if not self.validate_file(file_path):
            raise ValueError(f"Invalid Python file: {file_path}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Create parse result
        result = ParseResult(file_path, self.get_language())
        
        # Extract metadata
        result.metadata = self.extract_metadata(file_path)
        
        # Calculate basic metrics
        basic_metrics = self.calculate_basic_metrics(content)
        result.metrics.update(basic_metrics)
        
        try:
            # Parse AST
            tree = ast.parse(content, filename=file_path)
            result.syntax_tree = self._ast_to_dict(tree)
            
            # Extract detailed information
            result.functions = self._extract_functions(tree)
            result.classes = self._extract_classes(tree)
            result.imports = self._extract_imports(tree)
            result.dependencies = self._extract_dependencies(tree)
            
            # Calculate advanced metrics
            result.metrics.update(self._calculate_complexity_metrics(tree))
            
            # Extract documentation
            result.documentation = self._extract_documentation(tree, content)
            
            # Identify potential issues
            result.issues = self._identify_issues(tree, content)
            
        except SyntaxError as e:
            result.issues.append({
                'type': 'syntax_error',
                'message': str(e),
                'line': e.lineno,
                'column': e.offset
            })
        
        return result.to_dict()
    
    def _ast_to_dict(self, node: ast.AST) -> Dict[str, Any]:
        """Convert AST node to dictionary representation."""
        if isinstance(node, ast.AST):
            result = {'type': node.__class__.__name__}
            
            # Add line number information if available
            if hasattr(node, 'lineno'):
                result['lineno'] = node.lineno
            if hasattr(node, 'col_offset'):
                result['col_offset'] = node.col_offset
            
            # Process fields
            for field, value in ast.iter_fields(node):
                if isinstance(value, list):
                    result[field] = [self._ast_to_dict(item) for item in value]
                elif isinstance(value, ast.AST):
                    result[field] = self._ast_to_dict(value)
                else:
                    result[field] = value
            
            return result
        else:
            return node
    
    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract function definitions from AST."""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = FunctionInfo(
                    name=node.name,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno
                )
                
                # Extract parameters
                func_info.parameters = self._extract_function_parameters(node)
                
                # Extract return type annotation
                if node.returns:
                    func_info.return_type = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
                
                # Extract docstring
                func_info.docstring = ast.get_docstring(node)
                
                # Calculate complexity
                func_info.complexity = self._calculate_function_complexity(node)
                
                # Extract function calls
                func_info.calls = self._extract_function_calls(node)
                
                # Extract decorators
                func_info.decorators = [ast.unparse(dec) if hasattr(ast, 'unparse') else str(dec) for dec in node.decorator_list]
                
                functions.append(func_info.to_dict())
        
        return functions
    
    def _extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract class definitions from AST."""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = ClassInfo(
                    name=node.name,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno
                )
                
                # Extract base classes
                class_info.base_classes = [ast.unparse(base) if hasattr(ast, 'unparse') else str(base) for base in node.bases]
                
                # Extract methods
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_info = FunctionInfo(
                            name=item.name,
                            line_start=item.lineno,
                            line_end=item.end_lineno or item.lineno
                        )
                        method_info.parameters = self._extract_function_parameters(item)
                        method_info.docstring = ast.get_docstring(item)
                        method_info.complexity = self._calculate_function_complexity(item)
                        class_info.methods.append(method_info)
                
                # Extract class attributes
                class_info.attributes = self._extract_class_attributes(node)
                
                # Extract docstring
                class_info.docstring = ast.get_docstring(node)
                
                # Extract decorators
                class_info.decorators = [ast.unparse(dec) if hasattr(ast, 'unparse') else str(dec) for dec in node.decorator_list]
                
                classes.append(class_info.to_dict())
        
        return classes
    
    def _extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract import statements from AST."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'alias': alias.asname,
                        'line': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append({
                        'type': 'from_import',
                        'module': module,
                        'name': alias.name,
                        'alias': alias.asname,
                        'level': node.level,
                        'line': node.lineno
                    })
        
        return imports
    
    def _extract_dependencies(self, tree: ast.AST) -> List[str]:
        """Extract external dependencies from imports."""
        dependencies = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Get top-level module name
                    top_module = alias.name.split('.')[0]
                    dependencies.add(top_module)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.level == 0:  # Absolute import
                    top_module = node.module.split('.')[0]
                    dependencies.add(top_module)
        
        # Filter out standard library modules (simplified)
        stdlib_modules = {
            'os', 'sys', 'json', 'datetime', 'collections', 'itertools',
            'functools', 'operator', 'pathlib', 'typing', 'abc', 're',
            'math', 'random', 'string', 'time', 'urllib', 'http', 'email'
        }
        
        external_deps = [dep for dep in dependencies if dep not in stdlib_modules]
        return sorted(external_deps)
    
    def _extract_function_parameters(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract function parameters with type annotations."""
        parameters = []
        
        # Regular arguments
        for arg in node.args.args:
            param = {
                'name': arg.arg,
                'type': 'positional',
                'annotation': ast.unparse(arg.annotation) if arg.annotation and hasattr(ast, 'unparse') else None
            }
            parameters.append(param)
        
        # *args
        if node.args.vararg:
            param = {
                'name': node.args.vararg.arg,
                'type': 'vararg',
                'annotation': ast.unparse(node.args.vararg.annotation) if node.args.vararg.annotation and hasattr(ast, 'unparse') else None
            }
            parameters.append(param)
        
        # **kwargs
        if node.args.kwarg:
            param = {
                'name': node.args.kwarg.arg,
                'type': 'kwarg',
                'annotation': ast.unparse(node.args.kwarg.annotation) if node.args.kwarg.annotation and hasattr(ast, 'unparse') else None
            }
            parameters.append(param)
        
        return parameters
    
    def _extract_function_calls(self, node: ast.FunctionDef) -> List[str]:
        """Extract function calls within a function."""
        calls = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    if hasattr(ast, 'unparse'):
                        calls.append(ast.unparse(child.func))
        
        return list(set(calls))  # Remove duplicates
    
    def _extract_class_attributes(self, node: ast.ClassDef) -> List[str]:
        """Extract class attributes."""
        attributes = []
        
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
        
        return attributes
    
    def _calculate_complexity_metrics(self, tree: ast.AST) -> Dict[str, Any]:
        """Calculate various complexity metrics."""
        metrics = {
            'cyclomatic_complexity': 0,
            'cognitive_complexity': 0,
            'nesting_depth': 0,
            'function_count': 0,
            'class_count': 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                metrics['function_count'] += 1
                metrics['cyclomatic_complexity'] += self._calculate_function_complexity(node)
            elif isinstance(node, ast.ClassDef):
                metrics['class_count'] += 1
        
        return metrics
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _extract_documentation(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """Extract documentation and comments."""
        documentation = {
            'module_docstring': ast.get_docstring(tree),
            'comments': self._extract_comments(content),
            'docstring_coverage': 0
        }
        
        # Calculate docstring coverage
        total_functions = 0
        documented_functions = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                total_functions += 1
                if ast.get_docstring(node):
                    documented_functions += 1
        
        if total_functions > 0:
            documentation['docstring_coverage'] = documented_functions / total_functions
        
        return documentation
    
    def _extract_comments(self, content: str) -> List[Dict[str, Any]]:
        """Extract comments from source code."""
        comments = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('#'):
                comments.append({
                    'line': i,
                    'text': stripped[1:].strip(),
                    'type': 'single_line'
                })
        
        return comments
    
    def _identify_issues(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Identify potential code issues and anti-patterns."""
        issues = []
        
        # Check for long functions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    length = node.end_lineno - node.lineno
                    if length > 50:  # Arbitrary threshold
                        issues.append({
                            'type': 'long_function',
                            'message': f'Function {node.name} is {length} lines long',
                            'line': node.lineno,
                            'severity': 'warning'
                        })
        
        # Check for high complexity
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = self._calculate_function_complexity(node)
                if complexity > 10:  # Arbitrary threshold
                    issues.append({
                        'type': 'high_complexity',
                        'message': f'Function {node.name} has complexity {complexity}',
                        'line': node.lineno,
                        'severity': 'warning'
                    })
        
        return issues

