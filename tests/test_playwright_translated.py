"""Test translated from Playwright to Selenium."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def test_playwright_flow_in_selenium(driver):
    """Exact translation of Playwright test to Selenium."""
    wait = WebDriverWait(driver, 10)
    
    # Navigate to the page
    driver.get("https://bstackdemo.com/")
    
    # Click "Sign In" link
    sign_in_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Sign In")))
    sign_in_link.click()
    
    # Click on username dropdown - finding div with text "Select Username"
    username_dropdown = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Select Username')]"))
    )
    username_dropdown.click()
    
    # Click "demouser" option
    demouser_option = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[text()='demouser']"))
    )
    demouser_option.click()
    
    # Click on password dropdown - finding div with text "Select Password"
    password_dropdown = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Select Password')]"))
    )
    password_dropdown.click()
    
    # Click "testingisfun99" option
    password_option = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[text()='testingisfun99']"))
    )
    password_option.click()
    
    # Click "Log In" button
    login_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Log In']"))
    )
    login_button.click()
    
    # Wait for page to load after login
    time.sleep(2)
    
    # Click "Samsung" filter
    samsung_filter = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='Samsung']"))
    )
    samsung_filter.click()
    
    # Wait for products to filter
    time.sleep(2)
    
    # Click favorite button for product with id="11" (Galaxy S20+)
    # In Playwright: [id="11"] .get_by_role("button", name="delete")
    favorite_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='11']//button"))
    )
    favorite_button.click()
    
    # Click "Favourites" link
    favourites_link = wait.until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Favourites"))
    )
    favourites_link.click()
    
    # Verify "Galaxy S20+" is in favorites
    galaxy_s20 = wait.until(
        EC.presence_of_element_located((By.XPATH, "//p[text()='Galaxy S20+']"))
    )
    assert galaxy_s20.is_displayed(), "Galaxy S20+ not found in favorites"
    
    print("[Demo] ✅ Test completed successfully!")