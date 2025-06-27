"""Login page object model for Demo test suite - using Playwright-style selectors."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

from .base_page import BasePage
from ..config.config import Config


class LoginPage(BasePage):
    """Login page object model for Demo."""
    
    # Locators - using Playwright-style approach
    SIGN_IN_LINK = (By.LINK_TEXT, "Sign In")
    USERNAME_DROPDOWN = (By.XPATH, "//div[contains(text(), 'Select Username')]")
    PASSWORD_DROPDOWN = (By.XPATH, "//div[contains(text(), 'Select Password')]")
    DEMOUSER_OPTION = (By.XPATH, "//div[text()='demouser']")
    PASSWORD_OPTION = (By.XPATH, "//div[text()='testingisfun99']")
    LOGIN_BUTTON = (By.XPATH, "//button[text()='Log In']")
    LOGOUT_BUTTON = (By.CSS_SELECTOR, "#logout")
    
    def __init__(self, driver):
        """Initialize Demo login page."""
        super().__init__(driver)
        self.url = Config.BASE_URL
    
    def navigate_and_click_signin(self) -> None:
        """Navigate to Demo site and click sign in."""
        self.navigate_to(self.url)
        self.wait_for_page_load()
        
        # Click "Sign In" link
        self.wait.until(EC.element_to_be_clickable(self.SIGN_IN_LINK)).click()
        self.logger.info("[Demo] Clicked Sign In link")
    
    def select_username(self) -> None:
        """Select demouser from username dropdown."""
        self.logger.info("[Demo] Selecting username: demouser")
        
        # Click on the dropdown with "Select Username" text
        self.wait.until(EC.element_to_be_clickable(self.USERNAME_DROPDOWN)).click()
        time.sleep(0.5)  # Small delay for dropdown animation
        
        # Click the demouser option
        self.wait.until(EC.element_to_be_clickable(self.DEMOUSER_OPTION)).click()
        self.logger.info("[Demo] Selected demouser")
    
    def select_password(self) -> None:
        """Select testingisfun99 from password dropdown."""
        self.logger.info("[Demo] Selecting password")
        
        # Click on the dropdown with "Select Password" text
        self.wait.until(EC.element_to_be_clickable(self.PASSWORD_DROPDOWN)).click()
        time.sleep(0.5)  # Small delay for dropdown animation
        
        # Click the password option
        self.wait.until(EC.element_to_be_clickable(self.PASSWORD_OPTION)).click()
        self.logger.info("[Demo] Selected password")
    
    def click_login(self) -> None:
        """Click Log In button."""
        self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON)).click()
        self.logger.info("[Demo] Clicked Log In button")
    
    def verify_login_successful(self) -> bool:
        """Verify login was successful by checking for logout button."""
        return self.is_element_visible(self.LOGOUT_BUTTON, timeout=10)
    
    def login(self, username: str = "demouser", password: str = "testingisfun99") -> None:
        """Complete Demo login flow using Playwright-style approach."""
        # Navigate and click sign in
        self.navigate_and_click_signin()
        
        # Select username and password
        self.select_username()
        self.select_password()
        
        # Click Log In
        self.click_login()
        
        # Wait for login to complete
        time.sleep(2)
        
        # Verify login successful
        assert self.verify_login_successful(), "[Demo] Login failed - logout button not found"
        self.logger.info("[Demo] Login completed successfully")