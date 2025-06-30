"""Favorites page object for BStackDemo."""

from selenium.webdriver.common.by import By
import logging

from .base_page import BasePage

logger = logging.getLogger(__name__)


class FavoritesPage(BasePage):
    """Page object for favorites page."""
    
    # Locators
    FAVORITE_PRODUCTS = (By.CLASS_NAME, "shelf-item")
    PRODUCT_TITLE = (By.CLASS_NAME, "shelf-item__title")
    EMPTY_FAVORITES_MSG = (By.XPATH, "//p[contains(text(),