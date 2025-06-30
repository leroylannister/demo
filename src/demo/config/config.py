"""Configuration management for Demo test suite."""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Central configuration for Demo test suite."""
    
    # Project info
    PROJECT_NAME = "Demo"
    
    # URLs
    BASE_URL = os.getenv("BASE_URL", "https://www.bstackdemo.com")
    
    # BrowserStack Configuration
    BROWSERSTACK_USERNAME = os.getenv("BROWSERSTACK_USERNAME")
    BROWSERSTACK_ACCESS_KEY = os.getenv("BROWSERSTACK_ACCESS_KEY")
    BROWSERSTACK_HUB_URL = "https://hub-cloud.browserstack.com/wd/hub"
    
    # Test Credentials
    TEST_USERNAME = os.getenv("TEST_USERNAME", "demouser")
    TEST_PASSWORD = os.getenv("TEST_PASSWORD", "testingisfun99")
    
    # Browser Configuration
    BROWSER_TYPE = os.getenv("BROWSER_TYPE", "chrome_windows")
    IMPLICIT_WAIT = int(os.getenv("IMPLICIT_WAIT", "10"))
    EXPLICIT_WAIT = int(os.getenv("EXPLICIT_WAIT", "10"))
    
    # Test Configuration
    PARALLEL_EXECUTION = os.getenv("PARALLEL_EXECUTION", "true").lower() == "true"
    TEST_TIMEOUT = int(os.getenv("TEST_TIMEOUT", "300"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_TO_FILE = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    LOG_DIR = Path("logs")
    
    # Reporting
    REPORTS_DIR = Path("reports")
    SCREENSHOTS_DIR = Path("screenshots")
    
    # Browser Configurations for BrowserStack
    BROWSER_CONFIGS: Dict[str, Dict[str, Any]] = {
        "chrome_windows": {
            "browserName": "Chrome",
            "browserVersion": "latest",
            "os": "Windows",
            "osVersion": "10",
            "sessionName": "Chrome on Windows 10"
        },
        "firefox_mac": {
            "browserName": "Firefox",
            "browserVersion": "latest",
            "os": "OS X",
            "osVersion": "Ventura",
            "sessionName": "Firefox on macOS Ventura"
        },
        "samsung_mobile": {
            "deviceName": "Samsung Galaxy S22",
            "platformName": "Android",
            "platformVersion": "12.0",
            "sessionName": "Samsung Galaxy S22",
            "realMobile": "true"
        }
    }
    
    @classmethod
    def is_browserstack_enabled(cls) -> bool:
        """Check if BrowserStack credentials are configured."""
        return bool(cls.BROWSERSTACK_USERNAME and cls.BROWSERSTACK_ACCESS_KEY)
    
    @classmethod
    def get_browser_config(cls, browser_type: str = None) -> Dict[str, Any]:
        """Get browser configuration for specified type."""
        browser_type = browser_type or cls.BROWSER_TYPE
        return cls.BROWSER_CONFIGS.get(browser_type, cls.BROWSER_CONFIGS["chrome_windows"])
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories for logs, reports, and screenshots."""
        for directory in [cls.LOG_DIR, cls.REPORTS_DIR, cls.SCREENSHOTS_DIR]:
            directory.mkdir(exist_ok=True)