import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data


def test_signup_for_activity_success():
    email = "newstudent@mergington.edu"
    activity = "Basketball Team"
    # Zorg dat de deelnemer nog niet is ingeschreven
    client.get("/activities")  # fetch to update state
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert f"Signed up {email}" in response.json()["message"]
    # Nogmaals inschrijven moet een fout geven
    response2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_activity_structure():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    # Verify that each activity has the expected structure
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)
        assert isinstance(activity_data["max_participants"], int)


def test_signup_for_different_activities():
    email = "multi@mergington.edu"
    # Sign up for Swimming Club
    response1 = client.post(f"/activities/Swimming Club/signup?email={email}")
    assert response1.status_code == 200
    # Sign up for Drama Club
    response2 = client.post(f"/activities/Drama Club/signup?email={email}")
    assert response2.status_code == 200
    # Verify both signups
    assert f"Signed up {email}" in response1.json()["message"]
    assert f"Signed up {email}" in response2.json()["message"]


def test_get_participants_list():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    # Verify Chess Club has the expected initial participants
    chess_participants = data["Chess Club"]["participants"]
    assert "michael@mergington.edu" in chess_participants
    assert "daniel@mergington.edu" in chess_participants


def test_signup_different_activity_types():
    # Test signup for various activity types
    activities_to_test = ["Math Olympiad", "Art Workshop", "Programming Class"]
    for i, activity in enumerate(activities_to_test):
        email = f"student{i}@mergington.edu"
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        assert f"Signed up {email} for {activity}" in response.json()["message"]
