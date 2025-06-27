"""Pytest configuration and fixtures for Demo test suite with BrowserStack support."""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service
import sys
import platform

try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WEBDRIVER_MANAGER = True
except ImportError:
    USE_WEBDRIVER_MANAGER = False

from src.demo.config.config import Config
from src.demo.config.browserstack_config import BrowserStackConfig
from src.demo.utils.logger import get_logger

logger = get_logger("Demo.conftest")


def pytest_addoption(parser):
    """Add command line options for Demo tests."""
    parser.addoption(
        "--test-browser",  # Changed from --browser to avoid conflicts
        action="store", 
        default="chrome_local",
        choices=["chrome_windows", "firefox_mac", "samsung_mobile", "chrome_local"],
        help="Browser to run Demo tests on"
    )
    parser.addoption(
        "--local",
        action="store_true",
        default=False,
        help="Run Demo tests locally instead of BrowserStack"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode (local only)"
    )


@pytest.fixture
def driver(request):
    """Setup and teardown driver for Demo tests."""
    browser = request.config.getoption("--test-browser")  # Updated parameter name
    is_local = request.config.getoption("--local") or browser == "chrome_local"
    is_headless = request.config.getoption("--headless")
    
    print(f"\n[Demo] Platform: {platform.system()} {platform.machine()}")
    
    if is_local:
        print(f"[Demo] Setting up local Chrome driver...")
        driver = _create_local_driver(is_headless)
    else:
        print(f"[Demo] Setting up BrowserStack driver for {browser}...")
        try:
            Config.validate_config()  # Ensure BrowserStack credentials are set
            driver = _create_browserstack_driver(browser, request)
        except ValueError as e:
            print(f"[Demo] BrowserStack configuration error: {e}")
            print("[Demo] Falling back to local Chrome driver...")
            driver = _create_local_driver(is_headless)
    
    driver.implicitly_wait(10)
    
    # Maximize window for desktop browsers
    if "mobile" not in browser:
        driver.maximize_window()
    
    print("[Demo] Driver ready!")
    
    yield driver
    
    # Cleanup
    print("[Demo] Closing driver...")
    driver.quit()


def _create_local_driver(is_headless=False):
    """Create local Chrome driver with your existing configuration."""
    # Chrome options - keeping your existing options
    options = ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Add headless option if requested
    if is_headless:
        options.add_argument("--headless=new")
    
    try:
        if USE_WEBDRIVER_MANAGER:
            # Use webdriver-manager to handle driver installation
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        else:
            # Try default Chrome
            driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"[Demo] Error creating Chrome driver: {e}")
        print("[Demo] Make sure Chrome browser is installed")
        raise
    
    return driver


def _create_browserstack_driver(browser, request):
    """Create BrowserStack driver."""
    # Get capabilities for the specified browser
    capabilities = BrowserStackConfig.get_capabilities(browser)
    
    # Add test name to capabilities
    test_name = request.node.name
    capabilities["name"] = f"Demo - {test_name}"
    
    # BrowserStack hub URL
    hub_url = f"https://{Config.BROWSERSTACK_USERNAME}:{Config.BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub"
    
    print(f"[Demo] Connecting to BrowserStack...")
    
    try:
        # Create driver based on browser type
        if browser == "chrome_windows":
            options = ChromeOptions()
            # Apply your Chrome options to BrowserStack as well
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.set_capability('bstack:options', capabilities)
            driver = webdriver.Remote(command_executor=hub_url, options=options)
        elif browser == "firefox_mac":
            options = FirefoxOptions()
            options.set_capability('bstack:options', capabilities)
            driver = webdriver.Remote(command_executor=hub_url, options=options)
        elif browser == "samsung_mobile":
            # For mobile, use the capabilities directly
            driver = webdriver.Remote(command_executor=hub_url, desired_capabilities=capabilities)
        else:
            raise ValueError(f"Unsupported browser: {browser}")
        
        # Log BrowserStack session URL
        session_id = driver.session_id
        print(f"[Demo] BrowserStack session: https://automate.browserstack.com/dashboard/v2/sessions/{session_id}")
        logger.info(f"[Demo] BrowserStack session: https://automate.browserstack.com/dashboard/v2/sessions/{session_id}")
        
        return driver
        
    except Exception as e:
        print(f"[Demo] Error creating BrowserStack driver: {e}")
        raise


@pytest.fixture(autouse=True)
def browserstack_test_status(request, driver):
    """Mark test status in BrowserStack after completion."""
    yield
    
    # Only update status for BrowserStack sessions
    if hasattr(driver, 'session_id') and not (request.config.getoption("--local") or request.config.getoption("--test-browser") == "chrome_local"):
        try:
            status = "passed" if request.node.rep_call.passed else "failed"
            reason = "" if request.node.rep_call.passed else str(request.node.rep_call.longrepr)
            
            # Update test status in BrowserStack
            driver.execute_script(
                f'browserstack_executor: {{"action": "setSessionStatus", "arguments": {{"status":"{status}", "reason": "{reason[:255]}"}}}}'
            )
        except:
            # Ignore errors in status update
            pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Make test result available to fixtures."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)