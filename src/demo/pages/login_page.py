# src/demo/pages/login_page.py

"""Login page object model for Demo test suite - using Playwright-style selectors."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time

from .base_page import BasePage
from ..config.config import Config


class LoginPage(BasePage):
    """Login page object model for Demo."""

    # Locators are proven to work locally, DO NOT CHANGE THEM.
    SIGN_IN_LINK = (
        By.XPATH, "/html/body/div/div/div/div[1]/div/div/div[2]/nav/span")
    USERNAME_DROPDOWN = (
        By.XPATH, "//div[contains(text(), 'Select Username')]")
    PASSWORD_DROPDOWN = (
        By.XPATH, "//div[contains(text(), 'Select Password')]")
    DEMOUSER_OPTION = (By.XPATH, "//div[text()='demouser']")
    PASSWORD_OPTION = (By.XPATH, "//div[text()='testingisfun99']")
    LOGIN_BUTTON = (By.XPATH, "//button[text()='Log In']")
    LOGOUT_BUTTON = (
        By.XPATH, "/html/body/div/div/div/div[1]/div/div/div[2]/nav/span")

    def __init__(self, driver):
        """Initialize Demo login page."""
        super().__init__(driver)
        self.url = Config.BASE_URL

    def navigate_and_click_signin(self) -> None:
        """Navigate to Demo site and click sign in."""
        self.navigate_to(self.url)
        self.wait_for_page_load()

        # === THE FIX IS HERE ===
        # The default wait is too short for BrowserStack's latency.
        # We will use a longer, explicit 20-second wait ONLY for this one step.
        try:
            self.logger.info(
                "[Demo] Waiting up to 20s for Sign In link on remote environment...")
            long_wait = WebDriverWait(self.driver, 20)
            sign_in_element = long_wait.until(
                EC.element_to_be_clickable(self.SIGN_IN_LINK))
            sign_in_element.click()
            self.logger.info("[Demo] Clicked Sign In link")
        except TimeoutException:
            self.logger.error(
                "[Demo] FATAL: Sign In link was not clickable even after 20 seconds.")
            # This will help you debug by showing what BrowserStack sees if it fails again
            self.driver.save_screenshot("screenshots/fatal_signin_timeout.png")
            raise

    # NO OTHER CHANGES ARE NEEDED IN THE REST OF THE FILE.
    # The functions below this are all fine.

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
        # Using the updated LOGOUT_BUTTON locator
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

