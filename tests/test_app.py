from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_expected_structure():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    encoded_activity = quote(activity_name, safe="")

    # Act
    response = client.post(
        f"/activities/{encoded_activity}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    activity_response = client.get("/activities")
    assert email in activity_response.json()[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = "michael@mergington.edu"
    encoded_activity = quote(activity_name, safe="")

    # Act
    response = client.post(
        f"/activities/{encoded_activity}/signup",
        params={"email": duplicate_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_delete_participant_removes_student():
    # Arrange
    activity_name = "Chess Club"
    email = "daniel@mergington.edu"
    encoded_activity = quote(activity_name, safe="")
    encoded_email = quote(email, safe="")

    # Act
    response = client.delete(
        f"/activities/{encoded_activity}/participants/{encoded_email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}

    activity_response = client.get("/activities")
    assert email not in activity_response.json()[activity_name]["participants"]


def test_delete_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "missing@mergington.edu"
    encoded_activity = quote(activity_name, safe="")
    encoded_email = quote(email, safe="")

    # Act
    response = client.delete(
        f"/activities/{encoded_activity}/participants/{encoded_email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
