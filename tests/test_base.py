"""Base test class for Demo test suite."""

import pytest
import logging
from pathlib import Path
from typing import Optional

from src.demo.config.config import Config
from src.demo.utils.browserstack_api import BrowserStackAPI

logger = logging.getLogger(__name__)


class TestBase:
    """Base test class with common functionality for Demo tests."""
    
    driver = None
    browserstack_api = None
    test_passed = True
    failure_reason = None
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, driver, request):
        """Setup and teardown for each test method."""
        self.driver = driver
        self.test_name = request.node.name
        self.browserstack_api = BrowserStackAPI()
        
        # Reset test status
        self.test_passed = True
        self.failure_reason = None
        
        logger.info(f"Starting test: {self.test_name}")
        
        yield
        
        # Update BrowserStack status if applicable
        if self._is_browserstack_session():
            self._update_browserstack_status()
    
    def _is_browserstack_session(self) -> bool:
        """Check if the current session is running on BrowserStack."""
        if not self.driver or not hasattr(self.driver, 'capabilities'):
            return False
        
        capabilities = self.driver.capabilities
        browserstack_indicators = [
            'browserstack.user',
            'browserstack.key',
            'bstack:options',
            'browserstack:options'
        ]
        
        return any(indicator in capabilities for indicator in browserstack_indicators)
    
    def _update_browserstack_status(self):
        """Update BrowserStack session status based on test outcome."""
        if not self.browserstack_api or not hasattr(self.driver, 'session_id'):
            return
        
        session_id = self.driver.session_id
        
        if self.test_passed:
            self.browserstack_api.update_session_status(
                session_id,
                "passed",
                f"Test {self.test_name} passed"
            )
        else:
            self.browserstack_api.update_session_status(
                session_id,
                "failed",
                self.failure_reason or f"Test {self.test_name} failed"
            )
    
    def mark_test_failed(self, reason: str):
        """Mark the current test as failed."""
        self.test_passed = False
        self.failure_reason = reason
        logger.error(f"Test marked as failed: {reason}")
    
    def take_screenshot(self, name: str) -> Optional[Path]:
        """Take a screenshot for debugging."""
        try:
            screenshot_path = Config.SCREENSHOTS_DIR / f"{self.test_name}_{name}.png"
            self.driver.save_screenshot(str(screenshot_path))
            logger.info(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
    
    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """Hook to capture pytest test outcomes."""
        outcome = yield
        report = outcome.get_result()
        
        if report.when == "call" and report.failed:
            self.mark_test_failed(str(report.longrepr))