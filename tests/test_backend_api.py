from src.app import activities


def test_root_redirects_to_static_index(client):
    # Arrange
    endpoint = "/"

    # Act
    response = client.get(endpoint, follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_static_index_is_accessible(client):
    # Arrange
    endpoint = "/static/index.html"

    # Act
    response = client.get(endpoint)

    # Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_get_activities_returns_activity_catalog(client):
    # Arrange
    endpoint = "/activities"

    # Act
    response = client.get(endpoint)

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"] == activities["Chess Club"]["participants"]


def test_signup_adds_student_to_participants(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    endpoint = f"/activities/{activity_name}/signup"
    assert email not in activities[activity_name]["participants"]

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_existing_student_returns_400(client):
    # Arrange
    activity_name = "Programming Class"
    email = activities[activity_name]["participants"][0]
    endpoint = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"
    endpoint = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_student_from_participants(client):
    # Arrange
    activity_name = "Gym Class"
    email = "remove.me@mergington.edu"
    signup_endpoint = f"/activities/{activity_name}/signup"
    unregister_endpoint = f"/activities/{activity_name}/unregister"
    setup_response = client.post(signup_endpoint, params={"email": email})
    assert setup_response.status_code == 200
    assert email in activities[activity_name]["participants"]

    # Act
    response = client.post(unregister_endpoint, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"
    endpoint = f"/activities/{activity_name}/unregister"

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_unknown_student_returns_404(client):
    # Arrange
    activity_name = "Basketball Team"
    email = "missing.student@mergington.edu"
    endpoint = f"/activities/{activity_name}/unregister"
    assert email not in activities[activity_name]["participants"]

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student not found in this activity"}