"""Test following exact BrowserStack tutorial pattern."""

from selenium.webdriver.common.by import By


def test_exact_browserstack_login(driver):
    """Exact copy of BrowserStack tutorial code."""
    # Open the Bstack Demo website
    driver.get("https://bstackdemo.com/")
    
    # Find the sign-in button and click on it
    signin_btn = driver.find_element(by=By.CSS_SELECTOR, value="#signin")
    signin_btn.click()
    
    # Add implicit wait for element to be found
    driver.implicitly_wait(10)
    
    # Find the Username, Password and Login Button
    username = driver.find_element(by=By.ID, value="username")
    password = driver.find_element(by=By.ID, value="password")
    login_btn = driver.find_element(by=By.ID, value="login-btn")
    
    # Select demouser as Username
    username.click()
    username_input = driver.find_element(by=By.CSS_SELECTOR, value="#react-select-2-option-0-0")
    username_input.click()
    
    # Select testingisfun99 as Password
    password.click()
    password_input = driver.find_element(by=By.CSS_SELECTOR, value="#react-select-3-option-0-0")
    password_input.click()
    
    # Submit the form
    login_btn.click()
    driver.implicitly_wait(10)
    
    # Assert User is successfully Logged In
    logout_btn = driver.find_element(by=By.CSS_SELECTOR, value="#logout")
    assert logout_btn.is_displayed()
    
    print("[Demo] ✅ Login successful using exact BrowserStack pattern!")