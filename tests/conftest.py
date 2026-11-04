import os
import time

import pytest
import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5001")


@pytest.fixture
def auth_token():
    username = f"user_{time.time_ns()}"
    password = "geheim123"
    requests.post(f"{BASE_URL}/api/auth/register", json={"username": username, "password": password})
    response = requests.post(f"{BASE_URL}/api/auth/login", json={"username": username, "password": password})
    return response.json()["access_token"]