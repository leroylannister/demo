"""Configuration module for Demo test suite following 12-factor app principles."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)


class Config:
    """Configuration class for Demo test suite."""
    
    # Project Info
    PROJECT_NAME = "Demo"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    
    # URLs
    BASE_URL: str = os.getenv("BASE_URL", "https://www.bstackdemo.com")
    
    # Credentials (from environment variables)
    TEST_USERNAME: Optional[str] = os.getenv("TEST_USERNAME")
    TEST_PASSWORD: Optional[str] = os.getenv("TEST_PASSWORD")
    
    # BrowserStack
    BROWSERSTACK_USERNAME: Optional[str] = os.getenv("BROWSERSTACK_USERNAME")
    BROWSERSTACK_ACCESS_KEY: Optional[str] = os.getenv("BROWSERSTACK_ACCESS_KEY")
    
    # Timeouts
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "30"))
    IMPLICIT_WAIT: int = int(os.getenv("IMPLICIT_WAIT", "10"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate_config(cls) -> None:
        """Validate required configuration for Demo tests."""
        required_vars = [
            "TEST_USERNAME", 
            "TEST_PASSWORD",
            "BROWSERSTACK_USERNAME",
            "BROWSERSTACK_ACCESS_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(
                f"Demo Configuration Error - Missing required environment variables: {', '.join(missing_vars)}\n"
                f"Please check your .env file or environment variables."
            )