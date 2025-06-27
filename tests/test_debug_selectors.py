"""Debug test to find the correct selectors."""

import pytest
from selenium.webdriver.common.by import By
import time


class TestDebugSelectors:
    """Debug the actual selectors on the page."""
    
    def test_find_dropdown_selectors(self, driver):
        """Find the correct dropdown selectors."""
        # Open the Bstack Demo website
        driver.get("https://bstackdemo.com/")
        time.sleep(2)
        
        # Find and click sign-in
        print("\n[DEBUG] Looking for sign-in button...")
        signin_buttons = driver.find_elements(By.CSS_SELECTOR, "#signin")
        print(f"[DEBUG] Found {len(signin_buttons)} sign-in buttons")
        
        if signin_buttons:
            signin_buttons[0].click()
            time.sleep(2)
        
        # Find username field
        print("\n[DEBUG] Looking for username field...")
        username_fields = driver.find_elements(By.ID, "username")
        print(f"[DEBUG] Found {len(username_fields)} username fields")
        
        if username_fields:
            print("[DEBUG] Clicking username field...")
            username_fields[0].click()
            time.sleep(2)
            
            # Find all options that appear
            print("\n[DEBUG] Looking for dropdown options...")
            
            # Try different selectors
            selectors = [
                ("CSS ID exact", "#react-select-2-option-0-0"),
                ("CSS ID starts with", "[id^='react-select-2-option']"),
                ("CSS class option", ".css-1n7v3ny-option"),
                ("XPath contains text", "//div[contains(text(), 'demouser')]"),
                ("CSS any ID with option", "[id*='option']"),
                ("XPath any div with ID", "//div[contains(@id, 'option')]")
            ]
            
            for name, selector in selectors:
                try:
                    if name.startswith("CSS"):
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    else:
                        elements = driver.find_elements(By.XPATH, selector)
                    
                    print(f"\n[DEBUG] {name}: Found {len(elements)} elements")
                    for i, elem in enumerate(elements[:3]):  # Show first 3
                        print(f"  Element {i}: text='{elem.text}', id='{elem.get_attribute('id')}'")
                except Exception as e:
                    print(f"[DEBUG] {name}: Error - {str(e)}")
            
            # Take screenshot
            driver.save_screenshot("screenshots/debug_dropdown_open.png")
            print("\n[DEBUG] Screenshot saved: screenshots/debug_dropdown_open.png")
