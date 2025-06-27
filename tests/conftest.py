"""
Pytest configuration for BrowserStack integration.
This file handles the WebDriver setup based on environment variables.
"""
import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


@pytest.fixture(scope="function")
def driver(request):
    """
    Create a WebDriver instance for BrowserStack based on environment variables.
    
    Environment variables used:
    - BROWSERSTACK_USERNAME: BrowserStack username
    - BROWSERSTACK_ACCESS_KEY: BrowserStack access key
    - BS_BROWSER: Browser name (for desktop)
    - BS_BROWSER_VERSION: Browser version (for desktop)
    - BS_OS: Operating system (for desktop)
    - BS_OS_VERSION: OS version (for desktop)
    - BS_DEVICE: Device name (for mobile)
    - BS_PLATFORM_NAME: Platform name (for mobile)
    - BS_PLATFORM_VERSION: Platform version (for mobile)
    - BROWSERSTACK_BUILD_NAME: Build name for grouping tests
    - BROWSERSTACK_PROJECT_NAME: Project name
    - BROWSERSTACK_SESSION_NAME: Session name
    """
    # Get BrowserStack credentials
    username = os.environ.get('BROWSERSTACK_USERNAME')
    access_key = os.environ.get('BROWSERSTACK_ACCESS_KEY')
    
    if not username or not access_key:
        pytest.skip("BrowserStack credentials not found in environment variables")
    
    # Base capabilities
    desired_caps = {
        'browserstack.local': 'false',
        'browserstack.debug': 'true',
        'browserstack.console': 'info',
        'browserstack.networkLogs': 'true',
        'acceptSslCerts': 'true',
        'build': os.environ.get('BROWSERSTACK_BUILD_NAME', 'Local Build'),
        'project': os.environ.get('BROWSERSTACK_PROJECT_NAME', 'Demo Project'),
        'name': os.environ.get('BROWSERSTACK_SESSION_NAME', 'Test Session')
    }
    
    # Check if this is a mobile or desktop test
    if os.environ.get('BS_DEVICE'):
        # Mobile configuration
        desired_caps.update({
            'device': os.environ.get('BS_DEVICE'),
            'os_version': os.environ.get('BS_PLATFORM_VERSION'),
            'real_mobile': 'true',
            'browserstack.appium_version': '1.22.0'
        })
        
        # Set platform name for mobile
        platform_name = os.environ.get('BS_PLATFORM_NAME', 'Android')
        if platform_name.lower() == 'ios':
            desired_caps['platformName'] = 'iOS'
        else:
            desired_caps['platformName'] = 'Android'
    else:
        # Desktop configuration
        browser = os.environ.get('BS_BROWSER', 'Chrome')
        browser_version = os.environ.get('BS_BROWSER_VERSION', 'latest')
        os_name = os.environ.get('BS_OS', 'Windows')
        os_version = os.environ.get('BS_OS_VERSION', '10')
        
        desired_caps.update({
            'browser': browser,
            'browser_version': browser_version,
            'os': os_name,
            'os_version': os_version,
            'resolution': '1920x1080'
        })
    
    # Create the remote WebDriver
    driver = webdriver.Remote(
        command_executor=f'https://{username}:{access_key}@hub-cloud.browserstack.com/wd/hub',
        desired_capabilities=desired_caps
    )
    
    # Set implicit wait
    driver.implicitly_wait(10)
    
    # Maximize window for desktop browsers
    if not os.environ.get('BS_DEVICE'):
        driver.maximize_window()
    
    # Add the driver to the test item for access in tests
    request.cls.driver = driver if hasattr(request, 'cls') else None
    
    yield driver
    
    # Teardown
    try:
        # Mark test status in BrowserStack
        if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
            driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "Test failed"}}'
            )
        else:
            driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Test passed"}}'
            )
    except Exception:
        pass
    finally:
        driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to add test result to the request node for BrowserStack status updates.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_configure(config):
    """
    Configure pytest with custom markers.
    """
    config.addinivalue_line(
        "markers", "smoke: mark test as a smoke test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as a regression test"
    )


# Optional: Add screenshot capture on failure
@pytest.fixture(autouse=True)
def screenshot_on_failure(request, driver):
    """
    Automatically capture screenshot on test failure.
    """
    yield
    
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        try:
            # Create screenshots directory if it doesn't exist
            os.makedirs('screenshots', exist_ok=True)
            
            # Generate screenshot filename
            test_name = request.node.name
            screenshot_name = f"screenshots/{test_name}_failure.png"
            
            # Capture and save screenshot
            driver.save_screenshot(screenshot_name)
            print(f"Screenshot saved: {screenshot_name}")
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")