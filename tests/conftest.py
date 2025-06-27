"""Pytest configuration and fixtures for Demo test suite with BrowserStack support."""

import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.chrome.service import Service
import sys
import platform

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    USE_WEBDRIVER_MANAGER = True
except ImportError:
    USE_WEBDRIVER_MANAGER = False

from src.demo.utils.logger import get_logger

logger = get_logger("Demo.conftest")


def pytest_addoption(parser):
    """Add command line options for Demo tests."""
    parser.addoption(
        "--test-browser",
        action="store", 
        default="chrome_local",
        help="Browser to run Demo tests on (for local testing)"
    )
  
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode (local only)"
    )
    
    parser.addoption(
        "--local",
        action="store_true",
        default=False,
        help="Force local execution instead of BrowserStack"
    )


@pytest.fixture
def driver(request):
    """Setup and teardown driver for Demo tests."""
    # Check if we're running on BrowserStack (via environment variables from Jenkins)
    bs_browser = os.environ.get('BS_BROWSER')
    bs_device = os.environ.get('BS_DEVICE')
    
    # Determine if this is a BrowserStack run
    is_browserstack = bool(bs_browser or bs_device)
    is_local = request.config.getoption("--local") or not is_browserstack
    
    print(f"\n[Demo] Platform: {platform.system()} {platform.machine()}")
    
    if is_local:
        # Local execution
        browser = request.config.getoption("--test-browser")
        is_headless = request.config.getoption("--headless")
        print(f"[Demo] Setting up local {browser} driver...")
        driver = _create_local_driver(browser, is_headless)
    else:
        # BrowserStack execution
        print(f"[Demo] Setting up BrowserStack driver...")
        try:
            driver = _create_browserstack_driver(request)
        except Exception as e:
            print(f"[Demo] BrowserStack error: {e}")
            print("[Demo] Falling back to local Chrome driver...")
            driver = _create_local_driver("chrome_local", False)
    
    driver.implicitly_wait(10)
    
    # Maximize window for desktop browsers
    if not bs_device:
        try:
            driver.maximize_window()
        except:
            pass  # Some browsers/configs don't support maximize
    
    print("[Demo] Driver ready!")
    
    yield driver
    
    # Cleanup
    print("[Demo] Closing driver...")
    driver.quit()


def _create_local_driver(browser="chrome_local", is_headless=False):
    """Create local driver."""
    browser_name = browser.replace("_local", "").lower()
    
    if browser_name == "chrome":
        options = ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        if is_headless:
            options.add_argument("--headless=new")
        
        try:
            if USE_WEBDRIVER_MANAGER:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            else:
                driver = webdriver.Chrome(options=options)
        except Exception as e:
            print(f"[Demo] Error creating Chrome driver: {e}")
            raise
            
    elif browser_name == "firefox":
        options = FirefoxOptions()
        
        if is_headless:
            options.add_argument("--headless")
        
        try:
            if USE_WEBDRIVER_MANAGER:
                service = Service(GeckoDriverManager().install())
                driver = webdriver.Firefox(service=service, options=options)
            else:
                driver = webdriver.Firefox(options=options)
        except Exception as e:
            print(f"[Demo] Error creating Firefox driver: {e}")
            raise
            
    elif browser_name == "edge":
        options = EdgeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        if is_headless:
            options.add_argument("--headless")
        
        try:
            if USE_WEBDRIVER_MANAGER:
                service = Service(EdgeChromiumDriverManager().install())
                driver = webdriver.Edge(service=service, options=options)
            else:
                driver = webdriver.Edge(options=options)
        except Exception as e:
            print(f"[Demo] Error creating Edge driver: {e}")
            raise
            
    elif browser_name == "safari":
        # Safari doesn't support many options and doesn't need driver manager
        options = SafariOptions()
        try:
            driver = webdriver.Safari(options=options)
        except Exception as e:
            print(f"[Demo] Error creating Safari driver: {e}")
            print("[Demo] Make sure Safari's 'Allow Remote Automation' is enabled in Developer menu")
            raise
    else:
        raise ValueError(f"Unsupported browser: {browser}")
    
    return driver


