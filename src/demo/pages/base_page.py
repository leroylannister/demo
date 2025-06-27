"""Base page class for Demo test suite."""

from typing import Tuple, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

from ..config.config import Config
from ..utils.logger import get_logger


class BasePage:
    """Base page class with common functionality for Demo tests."""
    
    def __init__(self, driver: WebDriver) -> None:
        """Initialize base page for Demo."""
        self.driver = driver
        self.logger = get_logger(f"Demo.{self.__class__.__name__}")
        self.wait = WebDriverWait(driver, Config.DEFAULT_TIMEOUT)
    
    def navigate_to(self, url: str) -> None:
        """Navigate to specified URL."""
        self.logger.info(f"[Demo] Navigating to: {url}")
        self.driver.get(url)
    
    def find_element(self, locator: Tuple[str, str]) -> WebElement:
        """Find element with explicit wait."""
        try:
            self.logger.debug(f"[Demo] Finding element: {locator}")
            element = self.wait.until(EC.presence_of_element_located(locator))
            return element
        except TimeoutException:
            self.logger.error(f"[Demo] Element not found: {locator}")
            self.take_screenshot(f"demo_element_not_found_{locator[1]}")
            raise
    
    def find_clickable_element(self, locator: Tuple[str, str]) -> WebElement:
        """Find clickable element with explicit wait."""
        try:
            element = self.wait.until(EC.element_to_be_clickable(locator))
            return element
        except TimeoutException:
            self.logger.error(f"[Demo] Element not clickable: {locator}")
            raise
    
    def click(self, locator: Tuple[str, str]) -> None:
        """Click on element."""
        element = self.find_clickable_element(locator)
        self.logger.info(f"[Demo] Clicking element: {locator}")
        try:
            element.click()
        except ElementClickInterceptedException:
            # If regular click fails, try JavaScript click
            self.logger.warning(f"[Demo] Regular click failed, trying JavaScript click: {locator}")
            self.driver.execute_script("arguments[0].click();", element)
    
    def is_element_visible(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> bool:
        """Check if element is visible."""
        try:
            wait_time = timeout or Config.DEFAULT_TIMEOUT
            WebDriverWait(self.driver, wait_time).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    
    def is_element_displayed(self, locator: Tuple[str, str]) -> bool:
        """Check if element is displayed (following BrowserStack pattern)."""
        try:
            element = self.find_element(locator)
            return element.is_displayed()
        except:
            return False
    
    def wait_for_page_load(self) -> None:
        """Wait for page to load completely."""
        self.wait.until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        self.logger.debug("[Demo] Page loaded completely")
    
    def take_screenshot(self, name: str) -> None:
        """Take screenshot for debugging."""
        try:
            from pathlib import Path
            screenshot_dir = Path("screenshots")
            screenshot_dir.mkdir(exist_ok=True)
            
            filepath = screenshot_dir / f"{name}.png"
            self.driver.save_screenshot(str(filepath))
            self.logger.info(f"[Demo] Screenshot saved: {filepath}")
        except Exception as e:
            self.logger.error(f"[Demo] Failed to take screenshot: {e}")
    
    def scroll_to_element(self, locator: Tuple[str, str]) -> None:
        """Scroll to element."""
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        self.logger.debug(f"[Demo] Scrolled to element: {locator}")