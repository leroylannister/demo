"""BrowserStack REST API helper for updating test session status."""

import requests
import logging
import os
from typing import Optional

class BrowserStackAPI:
    """Helper class for BrowserStack Automate REST API operations."""
    
    def __init__(self, username: str = None, access_key: str = None):
        """Initialize with BrowserStack credentials."""
        self.username = username or os.getenv('BROWSERSTACK_USERNAME')
        self.access_key = access_key or os.getenv('BROWSERSTACK_ACCESS_KEY')
        self.base_url = "https://api.browserstack.com/automate"
        self.logger = logging.getLogger(__name__)
        
    def update_session_status(self, session_id: str, status: str, reason: str) -> bool:
        """
        Update the status of a BrowserStack session using REST API.
        
        Args:
            session_id: The BrowserStack session ID
            status: "passed" or "failed"
            reason: Reason for the status
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not session_id:
            self.logger.error("Session ID is required")
            return False
            
        url = f"{self.base_url}/sessions/{session_id}.json"
        data = {
            "status": status,
            "reason": reason
        }
        
        try:
            response = requests.put(
                url,
                json=data,
                auth=(self.username, self.access_key),
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info(f"Successfully updated session {session_id} status to {status}")
                return True
            else:
                self.logger.error(f"Failed to update session status. Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error updating session status: {e}")
            return False
    
    def get_session_details(self, session_id: str) -> Optional[dict]:
        """Get details of a specific session."""
        url = f"{self.base_url}/sessions/{session_id}.json"
        
        try:
            response = requests.get(
                url,
                auth=(self.username, self.access_key),
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Failed to get session details. Status code: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting session details: {e}")
            return None
