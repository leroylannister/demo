"""Base test class for Demo test suite with BrowserStack API integration."""

import pytest
import os
import time
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
    test_failed = False
    failure_reason = None
    
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
            
            # Verify session is accessible on BrowserStack
            if self.browserstack_api.wait_for_session(self.session_id, max_wait=15):
                self.logger.info(f"[Demo] Session {self.session_id} confirmed on BrowserStack")
            else:
                self.logger.warning(f"[Demo] Session {self.session_id} not yet visible on BrowserStack")
        
        # Reset test status
        self.test_passed = False
        self.test_failed = False
        self.failure_reason = None
    
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
            self.logger.warning("[Demo] Cannot update BrowserStack status - missing API or session ID")
            return
        
        session_id = driver.session_id
        
        # Small delay to ensure session is fully registered
        time.sleep(2)
        
        # Determine test status based on various indicators
        test_result = self._get_test_result()
        
        # Update BrowserStack session status with retry logic
        if test_result['passed']:
            success = self.browserstack_api.update_session_status(
                session_id,
                "passed",
                test_result['reason']
            )
            if success:
                self.logger.info(f"[Demo] ✅ BrowserStack session marked as PASSED")
            else:
                self.logger.error(f"[Demo] ❌ Failed to update BrowserStack session status")
        else:
            success = self.browserstack_api.update_session_status(
                session_id,
                "failed",
                test_result['reason']
            )
            if success:
                self.logger.info(f"[Demo] ❌ BrowserStack session marked as FAILED")
            else:
                self.logger.error(f"[Demo] ❌ Failed to update BrowserStack session status")
    
    def _get_test_result(self):
        """Determine if the test passed or failed with improved logic."""
        # Check if test was manually marked as failed
        if self.test_failed:
            return {
                'passed': False,
                'reason': self.failure_reason or "Test manually marked as failed"
            }
        
        # Check if test was manually marked as passed
        if self.test_passed:
            return {
                'passed': True,
                'reason': "Test manually marked as passed"
            }
        
        # Check pytest outcome using pytest's internal mechanisms
        try:
            import pytest
            # Get current test result from pytest if available
            current_test = getattr(self, '_pytest_current_test', None)
            if current_test:
                # If we reach here without explicit failure, assume success
                return {
                    'passed': True,
                    'reason': f"Test {current_test.split('::')[-1]} completed without errors"
                }
        except:
            pass
        
        # Default to passed if no explicit failure was recorded
        return {
            'passed': True,
            'reason': "Test completed without explicit failure"
        }
    
    def mark_test_passed(self, reason="Test completed successfully"):
        """Manually mark test as passed for BrowserStack reporting."""
        self.test_passed = True
        self.test_failed = False
        self.logger.info(f"[Demo] Marked test as PASSED: {reason}")
        
        # Immediate update if session is available
        if self.session_id and self.browserstack_api:
            success = self.browserstack_api.update_session_status(self.session_id, "passed", reason)
            if not success:
                self.logger.warning(f"[Demo] Failed to immediately update BrowserStack status, will retry in teardown")
    
    def mark_test_failed(self, reason="Test failed"):
        """Manually mark test as failed for BrowserStack reporting."""
        self.test_failed = True
        self.test_passed = False
        self.failure_reason = reason
        self.logger.error(f"[Demo] Marked test as FAILED: {reason}")
        
        # Immediate update if session is available
        if self.session_id and self.browserstack_api:
            success = self.browserstack_api.update_session_status(self.session_id, "failed", reason)
            if not success:
                self.logger.warning(f"[Demo] Failed to immediately update BrowserStack status, will retry in teardown")
    
    def verify_browserstack_credentials(self):
        """Verify BrowserStack credentials are properly configured."""
        if not self.browserstack_api:
            self.logger.error("[Demo] BrowserStack API not initialized")
            return False
        
        username = self.browserstack_api.username
        access_key = self.browserstack_api.access_key
        
        if not username:
            self.logger.error("[Demo] BrowserStack username not configured")
            return False
        
        if not access_key:
            self.logger.error("[Demo] BrowserStack access key not configured")
            return False
        
        self.logger.info(f"[Demo] BrowserStack credentials configured for user: {username}")
        return True
    
    def get_session_details(self):
        """Get current session details from BrowserStack."""
        if not self.session_id or not self.browserstack_api:
            return None
        
        details = self.browserstack_api.get_session_details(self.session_id)
        if details:
            self.logger.info(f"[Demo] Session details retrieved: {details.get('name', 'Unknown')}")
        return details
    
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
    
    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """Hook to capture pytest test outcomes."""
        outcome = yield
        report = outcome.get_result()
        
        # Store test outcome for BrowserStack reporting
        if report.when == 'call':
            if report.failed:
                self.mark_test_failed(f"Test failed: {report.longrepr}")
            elif report.passed:
                self.mark_test_passed("Test passed all assertions")
    
    def handle_test_exception(self, exception, test_name="Unknown"):
        """Handle exceptions during test execution."""
        error_msg = f"Exception in {test_name}: {str(exception)}"
        self.logger.error(f"[Demo] {error_msg}")
        self.mark_test_failed(error_msg)
        
        # Take screenshot for debugging
        self.take_screenshot(f"error_{test_name}")
        
        # Re-raise the exception so pytest can handle it
        raise exception