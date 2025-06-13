"""
ATE Analysis Service - Parser Factory
Factory for creating language-specific parsers
"""

import os
from typing import Dict, Optional, List

class ParserFactory:
    """Factory for creating language-specific parsers"""
    
    def __init__(self):
        self._parsers = {}
        self._initialize_parsers()
    
    def _initialize_parsers(self):
        """Initialize available parsers"""
        try:
            from .python_parser import PythonParser
            self._parsers['python'] = PythonParser
        except ImportError:
            pass
        
        try:
            from .javascript_parser import JavaScriptParser
            self._parsers['javascript'] = JavaScriptParser
            self._parsers['typescript'] = JavaScriptParser  # TypeScript uses same parser
        except ImportError:
            pass
        
        try:
            from .java_parser import JavaParser
            self._parsers['java'] = JavaParser
        except ImportError:
            pass
        
        try:
            from .generic_parser import GenericParser
            # Fallback parser for unsupported languages
            self._parsers['generic'] = GenericParser
        except ImportError:
            pass
    
    def get_parser(self, language: str):
        """Get parser instance for specified language"""
        language = language.lower()
        
        if language in self._parsers:
            return self._parsers[language]()
        
        # Try generic parser as fallback
        if 'generic' in self._parsers:
            return self._parsers['generic']()
        
        return None
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(self._parsers.keys())
    
    def get_language_details(self) -> Dict[str, Dict]:
        """Get detailed information about supported languages"""
        details = {}
        
        for language, parser_class in self._parsers.items():
            try:
                parser = parser_class()
                details[language] = {
                    'name': getattr(parser, 'language_name', language.title()),
                    'extensions': getattr(parser, 'file_extensions', []),
                    'features': getattr(parser, 'supported_features', []),
                    'version': getattr(parser, 'parser_version', '1.0.0')
                }
            except Exception:
                details[language] = {
                    'name': language.title(),
                    'extensions': [],
                    'features': [],
                    'version': 'unknown'
                }
        
        return details
    
    def is_language_supported(self, language: str) -> bool:
        """Check if language is supported"""
        return language.lower() in self._parsers

