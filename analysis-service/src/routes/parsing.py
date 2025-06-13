"""
ATE Analysis Service - Multi-Language Code Parsing Routes
Comprehensive code parsing with AST generation and semantic analysis
"""

import os
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from src.models.user import db, ParsedCodebase, ParsedFile
from src.utils.auth import require_auth, get_current_user
from src.utils.storage_client import StorageClient
from src.parsers.parser_factory import ParserFactory
from src.parsers.language_detector import LanguageDetector

parsing_bp = Blueprint('parsing', __name__)

@parsing_bp.route('/project/<project_id>', methods=['POST'])
@require_auth
def parse_project(project_id):
    """Parse entire project codebase"""
    try:
        current_user = get_current_user()
        tenant_id = current_user['tenant_id']
        
        # Get parsing configuration
        config = request.get_json() or {}
        parsing_config = {
            'include_ast': config.get('include_ast', True),
            'include_semantic_analysis': config.get('include_semantic_analysis', True),
            'languages': config.get('languages', []),  # Empty means all supported
            'exclude_patterns': config.get('exclude_patterns', [
                '*.min.js', '*.bundle.js', 'node_modules/*', '__pycache__/*',
                '*.pyc', '*.class', 'target/*', 'build/*', 'dist/*'
            ]),
            'max_file_size_mb': config.get('max_file_size_mb', current_app.config['MAX_FILE_SIZE_MB'])
        }
        
        # Check if project already being parsed
        existing_parse = ParsedCodebase.query.filter_by(
            project_id=project_id,
            tenant_id=tenant_id,
            parsing_status='parsing'
        ).first()
        
        if existing_parse:
            return jsonify({
                'error': 'Project is already being parsed',
                'existing_parse_id': existing_parse.id
            }), 409
        
        # Get project files from storage service
        storage_client = StorageClient(current_app.config['STORAGE_SERVICE_URL'])
        project_files = storage_client.get_project_files(project_id, current_user)
        
        if not project_files:
            return jsonify({'error': 'No files found in project or access denied'}), 404
        
        # Create parsed codebase record
        parsed_codebase = ParsedCodebase(
            project_id=project_id,
            tenant_id=tenant_id,
            parsing_status='parsing',
            total_files=len(project_files),
            parsing_config=parsing_config
        )
        
        db.session.add(parsed_codebase)
        db.session.commit()
        
        # Start parsing process
        if current_app.config['ENABLE_PARALLEL_PARSING']:
            parsing_results = _parse_files_parallel(
                project_files, parsed_codebase, parsing_config, current_user
            )
        else:
            parsing_results = _parse_files_sequential(
                project_files, parsed_codebase, parsing_config, current_user
            )
        
        # Update codebase with results
        parsed_codebase.parsing_status = 'completed'
        parsed_codebase.parsing_completed_at = datetime.utcnow()
        parsed_codebase.parsing_duration_seconds = (
            parsed_codebase.parsing_completed_at - parsed_codebase.parsing_started_at
        ).total_seconds()
        parsed_codebase.parsed_files = parsing_results['parsed_count']
        parsed_codebase.failed_files = parsing_results['failed_count']
        parsed_codebase.total_lines_of_code = parsing_results['total_lines']
        parsed_codebase.language_distribution = parsing_results['language_distribution']
        parsed_codebase.parsing_errors = parsing_results['errors']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Project parsing completed',
            'parsed_codebase': parsed_codebase.to_dict(),
            'parsing_results': parsing_results
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Parsing failed: {str(e)}'}), 500

