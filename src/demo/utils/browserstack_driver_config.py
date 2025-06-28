"""BrowserStack driver configuration for running tests on BrowserStack."""

import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class BrowserStackDriverConfig:
    """Configuration for BrowserStack drivers."""
    
    @staticmethod
    def get_browserstack_capabilities(browser_config):
        """Get BrowserStack capabilities based on browser configuration."""
        
        # Base capabilities
        capabilities = {
            'browserstack.user': os.getenv('BROWSERSTACK_USERNAME'),
            'browserstack.key': os.getenv('BROWSERSTACK_ACCESS_KEY'),
            'project': 'Demo Test Project',
            'build': f"Build #{os.getenv('BUILD_NUMBER', 'local')}",
            'name': f"Demo Test - {browser_config.get('browser', 'chrome')}",
            'browserstack.debug': 'true',
            'browserstack.console': 'info',
            'browserstack.networkLogs': 'true',
            'browserstack.seleniumLogs': 'true',
        }
        
        # Browser-specific configurations
        if browser_config['browser'] == 'chrome':
            capabilities.update({
                'browserName': 'Chrome',
                'browserVersion': browser_config.get('version', 'latest'),
                'os': browser_config.get('os', 'Windows'),
                'osVersion': browser_config.get('os_version', '10'),
            })
        elif browser_config['browser'] == 'firefox':
            capabilities.update({
                'browserName': 'Firefox',
                'browserVersion': browser_config.get('version', 'latest'),
                'os': browser_config.get('os', 'OS X'),
                'osVersion': browser_config.get('os_version', 'Monterey'),
            })
        elif browser_config['browser'] == 'samsung_mobile':
            capabilities.update({
                'browserName': 'chrome',
                'device': 'Samsung Galaxy S20',
                'realMobile': 'true',
                'osVersion': '10.0',
            })
        
        return capabilities
    
    @staticmethod
    def create_browserstack_driver(browser_config):
        """Create a BrowserStack WebDriver instance."""
        
        # Check if BrowserStack credentials are available
        username = os.getenv('BROWSERSTACK_USERNAME')
        access_key = os.getenv('BROWSERSTACK_ACCESS_KEY')
        
        if not username or not access_key:
            raise ValueError("BrowserStack credentials not found. Please set BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY environment variables.")
        
        # Get capabilities
        capabilities = BrowserStackDriverConfig.get_browserstack_capabilities(browser_config)
        
        # BrowserStack Hub URL
        hub_url = f"https://{username}:{access_key}@hub-cloud.browserstack.com/wd/hub"
        
        # Create remote driver
        driver = webdriver.Remote(
            command_executor=hub_url,
            desired_capabilities=capabilities
        )
        
        # Set implicit wait
        driver.implicitly_wait(10)
        
        return driver
    
    @staticmethod
    def should_use_browserstack():
        """Determine if tests should run on BrowserStack."""
        # Run on BrowserStack if credentials are available and not explicitly disabled
        return (
            os.getenv('BROWSERSTACK_USERNAME') and 
            os.getenv('BROWSERSTACK_ACCESS_KEY') and
            os.getenv('USE_BROWSERSTACK', 'true').lower() != 'false'
        )


# Browser configurations for different test environments
BROWSER_CONFIGS = {
    'chrome_windows': {
        'browser': 'chrome',
        'os': 'Windows',
        'os_version': '10',
        'version': 'latest'
    },
    'firefox_mac': {
        'browser': 'firefox',
        'os': 'OS X',
        'os_version': 'Monterey',
        'version': 'latest'
    },
    'samsung_mobile': {
        'browser': 'samsung_mobile',
    }
}