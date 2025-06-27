"""Products page object model for Demo test suite."""

import time
from selenium.webdriver.common.by import By

from .base_page import BasePage


class FavoritesPage(BasePage):
    """Products page object model for Demo."""
    
    # Locators - using CSS selectors where possible
    VENDOR_FILTER = (By.CSS_SELECTOR, "span.sort span.select-wrap")
    SAMSUNG_OPTION = (By.CSS_SELECTOR, "option[value='Samsung']")
    
    # Alternative XPath locators if CSS doesn't work
    VENDOR_FILTER_ALT = (By.XPATH, "//span[text()='Select a vendor']")
    SAMSUNG_OPTION_ALT = (By.XPATH, "//span[text()='Samsung']")
    
    # Product locators
    PRODUCT_CARDS = (By.CSS_SELECTOR, ".shelf-item")
    GALAXY_S20_PLUS = (By.XPATH, "//p[text()='Galaxy S20+']")
    
    # Favorite icon - need to find the heart icon for Galaxy S20+
    FAVORITE_ICON = (By.XPATH, "//p[text()='Galaxy S20+']/ancestor::div[@class='shelf-item']//button[contains(@class, 'MuiButtonBase-root')]")
    
    # Navigation
    FAVORITES_LINK = (By.CSS_SELECTOR, "a[href='/favourites']")
    
    def filter_by_samsung(self) -> None:
        """Filter products to show Samsung devices only."""
        self.logger.info("[Demo] Filtering products by Samsung")
        
        # Add implicit wait
        self.driver.implicitly_wait(10)
        
        try:
            # Try CSS selector first
            self.click(self.VENDOR_FILTER)
            time.sleep(1)
            self.click(self.SAMSUNG_OPTION)
        except:
            # Fall back to XPath if CSS doesn't work
            self.logger.info("[Demo] Using alternative selectors for filter")
            self.click(self.VENDOR_FILTER_ALT)
            time.sleep(1)
            self.click(self.SAMSUNG_OPTION_ALT)
        
        time.sleep(2)  # Wait for filter to apply
        self.logger.info("[Demo] Samsung filter applied")
    
    def favorite_galaxy_s20_plus(self) -> None:
        """Click favorite icon on Galaxy S20+."""
        self.logger.info("[Demo] Adding Galaxy S20+ to favorites")
        
        # Scroll to element if needed
        self.scroll_to_element(self.GALAXY_S20_PLUS)
        time.sleep(1)
        
        # Click the favorite icon
        self.click(self.FAVORITE_ICON)
        time.sleep(1)  # Wait for favorite action
        self.logger.info("[Demo] Galaxy S20+ added to favorites")
    
    def navigate_to_favorites(self) -> None:
        """Navigate to favorites page."""
        self.logger.info("[Demo] Navigating to favorites page")
        self.click(self.FAVORITES_LINK)
        self.driver.implicitly_wait(10)
        self.logger.info("[Demo] Navigated to favorites page")
    
    def is_product_displayed(self, product_name: str) -> bool:
        """Check if product is displayed on page."""
        product_locator = (By.XPATH, f"//p[text()='{product_name}']")
        return self.is_element_displayed(product_locator)
    
    def is_product_in_favorites(self, product_name: str) -> bool:
        """Check if product is in favorites."""
        product_locator = (By.XPATH, f"//p[text()='{product_name}']")
        return self.is_element_displayed(product_locator)