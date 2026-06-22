import copy
import urllib.parse

import pytest
from fastapi.testclient import TestClient

from app import app, activities


@pytest.fixture(autouse=True)
def client_and_restore():
    # Arrange: snapshot activities
    snapshot = copy.deepcopy(activities)
    client = TestClient(app)
    try:
        yield client
    finally:
        # Restore activities to original state after each test
        activities.clear()
        activities.update(snapshot)


def test_get_activities_returns_200_and_structure(client_and_restore):
    # Act
    client = client_and_restore
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect at least one known activity
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_success(client_and_restore):
    client = client_and_restore
    activity = "Chess Club"
    email = "testuser@example.com"

    # Act
    resp = client.post(f"/activities/{urllib.parse.quote(activity)}/signup?email={email}")

    # Assert
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]
    assert "Signed up" in resp.json()["message"]


def test_signup_duplicate(client_and_restore):
    client = client_and_restore
    activity = "Chess Club"
    email = "michael@mergington.edu"  # already a participant in initial data

    # Act
    resp = client.post(f"/activities/{urllib.parse.quote(activity)}/signup?email={email}")

    # Assert
    assert resp.status_code == 400


def test_signup_unknown_activity(client_and_restore):
    client = client_and_restore
    activity = "Nonexistent Club"
    email = "someone@example.com"

    # Act
    resp = client.post(f"/activities/{urllib.parse.quote(activity)}/signup?email={email}")

    # Assert
    assert resp.status_code == 404


def test_unregister_success(client_and_restore):
    client = client_and_restore
    activity = "Chess Club"
    email = "daniel@mergington.edu"  # existing participant

    # Act
    resp = client.post(f"/activities/{urllib.parse.quote(activity)}/unregister?email={email}")

    # Assert
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_not_found(client_and_restore):
    client = client_and_restore
    activity = "Chess Club"
    email = "notregistered@example.com"

    # Act
    resp = client.post(f"/activities/{urllib.parse.quote(activity)}/unregister?email={email}")

    # Assert
    assert resp.status_code == 404
