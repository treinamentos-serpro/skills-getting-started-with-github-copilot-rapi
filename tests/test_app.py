import pytest
from fastapi.testclient import TestClient

import src.app as app_module


ACTIVITY_NAME = "Chess Club"


@pytest.fixture
def activities(monkeypatch):
    sample_activities = {
        ACTIVITY_NAME: {
            "description": "Practice chess",
            "schedule": "Fridays at 3:30 PM",
            "max_participants": 2,
            "participants": ["current@school.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", sample_activities)
    return sample_activities


@pytest.fixture
def client(activities):
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client, activities):
    # Arrange
    expected_activities = activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_student_to_activity(client, activities):
    # Arrange
    email = "new@school.edu"

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {ACTIVITY_NAME}"}
    assert activities[ACTIVITY_NAME]["participants"] == [
        "current@school.edu",
        email,
    ]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "new@school.edu"

    # Act
    response = client.post(
        "/activities/Unknown Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_student(client):
    # Arrange
    email = "current@school.edu"

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_signup_rejects_full_activity(client, activities):
    # Arrange
    activities[ACTIVITY_NAME]["participants"] = [
        "first@school.edu",
        "second@school.edu",
    ]
    email = "new@school.edu"

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}


def test_unregister_removes_student_from_activity(client, activities):
    # Arrange
    email = "current@school.edu"

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {ACTIVITY_NAME}"
    }
    assert activities[ACTIVITY_NAME]["participants"] == []


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "current@school.edu"

    # Act
    response = client.delete(
        "/activities/Unknown Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_not_found_for_unregistered_student(client):
    # Arrange
    email = "missing@school.edu"

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }