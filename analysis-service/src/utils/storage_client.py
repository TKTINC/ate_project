"""
ATE Analysis Service - Storage Service Client
Client for interacting with the storage service
"""

import requests
from typing import Dict, List, Optional, Any

class StorageClient:
    """Client for interacting with the ATE storage service"""
    
    def __init__(self, storage_service_url: str):
        self.base_url = storage_service_url.rstrip('/')
        self.session = requests.Session()
    
    def get_project_files(self, project_id: str, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get list of files in a project"""
        try:
            headers = self._get_auth_headers(user_context)
            
            response = self.session.get(
                f"{self.base_url}/api/projects/{project_id}/files",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('files', [])
            else:
                return []
                
        except Exception as e:
            print(f"Error getting project files: {str(e)}")
            return []
    
    def download_file(self, project_id: str, file_id: str, user_context: Dict[str, Any]) -> Optional[str]:
        """Download file content"""
        try:
            headers = self._get_auth_headers(user_context)
            
            response = self.session.get(
                f"{self.base_url}/api/projects/{project_id}/files/{file_id}/content",
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.text
            else:
                return None
                
        except Exception as e:
            print(f"Error downloading file: {str(e)}")
            return None
    
    def get_file_metadata(self, project_id: str, file_id: str, user_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get file metadata"""
        try:
            headers = self._get_auth_headers(user_context)
            
            response = self.session.get(
                f"{self.base_url}/api/projects/{project_id}/files/{file_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('file')
            else:
                return None
                
        except Exception as e:
            print(f"Error getting file metadata: {str(e)}")
            return None
    
    def store_analysis_result(self, project_id: str, analysis_data: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        """Store analysis results in storage service"""
        try:
            headers = self._get_auth_headers(user_context)
            headers['Content-Type'] = 'application/json'
            
            response = self.session.post(
                f"{self.base_url}/api/projects/{project_id}/analysis",
                json=analysis_data,
                headers=headers,
                timeout=30
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            print(f"Error storing analysis result: {str(e)}")
            return False
    
    def get_project_info(self, project_id: str, user_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get project information"""
        try:
            headers = self._get_auth_headers(user_context)
            
            response = self.session.get(
                f"{self.base_url}/api/projects/{project_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('project')
            else:
                return None
                
        except Exception as e:
            print(f"Error getting project info: {str(e)}")
            return None
    
    def _get_auth_headers(self, user_context: Dict[str, Any]) -> Dict[str, str]:
        """Get authentication headers for requests"""
        headers = {}
        
        # Add tenant ID for multi-tenant isolation
        if 'tenant_id' in user_context:
            headers['X-Tenant-ID'] = user_context['tenant_id']
        
        # Add user ID for audit logging
        if 'user_id' in user_context:
            headers['X-User-ID'] = user_context['user_id']
        
        # Add authorization token if available
        if 'token' in user_context:
            headers['Authorization'] = f"Bearer {user_context['token']}"
        
        return headers
    
    def health_check(self) -> bool:
        """Check if storage service is healthy"""
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

