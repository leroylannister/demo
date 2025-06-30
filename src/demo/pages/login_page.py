"""Products page object for BStackDemo."""

from selenium.webdriver.common.by import By
import logging
import time

from .base_page import BasePage

logger = logging.getLogger(__name__)


class ProductsPage(BasePage):
    """Page object for products listing and filtering."""
    
    # Locators
    SAMSUNG_FILTER = (By.XPATH, "//span[text()='Samsung']")
    APPLE_FILTER = (By.XPATH, "//span[text()='Apple']")
    GOOGLE_FILTER = (By.XPATH, "//span[text()='Google']")
    ONEPLUS_FILTER = (By.XPATH, "//span[text()='OnePlus']")
    
    PRODUCT_TITLE = (By.CLASS_NAME, "shelf-item__title")
    PRODUCT_CONTAINER = (By.CLASS_NAME, "shelf-item")
    
    # Galaxy S20+ specific locators
    GALAXY_S20_CONTAINER = (By.CSS_SELECTOR, "[id='11']")
    GALAXY_S20_FAVORITE_BTN = (By.CSS_SELECTOR, "[id='11'] button")
    
    FAVORITES_LINK = (By.LINK_TEXT, "Favourites")
    
    def filter_by_brand(self, brand: str):
        """Apply brand filter."""
        logger.info(f"Filtering by brand: {brand}")
        
        brand_lower = brand.lower()
        if brand_lower == "samsung":
            self.click_element(*self.SAMSUNG_FILTER)
        elif brand_lower == "apple":
            self.click_element(*self.APPLE_FILTER)
        elif brand_lower == "google":
            self.click_element(*self.GOOGLE_FILTER)
        elif brand_lower == "oneplus":
            self.click_element(*self.ONEPLUS_FILTER)
        else:
            raise ValueError(f"Unknown brand: {brand}")
        
        # Wait for products to filter
        time.sleep(2)
    
    def filter_by_samsung(self):
        """Apply Samsung filter."""
        self.filter_by_brand("Samsung")
    
    def get_all_product_names(self):
        """Get names of all visible products."""
        products = self.find_elements(*self.PRODUCT_TITLE)
        return [p.text for p in products]
    
    def is_product_displayed(self, product_name: str):
        """Check if a specific product is displayed."""
        product_names = self.get_all_product_names()
        return product_name in product_names
    
    def favorite_product_by_name(self, product_name: str):
        """Add a product to favorites by its name."""
        logger.info(f"Adding {product_name} to favorites")
        
        # Find all product containers
        products = self.find_elements(*self.PRODUCT_CONTAINER)
        
        for product in products:
            title_element = product.find_element(By.CLASS_NAME, "shelf-item__title")
            if title_element.text == product_name:
                # Find and click the favorite button within this product
                favorite_btn = product.find_element(By.TAG_NAME, "button")
                self.scroll_to_element(favorite_btn)
                favorite_btn.click()
                logger.info(f"Clicked favorite for {product_name}")
                return
        
        raise Exception(f"Product not found: {product_name}")
    
    def favorite_galaxy_s20_plus(self):
        """Add Galaxy S20+ to favorites using specific selector."""
        logger.info("Adding Galaxy S20+ to favorites")
        
        # Method 1: Try specific ID selector
        try:
            self.click_element(*self.GALAXY_S20_FAVORITE_BTN)
            return
        except:
            logger.warning("Failed with ID selector, trying by name")
        
        # Method 2: Fallback to name-based selection
        self.favorite_product_by_name("Galaxy S20+")
    
    def navigate_to_favorites(self):
        """Navigate to favorites page."""
        logger.info("Navigating to favorites")
        self.click_element(*self.FAVORITES_LINK)
        
        # Wait for navigation
        time.sleep(1)