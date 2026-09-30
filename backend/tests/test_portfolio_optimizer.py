import datetime
import json
import numpy as np
import pytest
from sqlalchemy.orm import Session
from app.services.portfolio_optimizer import PortfolioOptimizer


def test_nsga2_optimization_execution_and_constraints(db_session: Session, populated_market_data):
    """
    Verify NSGA-II optimizer generates valid Pareto frontier solutions with long-only
    weights summing to 1.0 and finite objective metrics.
    """
    optimizer = PortfolioOptimizer(db_session)
    res = optimizer.optimize(symbols=populated_market_data, pop_size=20, generations=20)

    print("\n\n==================== NSGA-II OPTIMIZER OUTPUT ====================")
    print(json.dumps(res, indent=2))
    print("==================================================================\n")

    assert res["status"] == "success"
    assert res["algorithm"] == "NSGA-II"
    assert res["num_solutions"] > 0
    assert len(res["pareto_portfolios"]) > 0

    for port in res["pareto_portfolios"]:
        weights = port["weights"]
        metrics = port["metrics"]

        # 1. Long-only constraint: weights >= 0
        for sym, w in weights.items():
            assert w >= 0.0, f"Weight for {sym} is negative: {w}"

        # 2. Sum of weights == 1.0 (with 1e-3 float rounding tolerance)
        total_weight = sum(weights.values())
        assert abs(total_weight - 1.0) <= 1e-3, f"Weights sum to {total_weight}, expected 1.0"

        # 3. Finite numerical objective metrics
        assert np.isfinite(metrics["expected_return"])
        assert np.isfinite(metrics["volatility"])
        assert metrics["volatility"] >= 0.0
        assert np.isfinite(metrics["liquidity_score"])
        assert np.isfinite(metrics["sharpe_ratio"])


def test_nsga2_insufficient_data_handling(db_session: Session):
    """Verify NSGA-II fails gracefully when market data is insufficient."""
    optimizer = PortfolioOptimizer(db_session)
    with pytest.raises(ValueError) as exc_info:
        optimizer.optimize(symbols=["NON_EXISTENT1.NS", "NON_EXISTENT2.NS"])
    assert "Insufficient market data" in str(exc_info.value)
