# src/demo/pages/login_page.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time

from .base_page import BasePage
from ..config.config import Config

class LoginPage(BasePage):
    # ... other locators ...
    SIGN_IN_LINK = (By.XPATH, "/html/body/div/div/div/div[1]/div/div/div[2]/nav/span")
    USERNAME_DROPDOWN = (By.XPATH, "//div[contains(text(), 'Select Username')]")
    PASSWORD_DROPDOWN = (By.XPATH, "//div[contains(text(), 'Select Password')]")
    DEMOUSER_OPTION = (By.XPATH, "//div[text()='demouser']")
    PASSWORD_OPTION = (By.XPATH, "//div[text()='testingisfun99']")
    LOGIN_BUTTON = (By.XPATH, "//button[text()='Log In']")

    # Replace fragile Samsung filter with a reliable Favorites link locator
    FAVORITES_HEADER_LINK = (By.CSS_SELECTOR, "a[href='/favourites']")

    def verify_login_successful(self) -> bool:
        """Verify login success by checking for the Favorites header link."""
        self.logger.info("[Demo] Verifying login by checking for Favorites header link...")
        return self.is_element_visible(self.FAVORITES_HEADER_LINK, timeout=15)

    def login(self, username: str = "demouser", password: str = "testingisfun99") -> None:
        self.navigate_and_click_signin()
        self.select_username()
        self.select_password()
        self.click_login()
        time.sleep(2)
        assert self.verify_login_successful(), "[Demo] Login failed - Favorites header link not found"
        self.logger.info("[Demo] Login completed successfully")
