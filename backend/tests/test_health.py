from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Verify that root endpoint responds with metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "project" in data
    assert "version" in data
    assert "health_url" in data


def test_health_endpoint(client: TestClient):
    """Verify that /api/v1/health returns ok status and environment."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "timestamp" in data
    assert "database" in data
    assert "redis" in data


def test_root_health_alias(client: TestClient):
    """Verify that root /health alias responds identical to v1 health."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
