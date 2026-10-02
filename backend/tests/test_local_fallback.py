from unittest.mock import patch
from fastapi.testclient import TestClient

from app.core.celery_app import celery
from app.api.v1.endpoints.market_data import LOCAL_TASK_STORE


def test_market_data_refresh_local_fallback_when_redis_offline(client: TestClient):
    """
    Test that when Redis and Celery are offline (not eager), POST /api/v1/market-data/refresh
    falls back cleanly to background execution, stores status in LOCAL_TASK_STORE,
    and returns 202 Accepted rather than raising a 500 error.
    """
    orig_eager = celery.conf.task_always_eager
    celery.conf.task_always_eager = False
    try:
        with patch("app.api.v1.endpoints.market_data.check_redis_connection", return_value=False), \
             patch("app.api.v1.endpoints.market_data.refresh_market_data_task.run") as mock_run:
            mock_run.return_value = {"status": "success", "rows_fetched": 10}

            payload = {"symbols": ["RELIANCE.NS"], "lookback_days": 30}
            response = client.post("/api/v1/market-data/refresh", json=payload)

            assert response.status_code == 202
            data = response.json()
            assert "task_id" in data
            assert data["task_id"].startswith("local-refresh-")
            assert data["status"] == "PENDING"

            # Check that polling the task status endpoint resolves properly from LOCAL_TASK_STORE
            task_id = data["task_id"]
            status_res = client.get(f"/api/v1/market-data/task/{task_id}")
            assert status_res.status_code == 200
            status_data = status_res.json()
            assert status_data["task_id"] == task_id
            assert status_data["ready"] is True
            assert status_data["status"] == "SUCCESS"
    finally:
        celery.conf.task_always_eager = orig_eager


def test_market_data_sync_local_fallback_when_redis_offline(client: TestClient):
    """
    Test that when Redis is offline (not eager), POST /api/v1/market-data/sync
    falls back to background execution and returns 202 Accepted.
    """
    orig_eager = celery.conf.task_always_eager
    celery.conf.task_always_eager = False
    try:
        with patch("app.api.v1.endpoints.market_data.check_redis_connection", return_value=False), \
             patch("app.api.v1.endpoints.market_data.sync_market_data_task.run") as mock_run:
            mock_run.return_value = {"status": "success", "rows_fetched": 5}

            payload = {"symbols": ["TCS.NS"], "lookback_days": 10}
            response = client.post("/api/v1/market-data/sync", json=payload)

            assert response.status_code == 202
            data = response.json()
            assert "task_id" in data
            assert data["task_id"].startswith("local-sync-")
    finally:
        celery.conf.task_always_eager = orig_eager


def test_recommendations_local_fallback_when_redis_offline(client: TestClient):
    """
    Test that when Redis is offline (not eager), POST /api/v1/recommendations
    dispatches optimization locally and returns 202 Accepted.
    """
    orig_eager = celery.conf.task_always_eager
    celery.conf.task_always_eager = False
    try:
        with patch("app.api.v1.endpoints.recommendations.check_redis_connection", return_value=False), \
             patch("app.core.tasks.run_portfolio_optimization_task.run") as mock_opt:
            mock_opt.return_value = {"status": "success"}

            payload = {
                "symbols": ["RELIANCE.NS", "TCS.NS"],
                "pop_size": 20,
                "generations": 20,
            }
            response = client.post("/api/v1/recommendations", json=payload)

            assert response.status_code == 202
            data = response.json()
            assert "task_id" in data
            assert data["task_id"].startswith("local-task-")
    finally:
        celery.conf.task_always_eager = orig_eager
