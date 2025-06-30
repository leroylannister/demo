"""Pytest configuration for Demo tests."""

import pytest
import logging
from pathlib import Path

from src.demo.config.config import Config
from src.demo.utils.driver_factory import DriverFactory
from src.demo.utils.logger import setup_logger

# Create necessary directories
Config.create_directories()

# Setup logging
setup_logger()
logger = logging.getLogger(__name__)


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "smoke: mark test as a smoke test")
    config.addinivalue_line("markers", "regression: mark test as a regression test")
    config.addinivalue_line("markers", "critical: mark test as critical")


@pytest.fixture(scope="function")
def driver(request):
    """
    Setup and teardown WebDriver for each test.
    
    This fixture:
    - Creates appropriate driver (BrowserStack or local)
    - Handles cleanup after test
    - Logs test execution details
    """
    test_name = request.node.name
    logger.info(f"Starting test: {test_name}")
    
    # Create driver
    driver = DriverFactory.create_driver()
    
    # Log session details
    if hasattr(driver, 'session_id'):
        logger.info(f"Session ID: {driver.session_id}")
    
    yield driver
    
    # Cleanup
    try:
        driver.quit()
        logger.info(f"Test completed: {test_name}")
    except Exception as e:
        logger.error(f"Error during driver cleanup: {e}")


@pytest.fixture(scope="session")
def test_data():
    """Provide test data for all tests."""
    return {
        "username": Config.TEST_USERNAME,
        "password": Config.TEST_PASSWORD,
        "base_url": Config.BASE_URL,
        "product_name": "Galaxy S20+",
        "brand_filter": "Samsung"
    }


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test results and take screenshots on failure.
    """
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        # Get the driver from the test
        driver = item.funcargs.get('driver')
        if driver:
            # Take screenshot
            screenshot_name = f"{item.nodeid.replace('::', '_').replace('/', '_')}.png"
            screenshot_path = Config.SCREENSHOTS_DIR / screenshot_name
            
            try:
                driver.save_screenshot(str(screenshot_path))
                logger.info(f"Screenshot saved: {screenshot_path}")
            except Exception as e:
                logger.error(f"Failed to capture screenshot: {e}")