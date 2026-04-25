"""
Integration tests for FastAPI endpoints.
Tests all API endpoints (GET /activities, POST /signup, DELETE /unregister, GET /) using AAA pattern.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client, fresh_activities):
        """
        ARRANGE: TestClient is ready, activities fixture provides 9 activities
        ACT: Make GET request to /activities
        ASSERT: Verify response contains all 9 activities with correct structure
        """
        # ARRANGE
        expected_activity_count = 9
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Soccer Club", "Art Club", "Drama Club", "Debate Club", "Science Club"
        ]

        # ACT
        response = client.get("/activities")

        # ASSERT
        assert response.status_code == 200
        all_activities = response.json()
        assert len(all_activities) == expected_activity_count
        for activity_name in expected_activities:
            assert activity_name in all_activities

    def test_get_activities_response_structure(self, client, fresh_activities):
        """
        ARRANGE: TestClient with activities
        ACT: Make GET request to /activities
        ASSERT: Verify each activity has required fields (description, schedule, max_participants, participants)
        """
        # ARRANGE
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # ACT
        response = client.get("/activities")
        all_activities = response.json()

        # ASSERT
        assert response.status_code == 200
        for activity_name, activity_data in all_activities.items():
            for field in required_fields:
                assert field in activity_data, f"Field '{field}' missing in {activity_name}"
            # Verify participants is a list
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestGetRoot:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """
        ARRANGE: TestClient ready
        ACT: Make GET request to / with follow_redirects=False
        ASSERT: Verify redirect status 307 and location header points to /static/index.html
        """
        # ARRANGE
        expected_redirect_url = "/static/index.html"

        # ACT
        response = client.get("/", follow_redirects=False)

        # ASSERT
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_url


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, fresh_activities, sample_data):
        """
        ARRANGE: Fresh activities, new student email, existing activity
        ACT: POST /activities/{activity_name}/signup with email
        ASSERT: Verify 200 response, confirmation message, and participant added to activity
        """
        # ARRANGE
        email = sample_data["new_student"]
        activity_name = sample_data["activity_without_participants"]

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 200
        assert f"Signed up {email} for {activity_name}" in response.json()["message"]
        assert email in fresh_activities[activity_name]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client, fresh_activities, sample_data):
        """
        ARRANGE: Fresh activities, new student email, nonexistent activity
        ACT: POST /activities/{nonexistent}/signup
        ASSERT: Verify 404 response with appropriate error message
        """
        # ARRANGE
        email = sample_data["new_student"]
        activity_name = sample_data["nonexistent_activity"]

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_enrollment_returns_400(self, client, fresh_activities, sample_data):
        """
        ARRANGE: Fresh activities, student already enrolled in activity
        ACT: POST /activities/{activity_name}/signup with already-enrolled email
        ASSERT: Verify 400 response with duplicate enrollment error
        """
        # ARRANGE
        email = sample_data["existing_student_chess"]
        activity_name = sample_data["activity_with_participants"]
        # Verify student is already enrolled
        assert email in fresh_activities[activity_name]["participants"]

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_adds_participant_to_participants_list(self, client, fresh_activities, sample_data):
        """
        ARRANGE: Fresh activities, new student, activity with existing participants
        ACT: POST /activities/{activity_name}/signup and verify side effects
        ASSERT: Verify participant count increases, new email in list
        """
        # ARRANGE
        email = sample_data["new_student"]
        activity_name = sample_data["activity_with_participants"]
        initial_participant_count = len(fresh_activities[activity_name]["participants"])

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 200
        assert len(fresh_activities[activity_name]["participants"]) == initial_participant_count + 1
        assert email in fresh_activities[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client, fresh_activities, sample_data):
        """
        ARRANGE: Fresh activities, enrolled student, activity with participants
        ACT: DELETE /activities/{activity_name}/unregister
        ASSERT: Verify 200 response, participant removed from activity
        """
        # ARRANGE
        email = sample_data["existing_student_chess"]
        activity_name = sample_data["activity_with_participants"]
        # Verify student is enrolled
        assert email in fresh_activities[activity_name]["participants"]

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 200
        assert email not in fresh_activities[activity_name]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client, fresh_activities, sample_data):
        """
        ARRANGE: Fresh activities, email, nonexistent activity
        ACT: DELETE /activities/{nonexistent}/unregister
        ASSERT: Verify 404 response with error message
        """
        # ARRANGE
        email = sample_data["new_student"]
        activity_name = sample_data["nonexistent_activity"]

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_not_enrolled_student_returns_400(self, client, fresh_activities, sample_data):
        """
        ARRANGE: Fresh activities, student NOT enrolled in activity
        ACT: DELETE /activities/{activity_name}/unregister with non-enrolled email
        ASSERT: Verify 400 response with appropriate error message
        """
        # ARRANGE
        email = sample_data["new_student"]
        activity_name = sample_data["activity_with_participants"]
        # Verify student is NOT enrolled
        assert email not in fresh_activities[activity_name]["participants"]

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not signed up for this activity"

    def test_unregister_removes_participant_from_list(self, client, fresh_activities, sample_data):
        """
        ARRANGE: Fresh activities, enrolled student, activity with participants
        ACT: DELETE /activities/{activity_name}/unregister and verify side effects
        ASSERT: Verify participant count decreases, email removed from list
        """
        # ARRANGE
        email = sample_data["existing_student_chess"]
        activity_name = sample_data["activity_with_participants"]
        initial_participant_count = len(fresh_activities[activity_name]["participants"])

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 200
        assert len(fresh_activities[activity_name]["participants"]) == initial_participant_count - 1
        assert email not in fresh_activities[activity_name]["participants"]
