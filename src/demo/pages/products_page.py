"""Products page object model for Demo test suite - using Playwright-style selectors."""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class ProductsPage(BasePage):
    """Products page object model for Demo."""
    
    # Locators - Playwright style
    SAMSUNG_FILTER = (By.XPATH, "//span[text()='Samsung']")
    GALAXY_S20_FAVORITE_BUTTON = (By.XPATH, "//*[@id='11']//button")
    FAVORITES_LINK = (By.LINK_TEXT, "Favourites")
    GALAXY_S20_TEXT = (By.XPATH, "//p[text()='Galaxy S20+']")
    
    def filter_by_samsung(self) -> None:
        """Click Samsung filter."""
        self.logger.info("[Demo] Filtering products by Samsung")
        
        # Click Samsung text to filter
        samsung_element = self.wait.until(EC.element_to_be_clickable(self.SAMSUNG_FILTER))
        samsung_element.click()
        
        time.sleep(2)  # Wait for filter to apply
        self.logger.info("[Demo] Samsung filter applied")
    
    def favorite_galaxy_s20_plus(self) -> None:
        """Click favorite button for Galaxy S20+ (id=11)."""
        self.logger.info("[Demo] Adding Galaxy S20+ to favorites")
        
        # Find and click the favorite button for product id="11"
        favorite_btn = self.wait.until(EC.element_to_be_clickable(self.GALAXY_S20_FAVORITE_BUTTON))
        
        # Scroll to element if needed
        self.driver.execute_script("arguments[0].scrollIntoView(true);", favorite_btn)
        time.sleep(1)
        
        favorite_btn.click()
        time.sleep(1)  # Wait for favorite action
        self.logger.info("[Demo] Galaxy S20+ added to favorites")
    
    def navigate_to_favorites(self) -> None:
        """Click Favourites link."""
        self.logger.info("[Demo] Navigating to favorites page")
        
        favorites_link = self.wait.until(EC.element_to_be_clickable(self.FAVORITES_LINK))
        favorites_link.click()
        
        time.sleep(2)  # Wait for page load
        self.logger.info("[Demo] Navigated to favorites page")
    
    def is_product_displayed(self, product_name: str) -> bool:
        """Check if product is displayed on page."""
        try:
            product_element = self.driver.find_element(By.XPATH, f"//p[text()='{product_name}']")
            return product_element.is_displayed()
        except:
            return False