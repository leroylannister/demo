# tests/test_minimal.py
import pytest

@pytest.fixture
def my_fixture():
    return "Hello from fixture"

def test_with_fixture(my_fixture):
    assert my_fixture == "Hello from fixture"
    print(f"Fixture value: {my_fixture}")