
import pytest
import sys
from pathlib import Path

# Add parent directory to Python path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from fastapi.testclient import TestClient

from main import app
from bff.dependencies import ensure_data_seeded


@pytest.fixture
def client():
    """
    FastAPI test client for making requests to your endpoints.
    This is synchronous and perfect for simple API testing.
    """
    return TestClient(app)


@pytest.fixture
def mock_services():
    """Seed the in-memory repositories with test data."""
    ensure_data_seeded()
    yield
