"""BrowserStack capability configurations for Demo test suite."""

from typing import Dict, Any
from datetime import datetime


class BrowserStackConfig:
    """BrowserStack capability configurations for Demo tests."""
    
    COMMON_CAPS: Dict[str, Any] = {
        "browserstack.debug": "true",
        "browserstack.console": "verbose",
        "browserstack.networkLogs": "true",
        "acceptSslCerts": "true",
        "build": "Demo Test Suite Build",
        "project": "Demo - BStackDemo Tests",
        "browserstack.selenium_version": "4.0.0",
    }
    
    BROWSER_CAPS: Dict[str, Dict[str, Any]] = {
        "chrome_windows": {
            "os": "Windows",
            "os_version": "10",
            "browser": "Chrome",
            "browser_version": "latest",
            "resolution": "1920x1080",
            "name": "Demo - Chrome Windows Test",
        },
        "firefox_mac": {
            "os": "OS X",
            "os_version": "Ventura",
            "browser": "Firefox",
            "browser_version": "latest",
            "resolution": "1920x1080",
            "name": "Demo - Firefox Mac Test",
        },
        "samsung_mobile": {
            "device": "Samsung Galaxy S22",
            "real_mobile": "true",
            "os_version": "12.0",
            "name": "Demo - Samsung Galaxy S22 Test",
        },
    }
    
    @classmethod
    def get_capabilities(cls, browser_name: str) -> Dict[str, Any]:
        """Get capabilities for specific browser in Demo suite."""
        caps = cls.COMMON_CAPS.copy()
        browser_caps = cls.BROWSER_CAPS.get(browser_name, {})
        caps.update(browser_caps)
        
        # Add timestamp to build name for uniqueness
        caps["build"] = f"Demo - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return caps