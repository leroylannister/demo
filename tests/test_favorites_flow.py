"""Test suite for Demo favorites functionality using Playwright-style selectors."""

import pytest
import time

from tests.test_base import TestBase
from src.demo.pages.login_page import LoginPage
from src.demo.pages.products_page import ProductsPage
from src.demo.pages.favorites_page import FavoritesPage
from selenium.webdriver.common.by import By


class TestDemoFavoritesFlow(TestBase):
    """Test suite for Demo favorites functionality."""
    
    @pytest.mark.critical
    @pytest.mark.smoke
    def test_add_samsung_device_to_favorites(self):
        """Demo Test: Add Samsung Galaxy S20+ to favorites with proper BrowserStack integration"""
        try:
            # Initialize page objects
            login_page = LoginPage(self.driver)
            products_page = ProductsPage(self.driver)
            favorites_page = FavoritesPage(self.driver)
            
            # Step 1: Login
            self.logger.info("[Demo] Step 1: Logging into BStackDemo")
            login_page.login()
            
            # Step 2: Filter by Samsung
            self.logger.info("[Demo] Step 2: Filtering products by Samsung")
            products_page.filter_by_samsung()
            
            # Verify Galaxy S20+ is visible
            assert products_page.is_product_displayed("Galaxy S20+"), \
                "[Demo] Galaxy S20+ not found after Samsung filter"
            self.logger.info("[Demo] ✓ Samsung filter applied successfully")
            
            # Step 3: Add to favorites
            self.logger.info("[Demo] Step 3: Adding Galaxy S20+ to favorites")
            products_page.favorite_galaxy_s20_plus()
            self.logger.info("[Demo] ✓ Clicked favorite icon")
            
            # Step 4: Navigate to favorites and verify
            self.logger.info("[Demo] Step 4: Navigating to favorites page")
            products_page.navigate_to_favorites()
            
            # Verify Galaxy S20+ is in favorites
            assert favorites_page.is_product_in_favorites("Galaxy S20+"), \
                "[Demo] Galaxy S20+ not found in favorites"
            
            self.logger.info("[Demo] ✅ Successfully verified Galaxy S20+ in favorites")
            self.take_screenshot("demo_test_success_favorites_added")

            # Mark test as PASSED on BrowserStack
            self.driver.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status": "passed", "reason": "Samsung device successfully added to favorites"}}'
            )
            
        except Exception as e:
            # Mark test as FAILED on BrowserStack
            error_message = str(e).replace('"', '\\"')
            self.driver.execute_script(
                f'browserstack_executor: {{"action": "setSessionStatus", "arguments": {{"status": "failed", "reason": "{error_message}"}}}}'
            )
            raise

    @pytest.mark.debug
    @pytest.mark.skip(reason="Debug test - exclude from main runs")
    def test_debug_page(self):
        """Debug test to analyze page structure - excluded from main runs"""
        self.driver.get("https://www.bstackdemo.com")
        time.sleep(2)
        
        links = self.driver.find_elements(By.TAG_NAME, "a")
        print(f"\nFound {len(links)} links on page:")
        for link in links:
            print(f"  Text: '{link.text}' | Href: {link.get_attribute('href')}")
