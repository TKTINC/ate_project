"""
ATE Opportunity Detection Service - Business Intelligence Client
Client for integrating with business intelligence service
"""

import requests
from typing import Dict, Any, Optional

class BusinessIntelligenceClient:
    """Client for business intelligence service integration"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
    
    def get_comprehensive_analysis(self, analysis_id: str, current_user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get comprehensive business intelligence analysis"""
        try:
            headers = {
                'Authorization': f"Bearer {current_user.get('token', '')}",
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/api/intelligence/results/{analysis_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get business analysis: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting business analysis: {str(e)}")
            return None
    
    def get_domain_analysis(self, analysis_id: str, current_user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get domain classification analysis"""
        try:
            headers = {
                'Authorization': f"Bearer {current_user.get('token', '')}",
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/api/domains/results/{analysis_id}",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"Error getting domain analysis: {str(e)}")
            return None
    
    def get_process_analysis(self, analysis_id: str, current_user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get business process analysis"""
        try:
            headers = {
                'Authorization': f"Bearer {current_user.get('token', '')}",
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/api/processes/results/{analysis_id}",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"Error getting process analysis: {str(e)}")
            return None
    
    def get_knowledge_graphs(self, analysis_id: str, current_user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get knowledge graphs"""
        try:
            headers = {
                'Authorization': f"Bearer {current_user.get('token', '')}",
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/api/knowledge/graphs/{analysis_id}",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"Error getting knowledge graphs: {str(e)}")
            return None

