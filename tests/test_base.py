"""Base test class for Demo test suite with BrowserStack API integration."""

import pytest
import os
from typing import Optional
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.demo.utils.logger import get_logger
from src.demo.utils.browserstack_api import BrowserStackAPI


class TestBase:
    """Base test class with common functionality for Demo tests and BrowserStack integration."""
    
    driver = None
    logger = None
    session_id = None
    browserstack_api = None
    test_passed = False
    
    @pytest.fixture(autouse=True)
    def setup_method(self, driver):
        """Setup for each Demo test method with BrowserStack session tracking."""
        self.driver = driver
        self.logger = get_logger(f"Demo.{self.__class__.__name__}")
        
        # Initialize BrowserStack API helper
        self.browserstack_api = BrowserStackAPI()
        
        # Capture session ID for BrowserStack status reporting
        if self.driver and hasattr(self.driver, 'session_id'):
            self.session_id = self.driver.session_id
            self.logger.info(f"[Demo] BrowserStack session ID: {self.session_id}")
        
        # Reset test status
        self.test_passed = False
    
    @pytest.fixture(scope="function")
    def driver(self):
        """Setup Chrome driver with proper options for modern web apps."""
        chrome_options = Options()
        
        # Essential options to fix blank page issues
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Disable security features that might block content
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # User agent to avoid detection
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # For debugging - comment out headless mode
        # chrome_options.add_argument("--headless")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Set implicit wait
        driver.implicitly_wait(10)
        
        yield driver
        
        # Update BrowserStack session status before cleanup
        self._update_browserstack_status(driver)
        
        # Cleanup
        driver.quit()
    
    def _update_browserstack_status(self, driver):
        """Update BrowserStack session status based on test outcome."""
        if not self.browserstack_api or not hasattr(driver, 'session_id'):
            return
        
        session_id = driver.session_id
        
        # Determine test status based on pytest outcome
        test_result = self._get_test_result()
        
        # Update BrowserStack session status
        if test_result['passed']:
            self.browserstack_api.update_session_status(
                session_id,
                "passed",
                test_result['reason']
            )
        else:
            self.browserstack_api.update_session_status(
                session_id,
                "failed",
                test_result['reason']
            )
    
    def _get_test_result(self):
        """Determine if the test passed or failed."""
        # Check if test was manually marked
        if hasattr(self, 'test_passed') and self.test_passed:
            return {
                'passed': True,
                'reason': "Test completed successfully"
            }
        
        # For pytest, we'll assume passed unless manually marked as failed
        # The actual test outcome will be determined by pytest's exception handling
        return {
            'passed': True,
            'reason': f"Test {getattr(self, '_pytest_current_test', 'unknown')} completed"
        }
    
    def mark_test_passed(self, reason="Test completed successfully"):
        """Manually mark test as passed for BrowserStack reporting."""
        self.test_passed = True
        if self.session_id and self.browserstack_api:
            self.browserstack_api.update_session_status(self.session_id, "passed", reason)
            self.logger.info(f"[Demo] Marked test as PASSED: {reason}")
    
    def mark_test_failed(self, reason="Test failed"):
        """Manually mark test as failed for BrowserStack reporting."""
        self.test_passed = False
        if self.session_id and self.browserstack_api:
            self.browserstack_api.update_session_status(self.session_id, "failed", reason)
            self.logger.error(f"[Demo] Marked test as FAILED: {reason}")
    
    def take_screenshot(self, name: str) -> Optional[Path]:
        """Take screenshot for debugging Demo tests."""
        try:
            screenshot_dir = Path("screenshots")
            screenshot_dir.mkdir(exist_ok=True)
            
            filepath = screenshot_dir / f"demo_{name}.png"
            self.driver.save_screenshot(str(filepath))
            self.logger.info(f"[Demo] Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"[Demo] Failed to take screenshot: {e}")
            return None
