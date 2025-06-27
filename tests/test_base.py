"""Base test class for Demo test suite."""

import pytest
from typing import Optional
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
        
        # Cleanup
        driver.quit()
    
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