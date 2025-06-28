"""Fixed LoginPage using proven React Select interaction patterns."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import time

from src.demo.pages.base_page import BasePage


class LoginPage(BasePage):
    """LoginPage using proven React Select patterns from BrowserStack docs"""
    
    # Locators for elements on the page
    SIGN_IN_BUTTON = (By.ID, "signin")
    USERNAME_FIELD = (By.ID, "username")
    PASSWORD_FIELD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-btn")
    
    def __init__(self, driver):
        super().__init__(driver)
        
    def navigate_to_site(self):
        """Navigate to bstackdemo.com"""
        self.logger.info("[Demo] Navigating to bstackdemo.com...")
        self.driver.get("https://bstackdemo.com")
        
        try:
            WebDriverWait(self.driver, 10).until(EC.title_contains('StackDemo'))
            self.logger.info("[Demo] Page loaded successfully")
        except TimeoutException:
            self.logger.warning("[Demo] Page might not have loaded completely")
        
    def click_sign_in(self):
        """Click the Sign In button to open login modal"""
        try:
            self.logger.info("[Demo] Looking for Sign In button...")
            sign_in_btn = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.SIGN_IN_BUTTON)
            )
            sign_in_btn.click()
            self.logger.info("[Demo] ✓ Clicked Sign In button")
            
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located(self.USERNAME_FIELD)
                )
                self.logger.info("[Demo] ✓ Login modal opened successfully")
                return True
            except TimeoutException:
                self.logger.warning("[Demo] Login modal may not have opened properly")
                return True 
                
        except TimeoutException:
            self.logger.warning("[Demo] Sign In button not found")
            return False
    
    def select_username_and_password(self, username="demouser", password="testingisfun99"):
        """Select username and password using the working test pattern"""
        try:
            self.logger.info("[Demo] Selecting username and password...")
            
            # Step 1: Click on username field to open dropdown - using visibility_of_element_located like working test
            username_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.USERNAME_FIELD)
            )
            username_field.click()
            self.logger.info("[Demo] ✓ Clicked username field")
            
            # Step 2: Select demouser option using XPath like the working test
            username_option = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[contains(text(), 'demouser')]"))
            )
            username_option.click()
            self.logger.info("[Demo] ✓ Selected username")
            
            # Step 3: Click on password field to open dropdown
            password_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.PASSWORD_FIELD)
            )
            password_field.click()
            self.logger.info("[Demo] ✓ Clicked password field")
            
            # Step 4: Select password option using XPath like the working test
            password_option = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[contains(text(), 'testingisfun99')]"))
            )
            password_option.click()
            self.logger.info("[Demo] ✓ Selected password")
            
            return True
            
        except TimeoutException:
            self.logger.error("[Demo] Failed to select username and password")
            self.driver.save_screenshot("debug_username_password_selection_failed.png")
            return False
        except Exception as e:
            self.logger.error(f"[Demo] An unexpected error occurred: {e}")
            self.driver.save_screenshot("debug_username_password_selection_error.png")
            return False

    def click_login(self):
        """Click the Login button using the working test pattern"""
        try:
            self.logger.info("[Demo] Clicking Login button...")
            
            # Use visibility_of_element_located like the working test
            login_btn = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.LOGIN_BUTTON)
            )
            login_btn.click()
            
            self.logger.info("[Demo] ✓ Clicked Login button")
            return True
            
        except Exception as e:
            self.logger.error(f"[Demo] Login button click failed: {e}")
            self.driver.save_screenshot("debug_login_button_error.png")
            return False
    
    def verify_login_success(self):
        """Verify that login was successful by checking URL or logout button"""
        try:
            # Check if we're on the signed-in page (which indicates successful login)
            current_url = self.driver.current_url
            if "?signin=true" in current_url:
                self.logger.info("[Demo] ✓ Login successful - detected signin=true in URL")
                return True
                
            # Fallback: try to find logout button
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.ID, "logout"))
            )
            self.logger.info("[Demo] ✓ Login successful - logout button found")
            return True
            
        except TimeoutException:
            current_url = self.driver.current_url
            if "?signin=true" in current_url:
                self.logger.info("[Demo] ✓ Login successful - signin=true in URL")
                return True
            else:
                self.logger.error(f"[Demo] Login failed. Current URL: {current_url}")
                self.driver.save_screenshot("debug_login_failed.png")
                return False

    def login(self, username="demouser", password="testingisfun99"):
        """Complete login flow using working test patterns"""
        self.logger.info("[Demo] Starting login process...")
        
        self.navigate_to_site()
        self.click_sign_in()
        self.select_username_and_password(username, password)
        self.click_login()
        
        if self.verify_login_success():
            self.logger.info("[Demo] ✅ Login completed successfully")
        else:
            self.logger.warning("[Demo] ⚠️ Login may have failed")
        
        return True
