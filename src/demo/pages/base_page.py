"""Base page class for all page objects."""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

from ..config.config import Config

logger = logging.getLogger(__name__)


class BasePage:
    """Base class for all page objects."""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, Config.EXPLICIT_WAIT)
    
    def navigate_to(self, url: str = None):
        """Navigate to specified URL or base URL."""
        url = url or Config.BASE_URL
        logger.info(f"Navigating to: {url}")
        self.driver.get(url)
    
    def find_element(self, by: By, value: str, timeout: int = None):
        """Find element with explicit wait."""
        timeout = timeout or Config.EXPLICIT_WAIT
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.error(f"Element not found: {by}={value}")
            raise
    
    def find_clickable_element(self, by: By, value: str, timeout: int = None):
        """Find clickable element with explicit wait."""
        timeout = timeout or Config.EXPLICIT_WAIT
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            logger.error(f"Clickable element not found: {by}={value}")
            raise
    
    def find_elements(self, by: By, value: str):
        """Find multiple elements."""
        return self.driver.find_elements(by, value)
    
    def click_element(self, by: By, value: str, timeout: int = None):
        """Find and click element."""
        element = self.find_clickable_element(by, value, timeout)
        logger.debug(f"Clicking element: {by}={value}")
        element.click()
    
    def enter_text(self, by: By, value: str, text: str, timeout: int = None):
        """Find element and enter text."""
        element = self.find_element(by, value, timeout)
        element.clear()
        element.send_keys(text)
        logger.debug(f"Entered text in element: {by}={value}")
    
    def is_element_visible(self, by: By, value: str, timeout: int = 5):
        """Check if element is visible."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            return False
    
    def wait_for_element_to_disappear(self, by: By, value: str, timeout: int = None):
        """Wait for element to disappear."""
        timeout = timeout or Config.EXPLICIT_WAIT
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((by, value))
        )
    
    def get_element_text(self, by: By, value: str, timeout: int = None):
        """Get text from element."""
        element = self.find_element(by, value, timeout)
        return element.text
    
    def scroll_to_element(self, element):
        """Scroll element into view."""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
    
    def take_screenshot(self, name: str):
        """Take a screenshot."""
        screenshot_path = Config.SCREENSHOTS_DIR / f"{name}.png"
        self.driver.save_screenshot(str(screenshot_path))
        logger.info(f"Screenshot saved: {screenshot_path}")
        return screenshot_path