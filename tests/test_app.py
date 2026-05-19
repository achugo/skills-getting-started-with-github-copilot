"""
Tests for the Mergington High School Activities API.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities data to a known state before each test."""
    original = {name: {**data, "participants": list(data["participants"])} for name, data in activities.items()}
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


# --- GET /activities ---

def test_get_activities_returns_200():
    response = client.get("/activities")
    assert response.status_code == 200


def test_get_activities_returns_dict():
    response = client.get("/activities")
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0


def test_get_activities_contains_expected_fields():
    response = client.get("/activities")
    data = response.json()
    for activity in data.values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# --- POST /activities/{activity_name}/signup ---

def test_signup_success():
    response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    assert "newstudent@mergington.edu" in response.json()["message"]


def test_signup_adds_participant():
    client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
    response = client.get("/activities")
    participants = response.json()["Chess Club"]["participants"]
    assert "newstudent@mergington.edu" in participants


def test_signup_duplicate_rejected():
    """A student already signed up should not be able to sign up again."""
    email = "michael@mergington.edu"  # Already in Chess Club
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_nonexistent_activity_returns_404():
    response = client.post("/activities/Nonexistent Activity/signup?email=student@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# --- GET / (redirect) ---

def test_root_redirects_to_index():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (301, 302, 307, 308)
    assert "/static/index.html" in response.headers["location"]
