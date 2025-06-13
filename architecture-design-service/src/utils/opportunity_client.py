"""
ATE Architecture Design Service - Opportunity Service Client
"""

import requests
import json
from typing import Dict, List, Optional

class OpportunityClient:
    """Client for communicating with the Opportunity Detection Service"""
    
    def __init__(self, base_url: str = "http://localhost:5005"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_opportunity(self, opportunity_id: str, token: str = None) -> Optional[Dict]:
        """Get opportunity details by ID"""
        try:
            headers = {}
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            response = self.session.get(
                f"{self.base_url}/api/opportunities/{opportunity_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('opportunity')
            else:
                print(f"Error getting opportunity: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error communicating with opportunity service: {e}")
            return None
    
    def list_opportunities(self, filters: Dict = None, token: str = None) -> List[Dict]:
        """List opportunities with optional filters"""
        try:
            headers = {}
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            params = filters or {}
            
            response = self.session.get(
                f"{self.base_url}/api/opportunities",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('opportunities', [])
            else:
                print(f"Error listing opportunities: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Error communicating with opportunity service: {e}")
            return []
    
    def get_business_case(self, business_case_id: str, token: str = None) -> Optional[Dict]:
        """Get business case details by ID"""
        try:
            headers = {}
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            response = self.session.get(
                f"{self.base_url}/api/business_cases/{business_case_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('business_case')
            else:
                print(f"Error getting business case: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error communicating with opportunity service: {e}")
            return None

