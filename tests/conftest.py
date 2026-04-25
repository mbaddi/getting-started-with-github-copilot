"""
Pytest configuration and fixtures for FastAPI tests.
Provides test client, fresh activity data, and isolation between tests.
"""

import copy
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """
    ARRANGE: Provides a TestClient instance for making requests to the FastAPI app.
    Scope: Function (fresh instance per test)
    """
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """
    ARRANGE: Provides a fresh copy of activities data for each test.
    This fixture resets the global activities dict to a known state,
    preventing test pollution from other tests.
    
    Scope: Function (isolated copy per test)
    Autouse: False (explicitly used when needed)
    """
    # Create a deep copy of the original activities
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice and compete in basketball games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Train and play soccer matches",
            "schedule": "Mondays and Wednesdays, 3:00 PM - 5:00 PM",
            "max_participants": 22,
            "participants": []
        },
        "Art Club": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "Drama Club": {
            "description": "Act in plays and improve theatrical skills",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Debate Club": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Conduct experiments and learn about scientific concepts",
            "schedule": "Fridays, 2:00 PM - 4:00 PM",
            "max_participants": 25,
            "participants": []
        }
    }
    
    # Reset the global activities dict
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    
    # Yield the reference to activities for use in tests
    yield activities
    
    # Cleanup: reset activities after test completes
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


@pytest.fixture
def sample_data():
    """
    ARRANGE: Provides sample test data (email addresses, activity names) for assertions.
    Scope: Function
    """
    return {
        "existing_student_chess": "michael@mergington.edu",
        "existing_student_programming": "emma@mergington.edu",
        "new_student": "newstudent@mergington.edu",
        "another_student": "anotherstudent@mergington.edu",
        "activity_with_participants": "Chess Club",
        "activity_without_participants": "Basketball Team",
        "nonexistent_activity": "Nonexistent Club",
    }
