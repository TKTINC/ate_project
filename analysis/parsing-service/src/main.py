"""
Agent Transformation Engine - Code Parsing Service
Multi-language code parsing and semantic analysis service.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import shutil
from typing import Dict, List, Any

from parsers.python_parser import PythonParser
from parsers.javascript_parser import JavaScriptParser
from parsers.java_parser import JavaParser
from parsers.base_parser import ParserRegistry
from semantic.analyzer import SemanticAnalyzer
from utils.file_utils import FileUtils
from utils.security import SecurityValidator

app = Flask(__name__)
CORS(app)

# Initialize parsers
parser_registry = ParserRegistry()
parser_registry.register('python', PythonParser())
parser_registry.register('javascript', JavaScriptParser())
parser_registry.register('typescript', JavaScriptParser())
parser_registry.register('java', JavaParser())

# Initialize semantic analyzer
semantic_analyzer = SemanticAnalyzer()
file_utils = FileUtils()
security_validator = SecurityValidator()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for service monitoring."""
    return jsonify({
        'status': 'healthy',
        'service': 'parsing-service',
        'version': '1.0.0',
        'supported_languages': list(parser_registry.get_supported_languages())
    })

@app.route('/parse/codebase', methods=['POST'])
def parse_codebase():
    """Parse an entire codebase and extract comprehensive analysis."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('codebase_url') and not data.get('files'):
            return jsonify({'error': 'Either codebase_url or files must be provided'}), 400
        
        tenant_id = data.get('tenant_id')
        analysis_id = data.get('analysis_id')
        
        if not tenant_id or not analysis_id:
            return jsonify({'error': 'tenant_id and analysis_id are required'}), 400
        
        # Security validation
        if not security_validator.validate_tenant_access(tenant_id, request.headers.get('Authorization')):
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Create temporary workspace
        with tempfile.TemporaryDirectory() as temp_dir:
            if data.get('codebase_url'):
                # Download and extract codebase
                codebase_path = file_utils.download_codebase(data['codebase_url'], temp_dir)
            else:
                # Use provided files
                codebase_path = file_utils.create_codebase_from_files(data['files'], temp_dir)
            
            # Analyze codebase structure
            codebase_info = file_utils.analyze_codebase_structure(codebase_path)
            
            # Parse files by language
            parsing_results = {}
            for language, files in codebase_info['files_by_language'].items():
                if language in parser_registry.get_supported_languages():
                    parser = parser_registry.get_parser(language)
                    language_results = []
                    
                    for file_path in files:
                        try:
                            file_result = parser.parse_file(file_path)
                            file_result['relative_path'] = os.path.relpath(file_path, codebase_path)
                            language_results.append(file_result)
                        except Exception as e:
                            print(f"Error parsing {file_path}: {str(e)}")
                            continue
                    
                    parsing_results[language] = language_results
            
            # Perform semantic analysis
            semantic_results = semantic_analyzer.analyze_codebase(
                parsing_results, 
                codebase_info
            )
            
            # Compile comprehensive analysis results
            analysis_results = {
                'analysis_id': analysis_id,
                'tenant_id': tenant_id,
                'codebase_info': codebase_info,
                'parsing_results': parsing_results,
                'semantic_analysis': semantic_results,
                'summary': {
                    'total_files': codebase_info['total_files'],
                    'total_lines': codebase_info['total_lines'],
                    'languages_detected': list(codebase_info['files_by_language'].keys()),
                    'frameworks_detected': semantic_results.get('frameworks', []),
                    'architecture_patterns': semantic_results.get('architecture_patterns', []),
                    'complexity_score': semantic_results.get('complexity_score', 0),
                    'quality_score': semantic_results.get('quality_score', 0)
                }
            }
            
            return jsonify(analysis_results)
    
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/parse/file', methods=['POST'])
def parse_single_file():
    """Parse a single file and return detailed analysis."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['content', 'language', 'filename']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        language = data['language'].lower()
        if language not in parser_registry.get_supported_languages():
            return jsonify({'error': f'Language {language} not supported'}), 400
        
        # Security validation
        tenant_id = data.get('tenant_id')
        if tenant_id and not security_validator.validate_tenant_access(tenant_id, request.headers.get('Authorization')):
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Parse the file
        parser = parser_registry.get_parser(language)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{language}', delete=False) as temp_file:
            temp_file.write(data['content'])
            temp_file_path = temp_file.name
        
        try:
            parsing_result = parser.parse_file(temp_file_path)
            parsing_result['filename'] = data['filename']
            
            # Perform semantic analysis on single file
            semantic_result = semantic_analyzer.analyze_single_file(
                parsing_result, 
                language
            )
            
            result = {
                'parsing_result': parsing_result,
                'semantic_analysis': semantic_result,
                'summary': {
                    'language': language,
                    'lines_of_code': parsing_result.get('lines_of_code', 0),
                    'functions_count': len(parsing_result.get('functions', [])),
                    'classes_count': len(parsing_result.get('classes', [])),
                    'complexity_score': semantic_result.get('complexity_score', 0),
                    'quality_indicators': semantic_result.get('quality_indicators', {})
                }
            }
            
            return jsonify(result)
        
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    except Exception as e:
        return jsonify({'error': f'File parsing failed: {str(e)}'}), 500

