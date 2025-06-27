import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.smoke
class TestSimpleDemo:
    def test_page_loads(self, driver):
        """Simple test to verify BrowserStack connection works"""
        # Navigate to the demo site
        driver.get("https://www.bstackdemo.com")
        
        # Wait for page to load and check title
        wait = WebDriverWait(driver, 10)
        
        # Just verify we can interact with the page
        assert "StackDemo" in driver.title
        
        # Try to find any element to verify page loaded
        body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        assert body is not None
        
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")