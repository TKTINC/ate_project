"""
ATE Business Intelligence Service - Knowledge Graph Builder
Knowledge graph construction and semantic analysis
"""

import networkx as nx
from typing import Dict, List, Any
from collections import defaultdict

class KnowledgeGraphBuilder:
    """Builds knowledge graphs from business analysis data"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_nodes = config.get('max_nodes', 10000)
        self.graph_types = config.get('graph_types', ['entity_relationship'])
    
    def build_graphs(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build knowledge graphs from business analysis data"""
        try:
            graphs = []
            
            # Build different types of knowledge graphs
            if 'entity_relationship' in self.graph_types:
                entity_graph = self._build_entity_relationship_graph(graph_data)
                graphs.append(entity_graph)
            
            if 'concept_hierarchy' in self.graph_types:
                concept_graph = self._build_concept_hierarchy_graph(graph_data)
                graphs.append(concept_graph)
            
            if 'process_flow' in self.graph_types:
                process_graph = self._build_process_flow_graph(graph_data)
                graphs.append(process_graph)
            
            return {
                'graphs': graphs,
                'summary': {
                    'graphs_created': len(graphs),
                    'total_nodes': sum(len(g['nodes']) for g in graphs),
                    'total_edges': sum(len(g['edges']) for g in graphs)
                }
            }
            
        except Exception as e:
            return {
                'graphs': [],
                'errors': [str(e)]
            }
    
    def _build_entity_relationship_graph(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build entity relationship knowledge graph"""
        G = nx.Graph()
        nodes = []
        edges = []
        
        # Add domain entities as nodes
        for domain in graph_data.get('domains', []):
            domain_node = {
                'id': f"domain_{domain['id']}",
                'type': 'domain',
                'name': domain['domain_name'],
                'category': domain.get('domain_category', ''),
                'properties': {
                    'confidence': domain.get('confidence_score', 0.0),
                    'coverage': domain.get('coverage_percentage', 0.0)
                }
            }
            nodes.append(domain_node)
            G.add_node(domain_node['id'], **domain_node)
            
            # Add business entities within domain
            for entity in domain.get('business_entities', []):
                entity_node = {
                    'id': f"entity_{entity.get('entity_name', '').replace(' ', '_')}",
                    'type': 'business_entity',
                    'name': entity.get('entity_name', ''),
                    'entity_type': entity.get('entity_type', ''),
                    'properties': {
                        'confidence': entity.get('confidence_score', 0.0),
                        'importance': entity.get('importance_score', 0.0)
                    }
                }
                nodes.append(entity_node)
                G.add_node(entity_node['id'], **entity_node)
                
                # Create edge between domain and entity
                edge = {
                    'source': domain_node['id'],
                    'target': entity_node['id'],
                    'relationship': 'contains',
                    'weight': 1.0
                }
                edges.append(edge)
                G.add_edge(domain_node['id'], entity_node['id'], **edge)
        
        # Add process nodes and relationships
        for process in graph_data.get('processes', []):
            process_node = {
                'id': f"process_{process['id']}",
                'type': 'business_process',
                'name': process['process_name'],
                'process_type': process.get('process_type', ''),
                'properties': {
                    'confidence': process.get('confidence_score', 0.0),
                    'complexity': process.get('complexity_score', 0.0),
                    'automation_potential': process.get('automation_potential', 0.0)
                }
            }
            nodes.append(process_node)
            G.add_node(process_node['id'], **process_node)
            
            # Link process to domain if specified
            if process.get('domain_id'):
                domain_edge = {
                    'source': f"domain_{process['domain_id']}",
                    'target': process_node['id'],
                    'relationship': 'executes',
                    'weight': 0.8
                }
                edges.append(domain_edge)
                if f"domain_{process['domain_id']}" in [n['id'] for n in nodes]:
                    G.add_edge(f"domain_{process['domain_id']}", process_node['id'], **domain_edge)
        
        # Calculate graph metrics
        graph_metrics = self._calculate_graph_metrics(G)
        
        # Perform semantic analysis
        semantic_analysis = self._perform_semantic_analysis(nodes, edges)
        
        return {
            'graph_name': 'Entity Relationship Graph',
            'graph_type': 'entity_relationship',
            'graph_scope': 'global',
            'nodes': nodes,
            'edges': edges,
            'concepts': semantic_analysis['concepts'],
            'concept_hierarchy': semantic_analysis['concept_hierarchy'],
            'semantic_relationships': semantic_analysis['semantic_relationships'],
            'density': graph_metrics['density'],
            'clustering_coefficient': graph_metrics['clustering_coefficient'],
            'centrality_measures': graph_metrics['centrality_measures'],
            'communities': graph_metrics['communities'],
            'key_entities': graph_metrics['key_entities'],
            'relationship_patterns': graph_metrics['relationship_patterns'],
            'completeness_score': self._assess_completeness(nodes, edges),
            'consistency_score': self._assess_consistency(nodes, edges),
            'confidence_score': self._calculate_overall_confidence(nodes)
        }
    
    def _build_concept_hierarchy_graph(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build concept hierarchy knowledge graph"""
        G = nx.DiGraph()  # Directed graph for hierarchy
        nodes = []
        edges = []
        
        # Create concept hierarchy from domains
        root_node = {
            'id': 'business_concepts',
            'type': 'concept_root',
            'name': 'Business Concepts',
            'level': 0,
            'properties': {}
        }
        nodes.append(root_node)
        G.add_node(root_node['id'], **root_node)
        
        # Add domain concepts
        for domain in graph_data.get('domains', []):
            domain_concept = {
                'id': f"concept_{domain['domain_category']}",
                'type': 'domain_concept',
                'name': f"{domain['domain_category'].title()} Concept",
                'level': 1,
                'properties': {
                    'domain_category': domain['domain_category'],
                    'vocabulary_size': len(domain.get('domain_vocabulary', []))
                }
            }
            nodes.append(domain_concept)
            G.add_node(domain_concept['id'], **domain_concept)
            
            # Connect to root
            hierarchy_edge = {
                'source': root_node['id'],
                'target': domain_concept['id'],
                'relationship': 'parent_of',
                'weight': 1.0
            }
            edges.append(hierarchy_edge)
            G.add_edge(root_node['id'], domain_concept['id'], **hierarchy_edge)
            
            # Add vocabulary concepts
            for vocab_term in domain.get('domain_vocabulary', [])[:10]:  # Limit for performance
                vocab_concept = {
                    'id': f"vocab_{vocab_term.replace(' ', '_')}",
                    'type': 'vocabulary_concept',
                    'name': vocab_term.title(),
                    'level': 2,
                    'properties': {
                        'term': vocab_term,
                        'domain': domain['domain_category']
                    }
                }
                nodes.append(vocab_concept)
                G.add_node(vocab_concept['id'], **vocab_concept)
                
                # Connect to domain concept
                vocab_edge = {
                    'source': domain_concept['id'],
                    'target': vocab_concept['id'],
                    'relationship': 'contains_term',
                    'weight': 0.7
                }
                edges.append(vocab_edge)
                G.add_edge(domain_concept['id'], vocab_concept['id'], **vocab_edge)
        
        # Calculate hierarchy metrics
        hierarchy_metrics = self._calculate_hierarchy_metrics(G)
        
        return {
            'graph_name': 'Concept Hierarchy Graph',
            'graph_type': 'concept_hierarchy',
            'graph_scope': 'global',
            'nodes': nodes,
            'edges': edges,
            'concepts': [node['name'] for node in nodes if node['type'] in ['domain_concept', 'vocabulary_concept']],
            'concept_hierarchy': hierarchy_metrics['hierarchy_structure'],
            'semantic_relationships': hierarchy_metrics['semantic_relationships'],
            'density': hierarchy_metrics['density'],
            'clustering_coefficient': 0.0,  # Not applicable for hierarchies
            'centrality_measures': hierarchy_metrics['centrality_measures'],
            'communities': [],  # Not applicable for hierarchies
            'key_entities': hierarchy_metrics['key_concepts'],
            'relationship_patterns': ['parent_child', 'contains_term'],
            'completeness_score': 0.8,
            'consistency_score': 0.9,
            'confidence_score': 0.85
        }
    
    def _build_process_flow_graph(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build process flow knowledge graph"""
        G = nx.DiGraph()  # Directed graph for process flows
        nodes = []
        edges = []
        
        # Add process nodes and their steps
        for process in graph_data.get('processes', []):
            process_node = {
                'id': f"process_{process['id']}",
                'type': 'process',
                'name': process['process_name'],
                'properties': {
                    'process_type': process.get('process_type', ''),
                    'complexity': process.get('complexity_score', 0.0)
                }
            }
            nodes.append(process_node)
            G.add_node(process_node['id'], **process_node)
            
            # Add process steps
            for i, step in enumerate(process.get('process_steps', [])):
                step_node = {
                    'id': f"step_{process['id']}_{i}",
                    'type': 'process_step',
                    'name': step.get('step_name', f"Step {i+1}"),
                    'properties': {
                        'step_number': step.get('step_number', i+1),
                        'step_type': step.get('step_type', 'processing')
                    }
                }
                nodes.append(step_node)
                G.add_node(step_node['id'], **step_node)
                
                # Connect process to step
                step_edge = {
                    'source': process_node['id'],
                    'target': step_node['id'],
                    'relationship': 'contains_step',
                    'weight': 1.0
                }
                edges.append(step_edge)
                G.add_edge(process_node['id'], step_node['id'], **step_edge)
                
                # Connect sequential steps
                if i > 0:
                    prev_step_id = f"step_{process['id']}_{i-1}"
                    sequence_edge = {
                        'source': prev_step_id,
                        'target': step_node['id'],
                        'relationship': 'followed_by',
                        'weight': 0.9
                    }
                    edges.append(sequence_edge)
                    G.add_edge(prev_step_id, step_node['id'], **sequence_edge)
        
        # Calculate flow metrics
        flow_metrics = self._calculate_flow_metrics(G)
        
        return {
            'graph_name': 'Process Flow Graph',
            'graph_type': 'process_flow',
            'graph_scope': 'process',
            'nodes': nodes,
            'edges': edges,
            'concepts': [node['name'] for node in nodes if node['type'] == 'process'],
            'concept_hierarchy': {},
            'semantic_relationships': flow_metrics['flow_relationships'],
            'density': flow_metrics['density'],
            'clustering_coefficient': flow_metrics['clustering_coefficient'],
            'centrality_measures': flow_metrics['centrality_measures'],
            'communities': flow_metrics['process_groups'],
            'key_entities': flow_metrics['critical_processes'],
            'relationship_patterns': ['contains_step', 'followed_by'],
            'completeness_score': 0.7,
            'consistency_score': 0.8,
            'confidence_score': 0.75
        }
    
    def _calculate_graph_metrics(self, G: nx.Graph) -> Dict[str, Any]:
        """Calculate various graph metrics"""
        metrics = {}
        
        if len(G.nodes()) > 0:
            # Density
            metrics['density'] = nx.density(G)
            
            # Clustering coefficient
            metrics['clustering_coefficient'] = nx.average_clustering(G)
            
            # Centrality measures
            metrics['centrality_measures'] = {
                'degree_centrality': dict(list(nx.degree_centrality(G).items())[:10]),
                'betweenness_centrality': dict(list(nx.betweenness_centrality(G).items())[:10])
            }
            
            # Community detection
            try:
                communities = list(nx.connected_components(G))
                metrics['communities'] = [list(community) for community in communities[:5]]
            except:
                metrics['communities'] = []
            
            # Key entities (highest degree centrality)
            degree_centrality = nx.degree_centrality(G)
            key_entities = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
            metrics['key_entities'] = [{'id': entity[0], 'centrality': entity[1]} for entity in key_entities]
            
            # Relationship patterns
            edge_types = defaultdict(int)
            for _, _, data in G.edges(data=True):
                edge_types[data.get('relationship', 'unknown')] += 1
            metrics['relationship_patterns'] = dict(edge_types)
        else:
            metrics = {
                'density': 0.0,
                'clustering_coefficient': 0.0,
                'centrality_measures': {},
                'communities': [],
                'key_entities': [],
                'relationship_patterns': {}
            }
        
        return metrics
    
    def _calculate_hierarchy_metrics(self, G: nx.DiGraph) -> Dict[str, Any]:
        """Calculate hierarchy-specific metrics"""
        metrics = {}
        
        # Hierarchy structure
        hierarchy_structure = {}
        for node in G.nodes():
            level = G.nodes[node].get('level', 0)
            if level not in hierarchy_structure:
                hierarchy_structure[level] = []
            hierarchy_structure[level].append(node)
        
        metrics['hierarchy_structure'] = hierarchy_structure
        
        # Semantic relationships
        semantic_relationships = []
        for source, target, data in G.edges(data=True):
            semantic_relationships.append({
                'source': source,
                'target': target,
                'type': data.get('relationship', 'unknown'),
                'weight': data.get('weight', 1.0)
            })
        
        metrics['semantic_relationships'] = semantic_relationships
        
        # Density
        metrics['density'] = nx.density(G)
        
        # Centrality measures
        metrics['centrality_measures'] = {
            'in_degree_centrality': dict(list(nx.in_degree_centrality(G).items())[:10]),
            'out_degree_centrality': dict(list(nx.out_degree_centrality(G).items())[:10])
        }
        
        # Key concepts (highest centrality)
        in_degree_centrality = nx.in_degree_centrality(G)
        key_concepts = sorted(in_degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        metrics['key_concepts'] = [{'id': concept[0], 'centrality': concept[1]} for concept in key_concepts]
        
        return metrics
    
    def _calculate_flow_metrics(self, G: nx.DiGraph) -> Dict[str, Any]:
        """Calculate process flow-specific metrics"""
        metrics = {}
        
        # Flow relationships
        flow_relationships = []
        for source, target, data in G.edges(data=True):
            flow_relationships.append({
                'source': source,
                'target': target,
                'type': data.get('relationship', 'unknown'),
                'weight': data.get('weight', 1.0)
            })
        
        metrics['flow_relationships'] = flow_relationships
        
        # Density
        metrics['density'] = nx.density(G)
        
        # Clustering coefficient
        metrics['clustering_coefficient'] = nx.average_clustering(G.to_undirected())
        
        # Centrality measures
        metrics['centrality_measures'] = {
            'in_degree_centrality': dict(list(nx.in_degree_centrality(G).items())[:10]),
            'out_degree_centrality': dict(list(nx.out_degree_centrality(G).items())[:10])
        }
        
        # Process groups (weakly connected components)
        try:
            components = list(nx.weakly_connected_components(G))
            metrics['process_groups'] = [list(component) for component in components[:5]]
        except:
            metrics['process_groups'] = []
        
        # Critical processes (highest centrality)
        in_degree_centrality = nx.in_degree_centrality(G)
        critical_processes = sorted(in_degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        metrics['critical_processes'] = [{'id': process[0], 'centrality': process[1]} for process in critical_processes]
        
        return metrics
    
    def _perform_semantic_analysis(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform semantic analysis on the graph"""
        # Extract concepts
        concepts = []
        for node in nodes:
            if node['type'] in ['domain', 'business_entity', 'business_process']:
                concepts.append(node['name'])
        
        # Build concept hierarchy
        concept_hierarchy = {}
        for node in nodes:
            if node['type'] == 'domain':
                concept_hierarchy[node['name']] = []
                for other_node in nodes:
                    if other_node['type'] == 'business_entity':
                        # Check if entity belongs to this domain
                        for edge in edges:
                            if edge['source'] == node['id'] and edge['target'] == other_node['id']:
                                concept_hierarchy[node['name']].append(other_node['name'])
        
        # Extract semantic relationships
        semantic_relationships = []
        for edge in edges:
            semantic_relationships.append({
                'source': edge['source'],
                'target': edge['target'],
                'type': edge['relationship'],
                'weight': edge['weight']
            })
        
        return {
            'concepts': concepts,
            'concept_hierarchy': concept_hierarchy,
            'semantic_relationships': semantic_relationships
        }
    
    def _assess_completeness(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> float:
        """Assess the completeness of the knowledge graph"""
        # Simple heuristic: ratio of edges to possible edges
        num_nodes = len(nodes)
        num_edges = len(edges)
        
        if num_nodes <= 1:
            return 0.0
        
        max_possible_edges = num_nodes * (num_nodes - 1) / 2
        completeness = min(num_edges / max_possible_edges, 1.0)
        
        return completeness
    
    def _assess_consistency(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> float:
        """Assess the consistency of the knowledge graph"""
        # Simple heuristic: check for consistent node types and relationships
        consistency_score = 0.9  # Default high consistency
        
        # Check for orphaned nodes
        connected_nodes = set()
        for edge in edges:
            connected_nodes.add(edge['source'])
            connected_nodes.add(edge['target'])
        
        total_nodes = len(nodes)
        connected_ratio = len(connected_nodes) / max(total_nodes, 1)
        
        return consistency_score * connected_ratio
    
    def _calculate_overall_confidence(self, nodes: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence in the knowledge graph"""
        if not nodes:
            return 0.0
        
        confidence_scores = []
        for node in nodes:
            if 'confidence' in node.get('properties', {}):
                confidence_scores.append(node['properties']['confidence'])
        
        if confidence_scores:
            return sum(confidence_scores) / len(confidence_scores)
        else:
            return 0.7  # Default moderate confidence