@app.route('/parse/dependencies', methods=['POST'])
def analyze_dependencies():
    """Analyze dependencies for a codebase or specific files."""
    try:
        data = request.get_json()
        
        if not data.get('parsing_results'):
            return jsonify({'error': 'parsing_results are required'}), 400
        
        # Security validation
        tenant_id = data.get('tenant_id')
        if tenant_id and not security_validator.validate_tenant_access(tenant_id, request.headers.get('Authorization')):
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Analyze dependencies across all parsed files
        dependency_analysis = semantic_analyzer.analyze_dependencies(
            data['parsing_results']
        )
        
        return jsonify({
            'dependency_analysis': dependency_analysis,
            'summary': {
                'total_dependencies': len(dependency_analysis.get('external_dependencies', [])),
                'internal_dependencies': len(dependency_analysis.get('internal_dependencies', [])),
                'dependency_graph': dependency_analysis.get('dependency_graph', {}),
                'circular_dependencies': dependency_analysis.get('circular_dependencies', []),
                'security_vulnerabilities': dependency_analysis.get('security_vulnerabilities', [])
            }
        })
    
    except Exception as e:
        return jsonify({'error': f'Dependency analysis failed: {str(e)}'}), 500

@app.route('/parse/quality', methods=['POST'])
def analyze_code_quality():
    """Analyze code quality metrics for parsed codebase."""
    try:
        data = request.get_json()
        
        if not data.get('parsing_results'):
            return jsonify({'error': 'parsing_results are required'}), 400
        
        # Security validation
        tenant_id = data.get('tenant_id')
        if tenant_id and not security_validator.validate_tenant_access(tenant_id, request.headers.get('Authorization')):
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Analyze code quality
        quality_analysis = semantic_analyzer.analyze_code_quality(
            data['parsing_results']
        )
        
        return jsonify({
            'quality_analysis': quality_analysis,
            'summary': {
                'overall_quality_score': quality_analysis.get('overall_score', 0),
                'maintainability_score': quality_analysis.get('maintainability_score', 0),
                'complexity_score': quality_analysis.get('complexity_score', 0),
                'test_coverage': quality_analysis.get('test_coverage', 0),
                'code_smells': len(quality_analysis.get('code_smells', [])),
                'technical_debt_hours': quality_analysis.get('technical_debt_hours', 0)
            }
        })
    
    except Exception as e:
        return jsonify({'error': f'Quality analysis failed: {str(e)}'}), 500

@app.route('/languages', methods=['GET'])
def get_supported_languages():
    """Get list of supported programming languages."""
    return jsonify({
        'supported_languages': list(parser_registry.get_supported_languages()),
        'parser_capabilities': {
            lang: parser_registry.get_parser(lang).get_capabilities()
            for lang in parser_registry.get_supported_languages()
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=os.getenv('FLASK_ENV') == 'development')

