import os
import yaml
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_docker_compose_specification():
    """Validate that docker-compose.yml defines all required services with valid structure."""
    compose_path = os.path.join(ROOT_DIR, "docker-compose.yml")
    assert os.path.exists(compose_path), "docker-compose.yml does not exist"

    with open(compose_path, "r", encoding="utf-8") as f:
        compose_data = yaml.safe_load(f)

    assert "services" in compose_data, "No services defined in docker-compose.yml"
    services = compose_data["services"]

    # 1. Check all required services are defined
    required_services = [
        "frontend",
        "backend",
        "postgres",
        "redis",
        "celery-worker",
        "nginx",
    ]
    for svc in required_services:
        assert svc in services, f"Service '{svc}' is missing from docker-compose.yml"

    # 2. Check Postgres configuration
    postgres = services["postgres"]
    assert "postgres:15-alpine" in postgres["image"]
    assert "healthcheck" in postgres
    assert any("postgres_data" in v for v in postgres.get("volumes", []))

    # 3. Check Redis configuration
    redis_svc = services["redis"]
    assert "redis:7-alpine" in redis_svc["image"]
    assert "healthcheck" in redis_svc

    # 4. Check Backend configuration
    backend = services["backend"]
    assert backend["build"]["context"] == "./backend"
    assert "depends_on" in backend
    assert "postgres" in backend["depends_on"]
    assert "redis" in backend["depends_on"]

    # 5. Check Celery Worker configuration
    celery = services["celery-worker"]
    assert "celery" in celery["command"]
    assert "redis" in celery["depends_on"]

    # 6. Check Nginx Gateway configuration
    nginx = services["nginx"]
    assert nginx["build"]["context"] == "./nginx"
    assert "80:80" in nginx["ports"]
    assert "frontend" in nginx["depends_on"]
    assert "backend" in nginx["depends_on"]

    # 7. Check Networks & Volumes
    assert "xport_network" in compose_data.get("networks", {})
    assert "postgres_data" in compose_data.get("volumes", {})
    assert "redis_data" in compose_data.get("volumes", {})


def test_environment_examples():
    """Verify that .env.example files exist and have required baseline variables."""
    root_env = os.path.join(ROOT_DIR, ".env.example")
    assert os.path.exists(root_env), "Root .env.example missing"

    with open(root_env, "r", encoding="utf-8") as f:
        content = f.read()

    assert "DATABASE_URL=" in content
    assert "REDIS_URL=" in content
    assert "CELERY_BROKER_URL=" in content
    assert "VITE_API_BASE_URL=" in content


def test_dockerfiles_exist():
    """Verify that Dockerfiles exist for backend, frontend, and nginx."""
    assert os.path.exists(os.path.join(ROOT_DIR, "backend", "Dockerfile"))
    assert os.path.exists(os.path.join(ROOT_DIR, "frontend", "Dockerfile"))
    assert os.path.exists(os.path.join(ROOT_DIR, "nginx", "Dockerfile"))
    assert os.path.exists(os.path.join(ROOT_DIR, "nginx", "nginx.conf"))
