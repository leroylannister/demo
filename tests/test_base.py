"""Base test class for Demo test suite."""

import pytest
from typing import Optional
from pathlib import Path

from src.demo.utils.logger import get_logger


class TestBase:
    """Base test class with common functionality for Demo tests."""
    
    driver = None
    logger = None
    
    @pytest.fixture(autouse=True)
    def setup_method(self, driver):
        """Setup for each Demo test method."""
        self.driver = driver
        self.logger = get_logger(f"Demo.{self.__class__.__name__}")
    
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