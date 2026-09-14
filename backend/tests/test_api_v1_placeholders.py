from fastapi.testclient import TestClient


def test_recommendations_placeholder(client: TestClient):
    """Verify that recommendations endpoint returns 501 Not Implemented in foundation."""
    response = client.post("/api/v1/recommendations")
    assert response.status_code == 501
    data = response.json()
    assert "not implemented" in data["detail"].lower()
    assert data["status_code"] == 501
    assert "Stage 7" in data["stage_scheduled"]


def test_recommendations_status_placeholder(client: TestClient):
    """Verify that task status endpoint returns 501 Not Implemented."""
    response = client.get("/api/v1/recommendations/test-task-123")
    assert response.status_code == 501
    data = response.json()
    assert "test-task-123" in data["detail"]


def test_profiles_placeholder(client: TestClient):
    """Verify that profiles endpoint returns 501 Not Implemented in foundation."""
    response = client.post("/api/v1/profiles")
    assert response.status_code == 501
    data = response.json()
    assert "not implemented" in data["detail"].lower()
    assert data["status_code"] == 501


def test_whatif_placeholder(client: TestClient):
    """Verify that whatif endpoint returns 501 Not Implemented in foundation."""
    response = client.post("/api/v1/whatif")
    assert response.status_code == 501
    data = response.json()
    assert "not implemented" in data["detail"].lower()
    assert data["status_code"] == 501
