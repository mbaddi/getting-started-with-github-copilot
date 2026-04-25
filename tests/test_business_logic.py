"""
Unit tests for FastAPI business logic.
Tests core validation and data manipulation logic using AAA pattern.
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import activities


class TestActivityValidation:
    """Unit tests for activity existence validation"""

    def test_activity_exists_in_data(self, fresh_activities):
        """
        ARRANGE: Fresh activities with known activity names
        ACT: Check if specific activity exists in activities dict
        ASSERT: Verify activity exists
        """
        # ARRANGE
        activity_name = "Chess Club"

        # ACT
        activity_exists = activity_name in fresh_activities

        # ASSERT
        assert activity_exists is True

    def test_nonexistent_activity_not_in_data(self, fresh_activities):
        """
        ARRANGE: Fresh activities
        ACT: Check if nonexistent activity name exists in dict
        ASSERT: Verify it doesn't exist
        """
        # ARRANGE
        activity_name = "Nonexistent Club"

        # ACT
        activity_exists = activity_name in fresh_activities

        # ASSERT
        assert activity_exists is False

    def test_all_expected_activities_exist(self, fresh_activities):
        """
        ARRANGE: Fresh activities with known count
        ACT: Check all 9 activities exist
        ASSERT: Verify all 9 are present
        """
        # ARRANGE
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Soccer Club", "Art Club", "Drama Club", "Debate Club", "Science Club"
        ]

        # ACT
        all_exist = all(activity in fresh_activities for activity in expected_activities)

        # ASSERT
        assert all_exist is True


class TestDuplicateEnrollmentDetection:
    """Unit tests for detecting duplicate enrollments"""

    def test_student_already_enrolled_returns_true(self, fresh_activities):
        """
        ARRANGE: Fresh activities with known enrolled students
        ACT: Check if enrolled student email is in participants list
        ASSERT: Verify it is enrolled
        """
        # ARRANGE
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # ACT
        is_enrolled = email in fresh_activities[activity_name]["participants"]

        # ASSERT
        assert is_enrolled is True

    def test_student_not_enrolled_returns_false(self, fresh_activities):
        """
        ARRANGE: Fresh activities, new email not in any activity
        ACT: Check if new student email is in participants list
        ASSERT: Verify it is not enrolled
        """
        # ARRANGE
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # ACT
        is_enrolled = email in fresh_activities[activity_name]["participants"]

        # ASSERT
        assert is_enrolled is False

    def test_duplicate_check_different_activities(self, fresh_activities):
        """
        ARRANGE: Fresh activities with student enrolled in one activity
        ACT: Check enrollment in different activities
        ASSERT: Verify student is not enrolled in other activities
        """
        # ARRANGE
        email = "michael@mergington.edu"
        enrolled_activity = "Chess Club"
        other_activity = "Programming Class"

        # ACT
        is_enrolled_in_chess = email in fresh_activities[enrolled_activity]["participants"]
        is_enrolled_in_programming = email in fresh_activities[other_activity]["participants"]

        # ASSERT
        assert is_enrolled_in_chess is True
        assert is_enrolled_in_programming is False


class TestParticipantListOperations:
    """Unit tests for participants list add/remove operations"""

    def test_adding_participant_increases_count(self, fresh_activities):
        """
        ARRANGE: Fresh activities, count participants before adding
        ACT: Add new participant to list
        ASSERT: Verify count increased by 1
        """
        # ARRANGE
        email = "newstudent@mergington.edu"
        activity_name = "Basketball Team"
        initial_count = len(fresh_activities[activity_name]["participants"])

        # ACT
        fresh_activities[activity_name]["participants"].append(email)
        new_count = len(fresh_activities[activity_name]["participants"])

        # ASSERT
        assert new_count == initial_count + 1

    def test_added_participant_is_in_list(self, fresh_activities):
        """
        ARRANGE: Fresh activities, new email
        ACT: Add participant to list
        ASSERT: Verify participant can be found in list
        """
        # ARRANGE
        email = "newstudent@mergington.edu"
        activity_name = "Basketball Team"

        # ACT
        fresh_activities[activity_name]["participants"].append(email)
        is_in_list = email in fresh_activities[activity_name]["participants"]

        # ASSERT
        assert is_in_list is True

    def test_removing_participant_decreases_count(self, fresh_activities):
        """
        ARRANGE: Fresh activities with enrolled student, count participants
        ACT: Remove participant from list
        ASSERT: Verify count decreased by 1
        """
        # ARRANGE
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        initial_count = len(fresh_activities[activity_name]["participants"])

        # ACT
        fresh_activities[activity_name]["participants"].remove(email)
        new_count = len(fresh_activities[activity_name]["participants"])

        # ASSERT
        assert new_count == initial_count - 1

    def test_removed_participant_not_in_list(self, fresh_activities):
        """
        ARRANGE: Fresh activities with enrolled student
        ACT: Remove participant from list
        ASSERT: Verify participant no longer in list
        """
        # ARRANGE
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # ACT
        fresh_activities[activity_name]["participants"].remove(email)
        is_in_list = email in fresh_activities[activity_name]["participants"]

        # ASSERT
        assert is_in_list is False


class TestUnenrollmentValidation:
    """Unit tests for validating unenrollment operations"""

    def test_enrolled_student_can_be_removed(self, fresh_activities):
        """
        ARRANGE: Fresh activities, enrolled student, activity
        ACT: Check if student is in list before removal
        ASSERT: Verify student is enrolled and can theoretically be removed
        """
        # ARRANGE
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # ACT
        is_enrolled = email in fresh_activities[activity_name]["participants"]

        # ASSERT
        assert is_enrolled is True

    def test_not_enrolled_student_cannot_be_removed(self, fresh_activities):
        """
        ARRANGE: Fresh activities, student NOT enrolled, activity
        ACT: Check if student is in list
        ASSERT: Verify student is not enrolled (would cause error if removed)
        """
        # ARRANGE
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # ACT
        is_enrolled = email in fresh_activities[activity_name]["participants"]

        # ASSERT
        assert is_enrolled is False

    def test_remove_validates_before_error(self, fresh_activities):
        """
        ARRANGE: Fresh activities, not-enrolled student
        ACT: Try to remove student not in list (should raise ValueError)
        ASSERT: Verify ValueError is raised
        """
        # ARRANGE
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # ACT & ASSERT
        with pytest.raises(ValueError):
            fresh_activities[activity_name]["participants"].remove(email)


class TestParticipantDataIntegrity:
    """Unit tests for participants list data structure integrity"""

    def test_participants_is_list(self, fresh_activities):
        """
        ARRANGE: Fresh activities
        ACT: Check type of participants field
        ASSERT: Verify it's a list
        """
        # ARRANGE & ACT
        activity_name = "Chess Club"
        participants_type = type(fresh_activities[activity_name]["participants"])

        # ASSERT
        assert participants_type is list

    def test_all_activities_have_participants_list(self, fresh_activities):
        """
        ARRANGE: Fresh activities
        ACT: Check all activities have participants field that is a list
        ASSERT: Verify all activities comply
        """
        # ARRANGE & ACT
        all_valid = all(
            isinstance(activity_data["participants"], list)
            for activity_data in fresh_activities.values()
        )

        # ASSERT
        assert all_valid is True

    def test_participants_contain_valid_emails(self, fresh_activities):
        """
        ARRANGE: Fresh activities with known participants
        ACT: Check participants contain valid email strings
        ASSERT: Verify all participants are strings with @ symbol (basic email format)
        """
        # ARRANGE
        activity_name = "Chess Club"

        # ACT
        participants = fresh_activities[activity_name]["participants"]
        all_valid_emails = all(
            isinstance(p, str) and "@" in p
            for p in participants
        )

        # ASSERT
        assert all_valid_emails is True
