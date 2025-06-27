# tests/test_demo_basic.py
import pytest
from src.demo.config.config import Config

class TestDemoBasic:
    """Basic tests for Demo project setup."""
    
    def test_demo_config_loads(self):
        """Test that Demo configuration loads correctly."""
        assert Config.BASE_URL == "https://www.bstackdemo.com"
        assert Config.PROJECT_NAME == "Demo"
        print("✅ Demo configuration loaded successfully!")
    
    def test_demo_can_open_site(self, driver):
        """Test that Demo can open the test site."""
        driver.get(Config.BASE_URL)
        assert "StackDemo" in driver.title
        print("✅ Demo successfully opened BStackDemo!")