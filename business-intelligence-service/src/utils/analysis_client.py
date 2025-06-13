"""
ATE Business Intelligence Service - Analysis Service Client
Client for communicating with the analysis service
"""

import requests
from typing import Dict, Optional, Any

class AnalysisClient:
    """Client for interacting with the analysis service"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
    
    def get_parsing_results(self, codebase_id: str, user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get parsing results for a codebase"""
        try:
            # Create authorization header
            headers = {
                'Authorization': f"Bearer {user.get('token', '')}",
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/api/parse/results/{codebase_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                response.raise_for_status()
                
        except requests.RequestException as e:
            print(f"Error fetching parsing results: {e}")
            return None
    
    def get_dependency_analysis(self, codebase_id: str, user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get dependency analysis for a codebase"""
        try:
            headers = {
                'Authorization': f"Bearer {user.get('token', '')}",
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/api/analyze/dependencies/{codebase_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                response.raise_for_status()
                
        except requests.RequestException as e:
            print(f"Error fetching dependency analysis: {e}")
            return None
    
    def get_quality_assessment(self, codebase_id: str, user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get quality assessment for a codebase"""
        try:
            headers = {
                'Authorization': f"Bearer {user.get('token', '')}",
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/api/quality/assess/{codebase_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                response.raise_for_status()
                
        except requests.RequestException as e:
            print(f"Error fetching quality assessment: {e}")
            return None
    
    def get_architecture_analysis(self, codebase_id: str, user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get architecture analysis for a codebase"""
        try:
            headers = {
                'Authorization': f"Bearer {user.get('token', '')}",
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/api/architecture/analyze/{codebase_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                response.raise_for_status()
                
        except requests.RequestException as e:
            print(f"Error fetching architecture analysis: {e}")
            return None

