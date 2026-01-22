import pytest


def test_root_redirect(client):
    """Test that root path redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "/static/index.html" in response.headers["location"]


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    
    # Check structure of an activity
    chess = activities["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert "participants" in chess
    assert isinstance(chess["participants"], list)


def test_signup_for_activity_success(client):
    """Test successfully signing up for an activity"""
    response = client.post(
        "/activities/Basketball Team/signup?email=student@mergington.edu"
    )
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    assert "student@mergington.edu" in result["message"]
    
    # Verify the participant was added
    activities = client.get("/activities").json()
    assert "student@mergington.edu" in activities["Basketball Team"]["participants"]


def test_signup_for_nonexistent_activity(client):
    """Test signing up for an activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Club/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_student(client):
    """Test that a student can't sign up twice for the same activity"""
    email = "duplicate@mergington.edu"
    
    # First signup should succeed
    response1 = client.post(
        f"/activities/Soccer Club/signup?email={email}"
    )
    assert response1.status_code == 200
    
    # Second signup should fail
    response2 = client.post(
        f"/activities/Soccer Club/signup?email={email}"
    )
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_unregister_from_activity_success(client):
    """Test successfully unregistering from an activity"""
    email = "unregister@mergington.edu"
    
    # Sign up first
    client.post(f"/activities/Drama Club/signup?email={email}")
    
    # Verify they're signed up
    activities = client.get("/activities").json()
    assert email in activities["Drama Club"]["participants"]
    
    # Unregister
    response = client.post(
        f"/activities/Drama Club/unregister?email={email}"
    )
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]
    
    # Verify they're removed
    activities = client.get("/activities").json()
    assert email not in activities["Drama Club"]["participants"]


def test_unregister_from_nonexistent_activity(client):
    """Test unregistering from an activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_student_not_registered(client):
    """Test unregistering a student who isn't registered"""
    response = client.post(
        "/activities/Art Club/unregister?email=notregistered@mergington.edu"
    )
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


def test_initial_participants(client):
    """Test that initial participants are present"""
    activities = client.get("/activities").json()
    
    # Chess Club should have michael and daniel
    chess = activities["Chess Club"]
    assert "michael@mergington.edu" in chess["participants"]
    assert "daniel@mergington.edu" in chess["participants"]
    assert len(chess["participants"]) == 2
    
    # Programming Class should have emma and sophia
    prog = activities["Programming Class"]
    assert "emma@mergington.edu" in prog["participants"]
    assert "sophia@mergington.edu" in prog["participants"]


def test_max_participants_not_enforced_in_basic_signup(client):
    """Test that we can sign up beyond max_participants in basic implementation"""
    activity_name = "Debate Team"
    activities = client.get("/activities").json()
    max_participants = activities[activity_name]["max_participants"]
    
    # Sign up multiple students
    for i in range(max_participants + 2):
        email = f"student{i}@mergington.edu"
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert response.status_code == 200
    
    # Verify all were added
    activities = client.get("/activities").json()
    assert len(activities[activity_name]["participants"]) == max_participants + 2
