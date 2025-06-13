"""
Base Parser Interface and Registry for Multi-Language Code Analysis
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import os

class BaseParser(ABC):
    """Abstract base class for language-specific parsers."""
    
    @abstractmethod
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a single file and return structured analysis results.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Dictionary containing parsing results with standardized structure
        """
        pass
    
    @abstractmethod
    def get_language(self) -> str:
        """Return the programming language this parser handles."""
        pass
    
    @abstractmethod
    def get_file_extensions(self) -> List[str]:
        """Return list of file extensions this parser can handle."""
        pass
    
    def get_capabilities(self) -> Dict[str, bool]:
        """
        Return dictionary of parser capabilities.
        
        Returns:
            Dictionary with capability flags
        """
        return {
            'syntax_analysis': True,
            'semantic_analysis': True,
            'dependency_extraction': True,
            'function_extraction': True,
            'class_extraction': True,
            'import_analysis': True,
            'complexity_metrics': True,
            'documentation_extraction': True
        }
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate if file can be parsed by this parser.
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            True if file can be parsed, False otherwise
        """
        if not os.path.exists(file_path):
            return False
        
        file_extension = os.path.splitext(file_path)[1].lower()
        return file_extension in self.get_file_extensions()
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract basic file metadata.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary containing file metadata
        """
        stat = os.stat(file_path)
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
        
        return {
            'file_path': file_path,
            'file_size': stat.st_size,
            'line_count': len(lines),
            'character_count': len(content),
            'last_modified': stat.st_mtime,
            'encoding': 'utf-8'
        }
    
    def calculate_basic_metrics(self, content: str) -> Dict[str, Any]:
        """
        Calculate basic code metrics.
        
        Args:
            content: File content as string
            
        Returns:
            Dictionary containing basic metrics
        """
        lines = content.split('\n')
        
        # Count different types of lines
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
                comment_lines += 1
            else:
                code_lines += 1
        
        return {
            'total_lines': len(lines),
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'blank_lines': blank_lines,
            'comment_ratio': comment_lines / max(code_lines, 1)
        }

class ParserRegistry:
    """Registry for managing language-specific parsers."""
    
    def __init__(self):
        self._parsers: Dict[str, BaseParser] = {}
        self._extension_map: Dict[str, str] = {}
    
    def register(self, language: str, parser: BaseParser):
        """
        Register a parser for a specific language.
        
        Args:
            language: Programming language name
            parser: Parser instance
        """
        self._parsers[language.lower()] = parser
        
        # Update extension mapping
        for ext in parser.get_file_extensions():
            self._extension_map[ext.lower()] = language.lower()
    
    def get_parser(self, language: str) -> Optional[BaseParser]:
        """
        Get parser for specified language.
        
        Args:
            language: Programming language name
            
        Returns:
            Parser instance or None if not found
        """
        return self._parsers.get(language.lower())
    
    def get_parser_by_extension(self, file_extension: str) -> Optional[BaseParser]:
        """
        Get parser based on file extension.
        
        Args:
            file_extension: File extension (e.g., '.py', '.js')
            
        Returns:
            Parser instance or None if not found
        """
        language = self._extension_map.get(file_extension.lower())
        if language:
            return self._parsers.get(language)
        return None
    
    def get_parser_by_filename(self, filename: str) -> Optional[BaseParser]:
        """
        Get parser based on filename.
        
        Args:
            filename: Name of file
            
        Returns:
            Parser instance or None if not found
        """
        _, ext = os.path.splitext(filename)
        return self.get_parser_by_extension(ext)
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported programming languages.
        
        Returns:
            List of supported language names
        """
        return list(self._parsers.keys())
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported file extensions.
        
        Returns:
            List of supported file extensions
        """
        return list(self._extension_map.keys())
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """
        Detect programming language from file path.
        
        Args:
            file_path: Path to file
            
        Returns:
            Detected language name or None
        """
        _, ext = os.path.splitext(file_path)
        return self._extension_map.get(ext.lower())

class ParseResult:
    """Standardized structure for parsing results."""
    
    def __init__(self, file_path: str, language: str):
        self.file_path = file_path
        self.language = language
        self.metadata = {}
        self.syntax_tree = {}
        self.functions = []
        self.classes = []
        self.imports = []
        self.dependencies = []
        self.metrics = {}
        self.issues = []
        self.documentation = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parse result to dictionary."""
        return {
            'file_path': self.file_path,
            'language': self.language,
            'metadata': self.metadata,
            'syntax_tree': self.syntax_tree,
            'functions': self.functions,
            'classes': self.classes,
            'imports': self.imports,
            'dependencies': self.dependencies,
            'metrics': self.metrics,
            'issues': self.issues,
            'documentation': self.documentation
        }

class FunctionInfo:
    """Information about a function or method."""
    
    def __init__(self, name: str, line_start: int, line_end: int):
        self.name = name
        self.line_start = line_start
        self.line_end = line_end
        self.parameters = []
        self.return_type = None
        self.docstring = None
        self.complexity = 0
        self.calls = []
        self.decorators = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert function info to dictionary."""
        return {
            'name': self.name,
            'line_start': self.line_start,
            'line_end': self.line_end,
            'parameters': self.parameters,
            'return_type': self.return_type,
            'docstring': self.docstring,
            'complexity': self.complexity,
            'calls': self.calls,
            'decorators': self.decorators
        }

class ClassInfo:
    """Information about a class."""
    
    def __init__(self, name: str, line_start: int, line_end: int):
        self.name = name
        self.line_start = line_start
        self.line_end = line_end
        self.base_classes = []
        self.methods = []
        self.attributes = []
        self.docstring = None
        self.decorators = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert class info to dictionary."""
        return {
            'name': self.name,
            'line_start': self.line_start,
            'line_end': self.line_end,
            'base_classes': self.base_classes,
            'methods': [method.to_dict() for method in self.methods],
            'attributes': self.attributes,
            'docstring': self.docstring,
            'decorators': self.decorators
        }

