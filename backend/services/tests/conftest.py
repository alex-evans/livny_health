
import pytest
import sys
from pathlib import Path

# Add parent directory to Python path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """
    FastAPI test client for making requests to your endpoints.
    This is synchronous and perfect for simple API testing.
    """
    return TestClient(app)


@pytest.fixture
def sample_patient():
    """Reusable sample patient data for tests"""
    return {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1980-05-15",
        "mrn": "MRN-001234"
    }


@pytest.fixture
def sample_medication():
    """Reusable sample medication data for tests"""
    return {
        "rxcui": "197361",
        "name": "Simvastatin 20 MG Oral Tablet",
        "generic_name": "simvastatin"
    }


@pytest.fixture
def sample_search_term():
    """Common medication search term"""
    return "simvastatin"
