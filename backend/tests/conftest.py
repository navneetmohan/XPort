import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.celery_app import celery


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Session test client for FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def configure_celery_eager():
    """Configure Celery to execute tasks synchronously during tests."""
    celery.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )
    yield
    celery.conf.update(
        task_always_eager=False,
        task_eager_propagates=False,
    )
