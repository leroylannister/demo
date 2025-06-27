# tests/test_fixture.py
def test_fixture_available(driver):
    """Simple test to check if driver fixture is available."""
    assert driver is not None
    print(f"Driver type: {type(driver)}")