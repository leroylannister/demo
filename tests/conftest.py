"""Pytest configuration for Demo tests with BrowserStack support."""
import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "smoke: mark test as a smoke test")
    config.addinivalue_line("markers", "regression: mark test as a regression test")
    config.addinivalue_line("markers", "critical: mark test as critical")

@pytest.fixture
def driver(request):
    """Setup and teardown driver for Demo tests."""
    # Check if we're running on BrowserStack via environment variables
    if os.environ.get('BS_BROWSER') or os.environ.get('BS_DEVICE'):
        # --- BrowserStack execution (unchanged) ---
        username = os.environ.get('BROWSERSTACK_USERNAME')
        access_key = os.environ.get('BROWSERSTACK_ACCESS_KEY')
        
        options = ChromeOptions()
        bstack_options = {
            'buildName': os.environ.get('BROWSERSTACK_BUILD_NAME', 'Demo Build'),
            'sessionName': f'Demo - {request.node.name}',
            'local': 'false',
            'debug': 'true'
        }
        
        if os.environ.get('BS_DEVICE'):
            bstack_options['deviceName'] = os.environ.get('BS_DEVICE')
            bstack_options['osVersion'] = os.environ.get('BS_PLATFORM_VERSION')
            bstack_options['realMobile'] = 'true'
        else:
            bstack_options['os'] = os.environ.get('BS_OS', 'Windows')
            bstack_options['osVersion'] = os.environ.get('BS_OS_VERSION', '10')
        
        options.set_capability('bstack:options', bstack_options)
        
        driver = webdriver.Remote(
            command_executor=f'https://{username}:{access_key}@hub-cloud.browserstack.com/wd/hub',
            options=options
        )
    else:
        # --- START: Applied Local Chrome Fixes ---
        # Local Chrome driver setup with robust options
        options = ChromeOptions()
        
        ### <<< KEY FIX HERE
        # This argument is essential for Chrome v111+ to allow WebDriver to connect.
        options.add_argument("--remote-allow-origins=*")
        
        # Best-practice options for stability and to avoid detection
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        # --- END: Applied Local Chrome Fixes ---
    
    yield driver
    driver.quit()

