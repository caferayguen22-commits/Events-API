import time

import requests

from tests.conftest import BASE_URL


def test_health_endpoint_returns_healthy():
    response = requests.get(f"{BASE_URL}/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_register_creates_new_user():
    username = f"user_{time.time_ns()}"

    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"username": username, "password": "geheim123"},
    )

    assert response.status_code == 201
    assert response.json()["user"]["username"] == username

def test_login_returns_access_token():
    username = f"user_{time.time_ns()}"
    password = "geheim123"
    requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"username": username, "password": password},
    )

    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": username, "password": password},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_event_with_token_returns_event(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    event_data = {
        "title": "Python Meetup",
        "date": "2027-01-15T18:00:00",
        "location": "Berlin",
        "capacity": 50,
    }

    response = requests.post(f"{BASE_URL}/api/events", json=event_data, headers=headers)

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Python Meetup"
    assert body["location"] == "Berlin"
    assert body["capacity"] == 50


def test_rsvp_to_public_event_creates_rsvp(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    event_response = requests.post(
        f"{BASE_URL}/api/events",
        json={"title": "Public Event", "date": "2027-02-01T18:00:00"},
        headers=headers,
    )
    event_id = event_response.json()["id"]

    response = requests.post(f"{BASE_URL}/api/rsvps/event/{event_id}", json={}, headers=headers)

    assert response.status_code == 201
    body = response.json()
    assert body["event_id"] == event_id
    assert body["attending"] is True


def test_register_duplicate_username_returns_400():
    username = f"user_{time.time_ns()}"
    credentials = {"username": username, "password": "geheim123"}
    requests.post(f"{BASE_URL}/api/auth/register", json=credentials)

    response = requests.post(f"{BASE_URL}/api/auth/register", json=credentials)

    assert response.status_code == 400
    assert response.json()["error"] == "Username already exists"


def test_create_event_without_token_returns_401():
    response = requests.post(
        f"{BASE_URL}/api/events",
        json={"title": "Ohne Token", "date": "2027-03-01T18:00:00"},
    )

    assert response.status_code == 401


def test_rsvp_to_private_event_without_token_returns_401(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    event_response = requests.post(
        f"{BASE_URL}/api/events",
        json={"title": "Privat", "date": "2027-04-01T18:00:00", "is_public": False},
        headers=headers,
    )
    event_id = event_response.json()["id"]

    response = requests.post(f"{BASE_URL}/api/rsvps/event/{event_id}", json={})

    assert response.status_code == 401