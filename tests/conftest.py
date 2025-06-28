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
    
    # Debug what we have
    print(f"=== CONFTEST DEBUG ===")
    print(f"BROWSERSTACK_USERNAME: {bool(os.environ.get('BROWSERSTACK_USERNAME'))}")
    print(f"BROWSERSTACK_ACCESS_KEY: {bool(os.environ.get('BROWSERSTACK_ACCESS_KEY'))}")
    print(f"BROWSER_TYPE: {os.environ.get('BROWSER_TYPE', 'not-set')}")
    print(f"BS_BROWSER: {os.environ.get('BS_BROWSER', 'not-set')}")
    print(f"BS_DEVICE: {os.environ.get('BS_DEVICE', 'not-set')}")
    
    # Check for BrowserStack credentials
    username = os.environ.get('BROWSERSTACK_USERNAME')
    access_key = os.environ.get('BROWSERSTACK_ACCESS_KEY')
    browser_type = os.environ.get('BROWSER_TYPE', 'chrome_windows')
    
    # Use BrowserStack if credentials are available
    if username and access_key:
        print(f"=== USING BROWSERSTACK for {browser_type} ===")
        
        options = ChromeOptions()
        bstack_options = {
            'buildName': f"Demo-Build-{os.environ.get('BUILD_NUMBER', 'local')}",
            'sessionName': f'Demo-{browser_type}-{request.node.name}',
            'local': 'false',
            'debug': 'true',
            'consoleLogs': 'info',
            'networkLogs': 'true'
        }
        
        # Configure based on browser type
        if browser_type == 'samsung_mobile':
            bstack_options['deviceName'] = 'Samsung Galaxy S20'
            bstack_options['osVersion'] = '10.0'
            bstack_options['realMobile'] = 'true'
            options.set_capability('browserName', 'chrome')
        elif browser_type == 'firefox_mac':
            bstack_options['os'] = 'OS X'
            bstack_options['osVersion'] = 'Ventura'
            options.set_capability('browserName', 'Firefox')
            options.set_capability('browserVersion', 'latest')
        else:  # chrome_windows
            bstack_options['os'] = 'Windows'
            bstack_options['osVersion'] = '10'
            options.set_capability('browserName', 'Chrome')
            options.set_capability('browserVersion', 'latest')
        
        options.set_capability('bstack:options', bstack_options)
        
        print(f"Connecting to BrowserStack with: {bstack_options}")
        
        driver = webdriver.Remote(
            command_executor=f'https://{username}:{access_key}@hub-cloud.browserstack.com/wd/hub',
            options=options
        )
        
        print(f"✅ BrowserStack driver created: {driver.session_id}")
    else:
        print("=== USING LOCAL CHROME (no BrowserStack credentials) ===")
        # Local Chrome driver setup
        options = ChromeOptions()
        options.add_argument("--remote-allow-origins=*")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        print(f"Local Chrome driver created: {driver.session_id}")
    
    yield driver
    driver.quit()