def _parse_files_parallel(project_files, parsed_codebase, parsing_config, current_user):
    """Parse files in parallel using ThreadPoolExecutor"""
    parsing_results = {
        'parsed_count': 0,
        'failed_count': 0,
        'total_lines': 0,
        'language_distribution': {},
        'errors': []
    }
    
    max_workers = current_app.config['MAX_PARALLEL_WORKERS']
    storage_client = StorageClient(current_app.config['STORAGE_SERVICE_URL'])
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit parsing tasks
        future_to_file = {
            executor.submit(
                _parse_single_file, 
                file_info, parsed_codebase, parsing_config, storage_client, current_user
            ): file_info for file_info in project_files
        }
        
        # Collect results
        for future in as_completed(future_to_file):
            file_info = future_to_file[future]
            try:
                result = future.result()
                if result['success']:
                    parsing_results['parsed_count'] += 1
                    parsing_results['total_lines'] += result.get('line_count', 0)
                    
                    language = result.get('language', 'unknown')
                    parsing_results['language_distribution'][language] = (
                        parsing_results['language_distribution'].get(language, 0) + 1
                    )
                else:
                    parsing_results['failed_count'] += 1
                    parsing_results['errors'].append({
                        'file_path': file_info['file_path'],
                        'error': result['error']
                    })
                    
            except Exception as e:
                parsing_results['failed_count'] += 1
                parsing_results['errors'].append({
                    'file_path': file_info['file_path'],
                    'error': f'Parsing exception: {str(e)}'
                })
    
    return parsing_results

def _parse_files_sequential(project_files, parsed_codebase, parsing_config, current_user):
    """Parse files sequentially"""
    parsing_results = {
        'parsed_count': 0,
        'failed_count': 0,
        'total_lines': 0,
        'language_distribution': {},
        'errors': []
    }
    
    storage_client = StorageClient(current_app.config['STORAGE_SERVICE_URL'])
    
    for file_info in project_files:
        try:
            result = _parse_single_file(
                file_info, parsed_codebase, parsing_config, storage_client, current_user
            )
            
            if result['success']:
                parsing_results['parsed_count'] += 1
                parsing_results['total_lines'] += result.get('line_count', 0)
                
                language = result.get('language', 'unknown')
                parsing_results['language_distribution'][language] = (
                    parsing_results['language_distribution'].get(language, 0) + 1
                )
            else:
                parsing_results['failed_count'] += 1
                parsing_results['errors'].append({
                    'file_path': file_info['file_path'],
                    'error': result['error']
                })
                
        except Exception as e:
            parsing_results['failed_count'] += 1
            parsing_results['errors'].append({
                'file_path': file_info['file_path'],
                'error': f'Parsing exception: {str(e)}'
            })
    
    return parsing_results

