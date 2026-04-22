"""
Comprehensive test suite for Mergington High School Activities API

Tests organized by endpoint using the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the action being tested
- Assert: Verify the outcome
"""

import pytest
from src.app import activities


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_dict(self, client):
        """Test that /activities returns a dictionary"""
        # Arrange: (No setup needed)
        
        # Act: Make request to get activities
        response = client.get("/activities")
        
        # Assert: Verify response is successful and returns dict
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_activities_includes_all_activities(self, client):
        """Test that all 9 activities are returned"""
        # Arrange: Expected activity names
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Art Club",
            "Drama Club",
            "Debate Club",
            "Science Club"
        ]
        
        # Act: Get activities from API
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Verify all activities are present
        assert response.status_code == 200
        for activity in expected_activities:
            assert activity in data

    def test_get_activities_includes_participant_details(self, client):
        """Test that each activity includes participant details"""
        # Arrange: (No setup needed)
        
        # Act: Get activities from API
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Verify each activity has required fields and participants
        assert response.status_code == 200
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestRootRedirect:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root path redirects to static index.html"""
        # Arrange: (No setup needed)
        
        # Act: Make request to root path, don't follow redirects
        response = client.get("/", follow_redirects=False)
        
        # Assert: Verify redirect response
        assert response.status_code in [307, 308]  # Temporary or permanent redirect
        assert "/static/index.html" in response.headers.get("location", "")


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_valid_activity_and_email(self, client):
        """Test successful signup for an activity"""
        # Arrange: Set up test data
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Act: Sign up for activity
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Assert: Verify successful signup
        assert response.status_code == 200
        assert email in activities[activity]["participants"]
        data = response.json()
        assert "Signed up" in data["message"]

    def test_signup_adds_participant_to_list(self, client):
        """Test that signup actually adds email to participants list"""
        # Arrange: Track initial participant count
        email = "student1@mergington.edu"
        activity = "Programming Class"
        initial_count = len(activities[activity]["participants"])
        
        # Act: Sign up for activity
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Assert: Verify participant was added
        assert response.status_code == 200
        new_count = len(activities[activity]["participants"])
        assert new_count == initial_count + 1
        assert email in activities[activity]["participants"]

    def test_signup_activity_not_found(self, client):
        """Test signup fails with 404 when activity doesn't exist"""
        # Arrange: Use non-existent activity
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"
        
        # Act: Attempt to sign up
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Assert: Verify 404 response
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email_blocked(self, client):
        """Test that duplicate signup is prevented"""
        # Arrange: Use already registered participant
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act: Attempt to sign up with existing email
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Assert: Verify 400 error for duplicate
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_error_message_content(self, client):
        """Test that error messages are informative"""
        # Arrange: Use invalid activity to trigger error
        email = "student@mergington.edu"
        activity = "Invalid Activity"
        
        # Act: Attempt signup with invalid activity
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Assert: Verify error contains helpful detail
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert len(data["detail"]) > 0

    def test_signup_multiple_different_activities(self, client):
        """Test that same email can signup for multiple different activities"""
        # Arrange: Use same email for two different activities
        email = "versatile@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Drama Club"
        
        # Act: Sign up for first activity
        response1 = client.post(
            f"/activities/{activity1}/signup?email={email}"
        )
        
        # Act: Sign up for second activity
        response2 = client.post(
            f"/activities/{activity2}/signup?email={email}"
        )
        
        # Assert: Verify both signups succeeded
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_unregister_removes_participant(self, client):
        """Test that unregistering removes participant from activity"""
        # Arrange: Use existing participant
        email = "michael@mergington.edu"
        activity = "Chess Club"
        initial_participants = list(activities[activity]["participants"])
        
        # Act: Unregister participant
        response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        
        # Assert: Verify participant was removed
        assert response.status_code == 200
        assert email not in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) < len(initial_participants)

    def test_unregister_decrements_count(self, client):
        """Test that unregister decreases participant count"""
        # Arrange: Get initial count
        email = "emma@mergington.edu"
        activity = "Programming Class"
        initial_count = len(activities[activity]["participants"])
        
        # Act: Unregister participant
        response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        
        # Assert: Verify count decreased by exactly 1
        assert response.status_code == 200
        new_count = len(activities[activity]["participants"])
        assert new_count == initial_count - 1

    def test_unregister_returns_success_message(self, client):
        """Test that delete returns appropriate success message"""
        # Arrange: Use existing participant
        email = "john@mergington.edu"
        activity = "Gym Class"
        
        # Act: Unregister participant
        response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        
        # Assert: Verify success message
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]

    def test_unregister_activity_not_found(self, client):
        """Test unregister fails with 404 when activity doesn't exist"""
        # Arrange: Use non-existent activity
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"
        
        # Act: Attempt to unregister
        response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        
        # Assert: Verify 404 response
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_participant_not_found(self, client):
        """Test unregister fails with 404 when participant not in activity"""
        # Arrange: Use participant not in this activity
        email = "michael@mergington.edu"  # Only in Chess Club
        activity = "Drama Club"
        
        # Act: Attempt to unregister from wrong activity
        response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        
        # Assert: Verify 404 response
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_unregister_nonexistent_email(self, client):
        """Test unregister fails with 404 for email never registered"""
        # Arrange: Use email that doesn't exist
        email = "nobody@mergington.edu"
        activity = "Soccer Club"
        
        # Act: Attempt to unregister non-existent participant
        response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        
        # Assert: Verify 404 response
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_unregister_then_signup_again(self, client):
        """Test that participant can re-signup after unregistering"""
        # Arrange: Use existing participant
        email = "mason@mergington.edu"
        activity = "Drama Club"
        
        # Act: Unregister
        response1 = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        
        # Assert: Verify unregistration
        assert response1.status_code == 200
        assert email not in activities[activity]["participants"]
        
        # Act: Sign up again
        response2 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Assert: Verify re-signup succeeded
        assert response2.status_code == 200
        assert email in activities[activity]["participants"]
