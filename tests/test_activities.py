"""Tests for activity management endpoints"""
import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all available activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        assert "Art Club" in activities
        assert "Music Club" in activities
        assert "Drama Club" in activities
        assert "Science Club" in activities

    def test_get_activities_returns_correct_structure(self, client, reset_activities):
        """Test that each activity has the correct structure"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_shows_correct_participants(self, client, reset_activities):
        """Test that activities show the correct participants list"""
        response = client.get("/activities")
        activities = response.json()
        
        # Chess Club should have 2 participants initially
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_signup_adds_participant_to_list(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Verify the participant was added
        response = client.get("/activities")
        activities = response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup fails when activity doesn't exist"""
        response = client.post(
            "/activities/NonexistentActivity/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_signup(self, client, reset_activities):
        """Test signup fails when student is already signed up"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_with_url_encoded_email(self, client, reset_activities):
        """Test signup works with special characters in email"""
        activity_name = "Chess Club"
        email = "student+test@mergington.edu"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert email in client.get("/activities").json()["Chess Club"]["participants"]

    def test_signup_with_url_encoded_activity_name(self, client, reset_activities):
        """Test signup works with activity names that need URL encoding"""
        # All default activities don't have special chars, but test the logic
        activity_name = "Programming Class"  # Has space
        email = "newstudent@mergington.edu"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Verify participant is there initially
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]
        
        # Unregister
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Verify participant was removed
        response = client.get("/activities")
        assert email not in response.json()[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client, reset_activities):
        """Test unregister fails when activity doesn't exist"""
        response = client.delete(
            "/activities/NonexistentActivity/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_student_not_signed_up(self, client, reset_activities):
        """Test unregister fails when student is not signed up"""
        activity_name = "Chess Club"
        email = "nostudent@mergington.edu"
        
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_with_url_encoded_email(self, client, reset_activities):
        """Test unregister works with special characters in email"""
        activity_name = "Chess Club"
        email = "newstudent+test@mergington.edu"
        
        # First signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Then unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert email not in client.get("/activities").json()[activity_name]["participants"]


class TestRoot:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_index(self, client):
        """Test that root path redirects to static index page"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]

    def test_root_redirect_with_follow(self, client):
        """Test that following the redirect works"""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200