def _parse_single_file(file_info, parsed_codebase, parsing_config, storage_client, current_user):
    """Parse a single file and store results"""
    start_time = time.time()
    
    try:
        # Check file size
        file_size_mb = file_info.get('file_size_bytes', 0) / (1024 * 1024)
        if file_size_mb > parsing_config['max_file_size_mb']:
            return {
                'success': False,
                'error': f'File too large: {file_size_mb:.2f}MB > {parsing_config["max_file_size_mb"]}MB'
            }
        
        # Check exclude patterns
        file_path = file_info['file_path']
        for pattern in parsing_config['exclude_patterns']:
            if _matches_pattern(file_path, pattern):
                return {
                    'success': False,
                    'error': f'File excluded by pattern: {pattern}'
                }
        
        # Detect language
        language_detector = LanguageDetector()
        detected_language = language_detector.detect_language(file_path, file_info.get('language'))
        
        # Check if language is supported and requested
        if parsing_config['languages'] and detected_language not in parsing_config['languages']:
            return {
                'success': False,
                'error': f'Language not requested: {detected_language}'
            }
        
        # Download file content
        file_content = storage_client.download_file(
            parsed_codebase.project_id, file_info['id'], current_user
        )
        
        if not file_content:
            return {
                'success': False,
                'error': 'Failed to download file content'
            }
        
        # Get appropriate parser
        parser_factory = ParserFactory()
        parser = parser_factory.get_parser(detected_language)
        
        if not parser:
            return {
                'success': False,
                'error': f'No parser available for language: {detected_language}'
            }
        
        # Parse file
        parsing_result = parser.parse_file(
            file_content, 
            file_path,
            include_ast=parsing_config['include_ast'],
            include_semantic_analysis=parsing_config['include_semantic_analysis']
        )
        
        # Create parsed file record
        parsed_file = ParsedFile(
            codebase_id=parsed_codebase.id,
            file_id=file_info['id'],
            file_path=file_path,
            file_name=file_info['file_name'],
            language=detected_language,
            file_size_bytes=file_info.get('file_size_bytes', 0),
            line_count=parsing_result.get('line_count', 0),
            parsing_status='completed',
            parsing_duration_ms=(time.time() - start_time) * 1000,
            ast_data=parsing_result.get('ast_data') if parsing_config['include_ast'] else None,
            semantic_data=parsing_result.get('semantic_data') if parsing_config['include_semantic_analysis'] else None,
            functions=parsing_result.get('functions', []),
            classes=parsing_result.get('classes', []),
            imports=parsing_result.get('imports', []),
            exports=parsing_result.get('exports', []),
            variables=parsing_result.get('variables', []),
            complexity_metrics=parsing_result.get('complexity_metrics', {}),
            quality_metrics=parsing_result.get('quality_metrics', {}),
            parsing_errors=parsing_result.get('errors', []),
            syntax_errors=parsing_result.get('syntax_errors', [])
        )
        
        db.session.add(parsed_file)
        db.session.commit()
        
        return {
            'success': True,
            'language': detected_language,
            'line_count': parsing_result.get('line_count', 0),
            'parsed_file_id': parsed_file.id
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def _matches_pattern(file_path, pattern):
    """Check if file path matches exclude pattern"""
    import fnmatch
    return fnmatch.fnmatch(file_path, pattern)

@parsing_bp.route('/status/<codebase_id>', methods=['GET'])
@require_auth
def get_parsing_status(codebase_id):
    """Get parsing status for a codebase"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    parsed_codebase = ParsedCodebase.query.filter_by(
        id=codebase_id, tenant_id=tenant_id
    ).first()
    
    if not parsed_codebase:
        return jsonify({'error': 'Parsed codebase not found'}), 404
    
    return jsonify({
        'parsing_status': parsed_codebase.to_dict()
    })

@parsing_bp.route('/results/<codebase_id>', methods=['GET'])
@require_auth
def get_parsing_results(codebase_id):
    """Get detailed parsing results for a codebase"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    parsed_codebase = ParsedCodebase.query.filter_by(
        id=codebase_id, tenant_id=tenant_id
    ).first()
    
    if not parsed_codebase:
        return jsonify({'error': 'Parsed codebase not found'}), 404
    
    include_files = request.args.get('include_files', 'false').lower() == 'true'
    include_ast = request.args.get('include_ast', 'false').lower() == 'true'
    
    result = parsed_codebase.to_dict(include_files=include_files)
    
    if include_files and include_ast:
        # Add AST data to files
        for file_data in result['files']:
            parsed_file = ParsedFile.query.get(file_data['id'])
            if parsed_file:
                file_data.update(parsed_file.to_dict(include_ast=True))
    
    return jsonify({
        'parsing_results': result
    })

@parsing_bp.route('/file/<file_id>', methods=['GET'])
@require_auth
def get_parsed_file(file_id):
    """Get detailed parsing results for a specific file"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Get parsed file and verify access through codebase
    parsed_file = db.session.query(ParsedFile).join(ParsedCodebase).filter(
        ParsedFile.id == file_id,
        ParsedCodebase.tenant_id == tenant_id
    ).first()
    
    if not parsed_file:
        return jsonify({'error': 'Parsed file not found'}), 404
    
    include_ast = request.args.get('include_ast', 'false').lower() == 'true'
    
    return jsonify({
        'parsed_file': parsed_file.to_dict(include_ast=include_ast)
    })

@parsing_bp.route('/languages', methods=['GET'])
def get_supported_languages():
    """Get list of supported programming languages"""
    parser_factory = ParserFactory()
    
    return jsonify({
        'supported_languages': parser_factory.get_supported_languages(),
        'language_details': parser_factory.get_language_details()
    })

