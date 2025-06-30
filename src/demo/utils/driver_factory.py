"""Driver factory for creating Selenium WebDriver instances."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Dict, Any
import logging

from ..config.config import Config

logger = logging.getLogger(__name__)


class DriverFactory:
    """Factory class for creating WebDriver instances."""
    
    @staticmethod
    def create_driver(use_browserstack: bool = None) -> WebDriver:
        """
        Create a WebDriver instance.
        
        Args:
            use_browserstack: Force BrowserStack usage. If None, auto-detect based on config.
            
        Returns:
            WebDriver instance
        """
        if use_browserstack is None:
            use_browserstack = Config.is_browserstack_enabled()
        
        if use_browserstack:
            return DriverFactory._create_browserstack_driver()
        else:
            return DriverFactory._create_local_driver()
    
    @staticmethod
    def _create_browserstack_driver() -> WebDriver:
        """Create a BrowserStack WebDriver instance."""
        browser_config = Config.get_browser_config()
        
        # Base capabilities
        options = ChromeOptions()
        
        # BrowserStack specific options
        bstack_options = {
            'buildName': f"Demo-Build-{os.environ.get('BUILD_NUMBER', 'local')}",
            'sessionName': browser_config.get('sessionName', 'Demo Test'),
            'local': 'false',
            'debug': 'true',
            'consoleLogs': 'info',
            'networkLogs': 'true'
        }
        
        # Add browser-specific capabilities
        if 'deviceName' in browser_config:
            # Mobile device
            bstack_options.update({
                'deviceName': browser_config['deviceName'],
                'osVersion': browser_config.get('platformVersion'),
                'realMobile': browser_config.get('realMobile', 'true')
            })
            options.set_capability('browserName', 'chrome')
        else:
            # Desktop browser
            bstack_options.update({
                'os': browser_config['os'],
                'osVersion': browser_config['osVersion']
            })
            
            browser_name = browser_config['browserName']
            if browser_name.lower() == 'firefox':
                options = FirefoxOptions()
            
            options.set_capability('browserName', browser_name)
            options.set_capability('browserVersion', browser_config.get('browserVersion', 'latest'))
        
        options.set_capability('bstack:options', bstack_options)
        
        # Create remote driver
        hub_url = f"https://{Config.BROWSERSTACK_USERNAME}:{Config.BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub"
        
        logger.info(f"Creating BrowserStack driver: {browser_config.get('sessionName')}")
        
        driver = webdriver.Remote(
            command_executor=hub_url,
            options=options
        )
        
        driver.implicitly_wait(Config.IMPLICIT_WAIT)
        return driver
    
    @staticmethod
    def _create_local_driver() -> WebDriver:
        """Create a local Chrome WebDriver instance."""
        chrome_options = ChromeOptions()
        
        # Essential options for stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Additional options for better compatibility
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # Set a realistic user agent
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        logger.info("Creating local Chrome driver")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        driver.implicitly_wait(Config.IMPLICIT_WAIT)
        driver.maximize_window()
        
        return driver