"""
ATE Analysis Service - Language Detection
Detect programming language from file path and content
"""

import os
import re
from typing import Optional, Dict, List

class LanguageDetector:
    """Detect programming language from file extension and content"""
    
    def __init__(self):
        self.extension_map = {
            '.py': 'python',
            '.pyw': 'python',
            '.pyi': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.c': 'c',
            '.h': 'c',
            '.cpp': 'cpp',
            '.cxx': 'cpp',
            '.cc': 'cpp',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.r': 'r',
            '.R': 'r',
            '.sql': 'sql',
            '.sh': 'shell',
            '.bash': 'shell',
            '.zsh': 'shell',
            '.ps1': 'powershell',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.xml': 'xml',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.less': 'less'
        }
        
        self.content_patterns = {
            'python': [
                r'#!/usr/bin/env python',
                r'#!/usr/bin/python',
                r'# -\*- coding: utf-8 -\*-',
                r'from\s+\w+\s+import',
                r'import\s+\w+',
                r'def\s+\w+\s*\(',
                r'class\s+\w+\s*\(',
                r'if\s+__name__\s*==\s*["\']__main__["\']'
            ],
            'javascript': [
                r'function\s+\w+\s*\(',
                r'var\s+\w+\s*=',
                r'let\s+\w+\s*=',
                r'const\s+\w+\s*=',
                r'require\s*\(',
                r'module\.exports',
                r'export\s+default',
                r'import\s+.*\s+from'
            ],
            'java': [
                r'public\s+class\s+\w+',
                r'private\s+\w+\s+\w+',
                r'public\s+static\s+void\s+main',
                r'import\s+java\.',
                r'package\s+\w+',
                r'@Override',
                r'System\.out\.println'
            ],
            'c': [
                r'#include\s*<.*>',
                r'#include\s*".*"',
                r'int\s+main\s*\(',
                r'printf\s*\(',
                r'malloc\s*\(',
                r'free\s*\('
            ],
            'cpp': [
                r'#include\s*<iostream>',
                r'#include\s*<vector>',
                r'std::',
                r'using\s+namespace\s+std',
                r'cout\s*<<',
                r'cin\s*>>',
                r'class\s+\w+\s*{'
            ]
        }
    
    def detect_language(self, file_path: str, hint: Optional[str] = None) -> str:
        """Detect language from file path and optional hint"""
        
        # If hint is provided and valid, use it
        if hint and hint.lower() in self._get_supported_languages():
            return hint.lower()
        
        # Try extension-based detection
        _, ext = os.path.splitext(file_path.lower())
        if ext in self.extension_map:
            return self.extension_map[ext]
        
        # Try filename-based detection
        filename = os.path.basename(file_path).lower()
        if filename in ['makefile', 'dockerfile', 'vagrantfile']:
            return 'makefile' if filename == 'makefile' else filename
        
        # Default to generic if no detection possible
        return 'generic'
    
    def detect_from_content(self, content: str, file_path: str = '') -> str:
        """Detect language from file content"""
        
        # First try extension-based detection
        if file_path:
            ext_detection = self.detect_language(file_path)
            if ext_detection != 'generic':
                return ext_detection
        
        # Try content-based detection
        content_lower = content.lower()
        
        for language, patterns in self.content_patterns.items():
            matches = 0
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    matches += 1
            
            # If we find multiple pattern matches, it's likely this language
            if matches >= 2:
                return language
        
        # Single pattern matches (less confident)
        for language, patterns in self.content_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    return language
        
        return 'generic'
    
    def get_language_info(self, language: str) -> Dict[str, any]:
        """Get information about a detected language"""
        language_info = {
            'python': {
                'name': 'Python',
                'category': 'interpreted',
                'paradigms': ['object-oriented', 'functional', 'procedural'],
                'typical_extensions': ['.py', '.pyw', '.pyi']
            },
            'javascript': {
                'name': 'JavaScript',
                'category': 'interpreted',
                'paradigms': ['object-oriented', 'functional', 'event-driven'],
                'typical_extensions': ['.js', '.jsx']
            },
            'typescript': {
                'name': 'TypeScript',
                'category': 'compiled',
                'paradigms': ['object-oriented', 'functional'],
                'typical_extensions': ['.ts', '.tsx']
            },
            'java': {
                'name': 'Java',
                'category': 'compiled',
                'paradigms': ['object-oriented'],
                'typical_extensions': ['.java']
            },
            'c': {
                'name': 'C',
                'category': 'compiled',
                'paradigms': ['procedural'],
                'typical_extensions': ['.c', '.h']
            },
            'cpp': {
                'name': 'C++',
                'category': 'compiled',
                'paradigms': ['object-oriented', 'procedural'],
                'typical_extensions': ['.cpp', '.cxx', '.cc', '.hpp']
            },
            'generic': {
                'name': 'Generic/Unknown',
                'category': 'unknown',
                'paradigms': ['unknown'],
                'typical_extensions': []
            }
        }
        
        return language_info.get(language, language_info['generic'])
    
    def _get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(set(self.extension_map.values()))
    
    def is_supported(self, language: str) -> bool:
        """Check if language is supported"""
        return language.lower() in self._get_supported_languages()
    
    def get_confidence_score(self, content: str, detected_language: str) -> float:
        """Get confidence score for language detection (0.0 to 1.0)"""
        if detected_language == 'generic':
            return 0.1
        
        if detected_language not in self.content_patterns:
            return 0.5  # Extension-based detection
        
        patterns = self.content_patterns[detected_language]
        matches = 0
        
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                matches += 1
        
        # Calculate confidence based on pattern matches
        confidence = min(matches / len(patterns), 1.0)
        return max(confidence, 0.1)  # Minimum 10% confidence