def _create_browserstack_driver(request):
    """Create BrowserStack driver based on environment variables."""
    # Get BrowserStack credentials
    username = os.environ.get('BROWSERSTACK_USERNAME')
    access_key = os.environ.get('BROWSERSTACK_ACCESS_KEY')
    
    if not username or not access_key:
        raise ValueError("BrowserStack credentials not found in environment variables")
    
    # BrowserStack hub URL
    hub_url = f'https://{username}:{access_key}@hub-cloud.browserstack.com/wd/hub'
    
    # Base BrowserStack capabilities
    bstack_options = {
        'buildName': os.environ.get('BROWSERSTACK_BUILD_NAME', f'Demo Build {os.environ.get("BUILD_NUMBER", "Local")}'),
        'projectName': os.environ.get('BROWSERSTACK_PROJECT_NAME', 'Demo Project'),
        'sessionName': f'Demo - {request.node.name}',
        'debug': 'true',
        'consoleLogs': 'info',
        'networkLogs': 'true',
        'local': 'false'
    }
    
    # Check if this is a mobile or desktop test
    if os.environ.get('BS_DEVICE'):
        # Mobile configuration
        device_name = os.environ.get('BS_DEVICE')
        platform_name = os.environ.get('BS_PLATFORM_NAME', 'Android')
        platform_version = os.environ.get('BS_PLATFORM_VERSION')
        
        bstack_options.update({
            'deviceName': device_name,
            'osVersion': platform_version,
            'realMobile': 'true',
            'appiumVersion': '1.22.0'
        })
        
        # Create mobile options based on platform
        if platform_name.lower() == 'ios':
            # For iOS, we need to use Safari options
            options = SafariOptions()
            options.platform_name = 'iOS'
        else:
            # For Android, we use Chrome options
            options = ChromeOptions()
            options.platform_name = 'Android'
        
        # Set BrowserStack options
        options.set_capability('bstack:options', bstack_options)
        
    else:
        # Desktop configuration
        browser = os.environ.get('BS_BROWSER', 'Chrome').lower()
        browser_version = os.environ.get('BS_BROWSER_VERSION', 'latest')
        os_name = os.environ.get('BS_OS', 'Windows')
        os_version = os.environ.get('BS_OS_VERSION', '10')
        
        # Update BrowserStack options for desktop
        bstack_options.update({
            'os': os_name,
            'osVersion': os_version,
            'browserVersion': browser_version,
            'resolution': '1920x1080'
        })
        
        # Create browser-specific options
        if browser == 'chrome':
            options = ChromeOptions()
            options.browser_version = browser_version
            options.add_argument("--disable-blink-features=AutomationControlled")
            
        elif browser == 'firefox':
            options = FirefoxOptions()
            options.browser_version = browser_version
            
        elif browser == 'edge':
            options = EdgeOptions()
            options.browser_version = browser_version
            options.add_argument("--disable-blink-features=AutomationControlled")
            
        elif browser == 'safari':
            options = SafariOptions()
            options.browser_version = browser_version
        else:
            raise ValueError(f"Unsupported browser: {browser}")
        
        # Set BrowserStack options
        options.set_capability('bstack:options', bstack_options)
    
    # Create the driver
    print(f"[Demo] Connecting to BrowserStack...")
    driver = webdriver.Remote(command_executor=hub_url, options=options)
    
    # Log BrowserStack session URL
    session_id = driver.session_id
    session_url = f"https://automate.browserstack.com/dashboard/v2/sessions/{session_id}"
    print(f"[Demo] BrowserStack session: {session_url}")
    logger.info(f"BrowserStack session: {session_url}")
    
    return driver


@pytest.fixture(autouse=True)
def browserstack_test_status(request, driver):
    """Mark test status in BrowserStack after completion."""
    yield
    
    # Only update status for BrowserStack sessions
    if hasattr(driver, 'session_id') and (os.environ.get('BS_BROWSER') or os.environ.get('BS_DEVICE')):
        try:
            if hasattr(request.node, 'rep_call'):
                status = "passed" if request.node.rep_call.passed else "failed"
                reason = "" if request.node.rep_call.passed else str(request.node.rep_call.longrepr)[:255]
            else:
                status = "passed"
                reason = "Test completed"
            
            # Update test status in BrowserStack
            script = f'browserstack_executor: {{"action": "setSessionStatus", "arguments": {{"status":"{status}", "reason": "{reason}"}}}}'
            driver.execute_script(script)
        except Exception as e:
            # Log but don't fail on status update errors
            logger.warning(f"Failed to update BrowserStack status: {e}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Make test result available to fixtures."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(autouse=True)
def screenshot_on_failure(request, driver):
    """Automatically capture screenshot on test failure."""
    yield
    
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        try:
            # Create screenshots directory if it doesn't exist
            os.makedirs('screenshots', exist_ok=True)
            
            # Generate screenshot filename
            test_name = request.node.name.replace("/", "_").replace("::", "_")
            screenshot_name = f"screenshots/{test_name}_failure.png"
            
            # Capture and save screenshot
            driver.save_screenshot(screenshot_name)
            print(f"[Demo] Screenshot saved: {screenshot_name}")
            logger.info(f"Screenshot saved: {screenshot_name}")
        except Exception as e:
            print(f"[Demo] Failed to capture screenshot: {e}")
            logger.error(f"Failed to capture screenshot: {e}")


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "smoke: mark test as a smoke test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as a regression test"
    )
    config.addinivalue_line(
        "markers", "critical: mark test as critical"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )