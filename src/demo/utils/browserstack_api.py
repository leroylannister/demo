"""BrowserStack REST API helper for updating test session status."""

import requests
import logging
import os
import time
from typing import Optional

class BrowserStackAPI:
    """Helper class for BrowserStack Automate REST API operations."""
    
    def __init__(self, username: str = None, access_key: str = None):
        """Initialize with BrowserStack credentials."""
        self.username = username or os.getenv('BROWSERSTACK_USERNAME')
        self.access_key = access_key or os.getenv('BROWSERSTACK_ACCESS_KEY')
        self.base_url = "https://api.browserstack.com/automate"
        self.logger = logging.getLogger(__name__)
        
        # Validate credentials
        if not self.username or not self.access_key:
            self.logger.error("BrowserStack username and access key are required")
            
    def wait_for_session(self, session_id: str, max_wait: int = 30) -> bool:
        """
        Wait for session to be available on BrowserStack.
        
        Args:
            session_id: The BrowserStack session ID
            max_wait: Maximum time to wait in seconds
            
        Returns:
            bool: True if session is available, False otherwise
        """
        if not session_id:
            return False
            
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if self.get_session_details(session_id):
                self.logger.info(f"Session {session_id} is now available on BrowserStack")
                return True
            time.sleep(2)
            
        self.logger.warning(f"Session {session_id} not found after {max_wait} seconds")
        return False
        
    def update_session_status(self, session_id: str, status: str, reason: str, retry_count: int = 3) -> bool:
        """
        Update the status of a BrowserStack session using REST API with retry logic.
        
        Args:
            session_id: The BrowserStack session ID
            status: "passed" or "failed"
            reason: Reason for the status
            retry_count: Number of retry attempts
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not session_id:
            self.logger.error("Session ID is required")
            return False
            
        if not self.username or not self.access_key:
            self.logger.error("BrowserStack credentials not configured")
            return False
            
        # Wait for session to be available first
        if not self.wait_for_session(session_id):
            self.logger.error(f"Session {session_id} not found on BrowserStack")
            return False
            
        url = f"{self.base_url}/sessions/{session_id}.json"
        data = {
            "status": status,
            "reason": reason
        }
        
        for attempt in range(retry_count):
            try:
                self.logger.info(f"Attempting to update session {session_id} (attempt {attempt + 1}/{retry_count})")
                
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
                elif response.status_code == 404:
                    self.logger.warning(f"Session {session_id} not found (404). Waiting before retry...")
                    time.sleep(5)  # Wait longer for 404 errors
                else:
                    self.logger.error(f"Failed to update session status. Status code: {response.status_code}, Response: {response.text}")
                    time.sleep(2)
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error updating session status (attempt {attempt + 1}): {e}")
                if attempt < retry_count - 1:
                    time.sleep(2)
                    
        self.logger.error(f"Failed to update session {session_id} after {retry_count} attempts")
        return False
    
    def get_session_details(self, session_id: str) -> Optional[dict]:
        """Get details of a specific session."""
        if not session_id:
            return None
            
        url = f"{self.base_url}/sessions/{session_id}.json"
        
        try:
            response = requests.get(
                url,
                auth=(self.username, self.access_key),
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                self.logger.debug(f"Session {session_id} not found (404)")
                return None
            else:
                self.logger.error(f"Failed to get session details. Status code: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting session details: {e}")
            return None
            
    def get_build_sessions(self, build_id: str) -> Optional[list]:
        """Get all sessions for a specific build."""
        url = f"{self.base_url}/builds/{build_id}/sessions.json"
        
        try:
            response = requests.get(
                url,
                auth=(self.username, self.access_key),
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Failed to get build sessions. Status code: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting build sessions: {e}")
            return None

# Convenience function for backward compatibility
def update_session_status(session_id: str, status: str, reason: str = "") -> bool:
    """Convenience function to update session status."""
    api = BrowserStackAPI()
    return api.update_session_status(session_id, status, reason)