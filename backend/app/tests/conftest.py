import pytest
import os
import mongomock_motor
from fastapi.testclient import TestClient

os.environ["USE_MOCK_DB"] = "true"
os.environ["DATABASE_NAME"] = "test_expense_tracker"

from app.main import app
from app.core.database import db_instance, setup_database_indexes, seed_system_categories


@pytest.fixture(autouse=True)
def init_db():
    client = mongomock_motor.AsyncMongoMockClient()
    db_instance.client = client
    db_instance.db = client["test_expense_tracker"]
    db_instance.is_mock = True
    yield
    client.close()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    reg_payload = {
        "email": "testuser@example.com",
        "password": "Password123!",
        "full_name": "Test User",
        "monthly_income": 50000.0,
        "occupation": "Working Professional"
    }
    resp = client.post("/api/v1/auth/register", json=reg_payload)
    data = resp.json()
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}
