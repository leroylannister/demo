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

# Import driver config at module level to avoid issues
try:
    from src.demo.utils.browserstack_driver_config import BrowserStackDriverConfig, BROWSER_CONFIGS
    DRIVER_CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"Warning: BrowserStack driver config not available: {e}")
    DRIVER_CONFIG_AVAILABLE = False
    BrowserStackDriverConfig = None
    BROWSER_CONFIGS = {}

# Add this RIGHT AFTER your imports, before the class definition:
print("=== BROWSERSTACK DEBUG ===")
print(f"BROWSERSTACK_USERNAME: {bool(os.getenv('BROWSERSTACK_USERNAME'))}")
print(f"BROWSERSTACK_ACCESS_KEY: {bool(os.getenv('BROWSERSTACK_ACCESS_KEY'))}")
print(f"DRIVER_CONFIG_AVAILABLE: {DRIVER_CONFIG_AVAILABLE}")
try:
    if DRIVER_CONFIG_AVAILABLE:
        print(f"should_use_browserstack(): {BrowserStackDriverConfig.should_use_browserstack()}")
    else:
        print("Cannot call should_use_browserstack() - driver config not available")
except Exception as e:
    print(f"Error calling should_use_browserstack(): {e}")
print("=== END DEBUG ===")


class TestBase:
    """Base test class with common functionality for Demo tests and BrowserStack integration."""
    
    driver = None
    logger = None
    session_id = None
    browserstack_api = None
    test_passed = False
    test_failed = False
    failure_reason = None
    is_browserstack_session = False  # Track session type
    
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
            self.logger.info(f"[Demo] Session ID: {self.session_id}")
            
            # Check if this is a BrowserStack session
            self.is_browserstack_session = self._is_browserstack_session(self.driver)
            
            if self.is_browserstack_session:
                self.logger.info(f"[Demo] BrowserStack session detected")
                # Verify session is accessible on BrowserStack
                if self.browserstack_api.wait_for_session(self.session_id, max_wait=15):
                    self.logger.info(f"[Demo] Session {self.session_id} confirmed on BrowserStack")
                else:
                    self.logger.warning(f"[Demo] Session {self.session_id} not yet visible on BrowserStack")
            else:
                self.logger.info(f"[Demo] Local Chrome session - BrowserStack reporting disabled")
        
        # Reset test status
        self.test_passed = False
        self.test_failed = False
        self.failure_reason = None
    
    @pytest.fixture(scope="function")
    def driver(self):
        """Setup driver - BrowserStack if credentials available, local Chrome otherwise."""
        
        # ADD DEBUG LINES:
        print(f"[DEBUG] BROWSERSTACK_USERNAME exists: {bool(os.getenv('BROWSERSTACK_USERNAME'))}")
        print(f"[DEBUG] BROWSERSTACK_ACCESS_KEY exists: {bool(os.getenv('BROWSERSTACK_ACCESS_KEY'))}")
        print(f"[DEBUG] DRIVER_CONFIG_AVAILABLE: {DRIVER_CONFIG_AVAILABLE}")
        
        # Check if driver config is available
        if not DRIVER_CONFIG_AVAILABLE:
            print("[Demo] BrowserStack driver config not available, using local Chrome")
            driver = self._create_local_chrome_driver()
        else:
            # ADD MORE DEBUG:
            print(f"[DEBUG] should_use_browserstack(): {BrowserStackDriverConfig.should_use_browserstack()}")
            
            # Determine browser config from environment or default to chrome_windows
            browser_type = os.getenv('BROWSER_TYPE', 'chrome_windows')
            browser_config = BROWSER_CONFIGS.get(browser_type, BROWSER_CONFIGS['chrome_windows'])
            
            print(f"[Demo] Browser type: {browser_type}")
            print(f"[Demo] Browser config: {browser_config}")
            
            if BrowserStackDriverConfig.should_use_browserstack():
                print(f"[Demo] Creating BrowserStack driver for {browser_type}")
                try:
                    driver = BrowserStackDriverConfig.create_browserstack_driver(browser_config)
                    print(f"[Demo] ✅ BrowserStack driver created successfully")
                except Exception as e:
                    print(f"[Demo] Failed to create BrowserStack driver: {e}")
                    print(f"[Demo] Falling back to local Chrome driver")
                    driver = self._create_local_chrome_driver()
            else:
                print(f"[Demo] Creating local Chrome driver (BrowserStack not configured)")
                driver = self._create_local_chrome_driver()
        
        yield driver
        
        # Update BrowserStack session status before cleanup
        self._update_browserstack_status(driver)
        
        # Cleanup
        driver.quit()
    
    def _create_local_chrome_driver(self):
        """Create a local Chrome driver for testing."""
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
        
        return driver
    
    def _update_browserstack_status(self, driver):
        """Update BrowserStack session status based on test outcome."""
        if not self.browserstack_api or not hasattr(driver, 'session_id'):
            self.logger.warning("[Demo] Cannot update BrowserStack status - missing API or session ID")
            return
        
        # Check if this is actually a BrowserStack session using cached value
        if not self.is_browserstack_session:
            self.logger.info("[Demo] Local driver session - skipping BrowserStack status update")
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
    
    def _is_browserstack_session(self, driver):
        """Check if the driver is running on BrowserStack."""
        try:
            # BrowserStack sessions have specific capabilities
            capabilities = driver.capabilities
            
            # Check for BrowserStack-specific capability keys
            browserstack_indicators = [
                'browserstack.user',
                'browserstack.key', 
                'bstack:options',
                'browserstack:options'
            ]
            
            for indicator in browserstack_indicators:
                if indicator in capabilities:
                    return True
                    
            # Check if the session URL contains browserstack
            if hasattr(driver, 'command_executor') and driver.command_executor:
                executor_url = str(driver.command_executor.remote_server_addr)
                if 'browserstack' in executor_url.lower():
                    return True
                    
            return False
            
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.warning(f"[Demo] Could not determine if session is BrowserStack: {e}")
            else:
                print(f"[Demo] Could not determine if session is BrowserStack: {e}")
            return False
    
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
        
        # Immediate update if session is available and it's a BrowserStack session
        if (self.session_id and self.browserstack_api and self.is_browserstack_session):
            success = self.browserstack_api.update_session_status(self.session_id, "passed", reason)
            if not success:
                self.logger.warning(f"[Demo] Failed to immediately update BrowserStack status, will retry in teardown")
    
    def mark_test_failed(self, reason="Test failed"):
        """Manually mark test as failed for BrowserStack reporting."""
        self.test_failed = True
        self.test_passed = False
        self.failure_reason = reason
        self.logger.error(f"[Demo] Marked test as FAILED: {reason}")
        
        # Immediate update if session is available and it's a BrowserStack session
        if (self.session_id and self.browserstack_api and self.is_browserstack_session):
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
        if not self.session_id or not self.browserstack_api or not self.is_browserstack_session:
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