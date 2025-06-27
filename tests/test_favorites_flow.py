"""Test suite for Demo favorites functionality using Playwright-style selectors."""

import pytest
import time

from tests.test_base import TestBase
from src.demo.pages.login_page import LoginPage
from src.demo.pages.products_page import ProductsPage
from src.demo.pages.favorites_page import FavoritesPage


class TestDemoFavoritesFlow(TestBase):
    """Test suite for Demo favorites functionality."""
    
    @pytest.mark.critical
    @pytest.mark.smoke
    def test_add_samsung_device_to_favorites(self):
        """
        Demo Test: Add Samsung Galaxy S20+ to favorites.
        Translated from Playwright to Selenium.
        
        Steps:
        1. Open BStackDemo and sign in
        2. Filter products by clicking Samsung
        3. Favorite the Galaxy S20+ device (id=11)
        4. Navigate to Favourites and verify Galaxy S20+ is there
        """
        # Initialize page objects
        login_page = LoginPage(self.driver)
        products_page = ProductsPage(self.driver)
        favorites_page = FavoritesPage(self.driver)
        
        # Step 1: Login using Playwright-style approach
        self.logger.info("[Demo] Step 1: Logging into BStackDemo")
        login_page.login()
        
        # Step 2: Click Samsung filter
        self.logger.info("[Demo] Step 2: Filtering products by Samsung")
        products_page.filter_by_samsung()
        
        # Verify Galaxy S20+ is visible
        assert products_page.is_product_displayed("Galaxy S20+"), \
            "[Demo] Galaxy S20+ not found after Samsung filter"
        self.logger.info("[Demo] ✓ Samsung filter applied successfully")
        
        # Step 3: Favorite Galaxy S20+ (id=11)
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