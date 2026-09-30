from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.tasks import run_portfolio_optimization_task
from app.repositories.recommendation_repository import RecommendationRepository


def test_submit_recommendation_with_payload(client: TestClient):
    """Verify submitting a POST recommendation with JSON payload dispatches job and returns 202 Accepted."""
    payload = {
        "symbols": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"],
        "pop_size": 20,
        "generations": 20,
    }
    response = client.post("/api/v1/recommendations", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    assert "recommendation_id" in data
    assert data["status"] == "PENDING"
    assert data["symbols"] == ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]


def test_get_recommendation_status_endpoint(client: TestClient, db_session: Session):
    """Verify querying GET /api/v1/recommendations/{id} returns saved recommendation result."""
    repo = RecommendationRepository(db_session)
    rec = repo.create_recommendation(
        symbols={"symbols": ["RELIANCE.NS", "TCS.NS"]},
        task_id="test-task-999",
        recommendation_id="rec-uuid-12345",
    )
    repo.update_recommendation(
        recommendation_id=rec.id,
        status="COMPLETED",
        result_data={
            "status": "success",
            "algorithm": "NSGA-II",
            "pareto_portfolios": [
                {
                    "portfolio_id": 1,
                    "weights": {"RELIANCE.NS": 0.6, "TCS.NS": 0.4},
                    "metrics": {"expected_return": 0.15, "volatility": 0.12, "sharpe_ratio": 0.83},
                }
            ],
        },
    )

    response = client.get(f"/api/v1/recommendations/{rec.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["recommendation_id"] == "rec-uuid-12345"
    assert data["status"] == "COMPLETED"
    assert "result_data" in data
    assert len(data["result_data"]["pareto_portfolios"]) == 1


@patch("app.core.tasks.SessionLocal")
def test_run_portfolio_optimization_celery_task(mock_session_local, db_session: Session, populated_market_data):
    """Verify Celery task run_portfolio_optimization_task executes eagerly and stores result in DB."""
    mock_session_local.return_value = db_session
    result = run_portfolio_optimization_task(
        symbols=populated_market_data,
        pop_size=20,
        generations=20,
        recommendation_id="rec-celery-test-1",
    )
    assert result["status"] == "success"
    assert result["algorithm"] == "NSGA-II"

    repo = RecommendationRepository(db_session)
    stored_rec = repo.get_by_id_or_task_id("rec-celery-test-1")
    assert stored_rec is not None
    assert stored_rec.status == "COMPLETED"
    assert stored_rec.result_data["num_solutions"] > 0
