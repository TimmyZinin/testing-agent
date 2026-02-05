"""
Pytest fixtures for testing
"""

import pytest
import sys
from pathlib import Path

# Add tests directory to path so we can import from test files
sys.path.insert(0, str(Path(__file__).parent))

# Import Calculator from test file (it's defined there)
from test_calculator import Calculator


@pytest.fixture
def calculator():
    """Fixture that provides a fresh Calculator instance for each test."""
    return Calculator()
