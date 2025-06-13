"""
ATE Business Intelligence Service - Knowledge Graph Routes
Knowledge graph construction and semantic analysis
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from src.models.user import db, BusinessAnalysis, KnowledgeGraph
from src.utils.auth import require_auth, get_current_user
from src.analyzers.knowledge_graph_builder import KnowledgeGraphBuilder

knowledge_bp = Blueprint('knowledge', __name__)

@knowledge_bp.route('/build/<analysis_id>', methods=['POST'])
@require_auth
def build_knowledge_graph(analysis_id):
    """Build knowledge graphs from business analysis"""
    try:
        current_user = get_current_user()
        tenant_id = current_user['tenant_id']
        
        # Verify business analysis exists
        business_analysis = BusinessAnalysis.query.filter_by(
            id=analysis_id, tenant_id=tenant_id
        ).first()
        
        if not business_analysis:
            return jsonify({'error': 'Business analysis not found'}), 404
        
        # Get configuration
        config = request.get_json() or {}
        graph_config = {
            'graph_types': config.get('graph_types', ['entity_relationship', 'concept_hierarchy']),
            'max_nodes': config.get('max_nodes', current_app.config['MAX_KNOWLEDGE_GRAPH_NODES']),
            'include_semantic_analysis': config.get('include_semantic_analysis', True),
            'detect_communities': config.get('detect_communities', True),
            'calculate_centrality': config.get('calculate_centrality', True)
        }
        
        # Prepare data for knowledge graph construction
        graph_data = {
            'domains': [domain.to_dict() for domain in business_analysis.domains],
            'processes': [process.to_dict() for process in business_analysis.processes],
            'business_summary': business_analysis.business_summary
        }
        
        # Build knowledge graphs
        kg_builder = KnowledgeGraphBuilder(graph_config)
        graph_results = kg_builder.build_graphs(graph_data)
        
        # Store knowledge graphs
        graphs_created = []
        for graph_result in graph_results['graphs']:
            knowledge_graph = KnowledgeGraph(
                analysis_id=business_analysis.id,
                graph_name=graph_result['graph_name'],
                graph_type=graph_result['graph_type'],
                graph_scope=graph_result.get('graph_scope', 'global'),
                nodes=graph_result['nodes'],
                edges=graph_result['edges'],
                node_count=len(graph_result['nodes']),
                edge_count=len(graph_result['edges']),
                concepts=graph_result.get('concepts', []),
                concept_hierarchy=graph_result.get('concept_hierarchy', {}),
                semantic_relationships=graph_result.get('semantic_relationships', []),
                density=graph_result.get('density', 0.0),
                clustering_coefficient=graph_result.get('clustering_coefficient', 0.0),
                centrality_measures=graph_result.get('centrality_measures', {}),
                communities=graph_result.get('communities', []),
                key_entities=graph_result.get('key_entities', []),
                relationship_patterns=graph_result.get('relationship_patterns', []),
                completeness_score=graph_result.get('completeness_score', 0.0),
                consistency_score=graph_result.get('consistency_score', 0.0),
                confidence_score=graph_result.get('confidence_score', 0.0)
            )
            
            db.session.add(knowledge_graph)
            graphs_created.append(knowledge_graph)
        
        # Update business analysis summary
        business_analysis.business_summary.update({
            'knowledge_graphs_created': len(graphs_created),
            'total_entities': sum(kg.node_count for kg in graphs_created),
            'total_relationships': sum(kg.edge_count for kg in graphs_created)
        })
        
        db.session.commit()
        
        return jsonify({
            'message': 'Knowledge graphs built successfully',
            'analysis_id': business_analysis.id,
            'graphs_created': len(graphs_created),
            'total_nodes': sum(kg.node_count for kg in graphs_created),
            'total_edges': sum(kg.edge_count for kg in graphs_created),
            'summary': graph_results.get('summary', {})
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Knowledge graph construction failed: {str(e)}'}), 500

@knowledge_bp.route('/graphs/<analysis_id>', methods=['GET'])
@require_auth
def get_knowledge_graphs(analysis_id):
    """Get knowledge graphs for an analysis"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Verify access
    business_analysis = BusinessAnalysis.query.filter_by(
        id=analysis_id, tenant_id=tenant_id
    ).first()
    
    if not business_analysis:
        return jsonify({'error': 'Business analysis not found'}), 404
    
    include_graph_data = request.args.get('include_data', 'false').lower() == 'true'
    
    knowledge_graphs = KnowledgeGraph.query.filter_by(analysis_id=analysis_id).all()
    
    return jsonify({
        'knowledge_graphs': [kg.to_dict(include_graph_data=include_graph_data) for kg in knowledge_graphs],
        'summary': {
            'total_graphs': len(knowledge_graphs),
            'graph_types': list(set(kg.graph_type for kg in knowledge_graphs)),
            'total_nodes': sum(kg.node_count for kg in knowledge_graphs),
            'total_edges': sum(kg.edge_count for kg in knowledge_graphs)
        }
    })

@knowledge_bp.route('/graph/<graph_id>', methods=['GET'])
@require_auth
def get_graph_details(graph_id):
    """Get detailed information about a specific knowledge graph"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Get graph and verify access
    knowledge_graph = db.session.query(KnowledgeGraph).join(BusinessAnalysis).filter(
        KnowledgeGraph.id == graph_id,
        BusinessAnalysis.tenant_id == tenant_id
    ).first()
    
    if not knowledge_graph:
        return jsonify({'error': 'Knowledge graph not found'}), 404
    
    include_graph_data = request.args.get('include_data', 'true').lower() == 'true'
    
    return jsonify({
        'knowledge_graph': knowledge_graph.to_dict(include_graph_data=include_graph_data)
    })

@knowledge_bp.route('/semantic/<analysis_id>', methods=['GET'])
@require_auth
def get_semantic_analysis(analysis_id):
    """Get semantic analysis results across all knowledge graphs"""
    current_user = get_current_user()
    tenant_id = current_user['tenant_id']
    
    # Verify access
    business_analysis = BusinessAnalysis.query.filter_by(
        id=analysis_id, tenant_id=tenant_id
    ).first()
    
    if not business_analysis:
        return jsonify({'error': 'Business analysis not found'}), 404
    
    knowledge_graphs = KnowledgeGraph.query.filter_by(analysis_id=analysis_id).all()
    
    # Aggregate semantic analysis
    all_concepts = []
    all_relationships = []
    concept_hierarchies = {}
    
    for kg in knowledge_graphs:
        all_concepts.extend(kg.concepts or [])
        all_relationships.extend(kg.semantic_relationships or [])
        if kg.concept_hierarchy:
            concept_hierarchies[kg.graph_name] = kg.concept_hierarchy
    
    # Remove duplicates and analyze
    unique_concepts = list(set(all_concepts))
    relationship_types = list(set(rel.get('type') for rel in all_relationships if rel.get('type')))
    
    semantic_summary = {
        'total_concepts': len(unique_concepts),
        'unique_concepts': unique_concepts[:50],  # Limit for response size
        'total_relationships': len(all_relationships),
        'relationship_types': relationship_types,
        'concept_hierarchies': concept_hierarchies,
        'semantic_density': len(all_relationships) / max(len(unique_concepts), 1),
        'key_insights': [
            f"Identified {len(unique_concepts)} unique business concepts",
            f"Found {len(relationship_types)} types of semantic relationships",
            f"Average semantic density: {len(all_relationships) / max(len(unique_concepts), 1):.2f}"
        ]
    }
    
    return jsonify({
        'semantic_analysis': semantic_summary
    })

