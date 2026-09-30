"""
XPort — NSGA-II Multi-Objective Portfolio Optimizer Demonstration Script
For Code Evaluation & Project Review
"""
import os
import sys
import json
import datetime
import numpy as np

# Add parent directory to sys.path for direct execution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.db.base import Base
from app.models.market_data import MarketData
from app.models.engineered_features import EngineeredFeatures
from app.repositories.market_data_repository import MarketDataRepository
from app.repositories.engineered_features_repository import EngineeredFeaturesRepository
from app.services.portfolio_optimizer import PortfolioOptimizer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


def run_evaluation_demo():
    print("=" * 80)
    print("           XPORT: EXPLAINABLE MULTI-OBJECTIVE PORTFOLIO OPTIMIZATION          ")
    print("                       NSGA-II EVALUATION DEMONSTRATION                       ")
    print("=" * 80)
    print("\n[1] Initializing isolated evaluation database session...")

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]
    print(f"[2] Seeding historical market data & engineered features for: {', '.join(symbols)}")
    
    np.random.seed(42)
    m_repo = MarketDataRepository(db)
    f_repo = EngineeredFeaturesRepository(db)
    dates = [datetime.date(2025, 1, 1) + datetime.timedelta(days=i) for i in range(120)]

    for sym in symbols:
        m_recs = []
        f_recs = []
        base_price = 2500.0 if "RELIANCE" in sym else (3800.0 if "TCS" in sym else (1600.0 if "HDFCBANK" in sym else 1800.0))
        price = base_price
        
        # Give assets distinct return/volatility profiles for clear Pareto trade-offs
        mean_ret = 0.0012 if "RELIANCE" in sym else (0.0008 if "TCS" in sym else 0.0005)
        vol_scale = 0.015 if "RELIANCE" in sym else (0.010 if "TCS" in sym else 0.008)

        for d in dates:
            ret = float(np.random.normal(mean_ret, vol_scale))
            price *= (1.0 + ret)
            vol = int(np.random.randint(100000, 500000))

            m_recs.append({
                "symbol": sym, "date": d, "open": round(price * 0.998, 2), "high": round(price * 1.01, 2),
                "low": round(price * 0.99, 2), "close": round(price, 2), "adj_close": round(price, 2), "volume": vol
            })
            f_recs.append({
                "symbol": sym, "date": d, "sma_20": round(price * 0.99, 2), "sma_50": round(price * 0.98, 2),
                "ema_20": round(price * 0.995, 2), "rsi_14": 55.0, "macd": 2.0, "macd_signal": 1.5,
                "macd_histogram": 0.5, "daily_return": ret, "rolling_volatility": vol_scale * np.sqrt(252)
            })

        m_repo.upsert_records(m_recs)
        f_repo.upsert_records(f_recs)

    print("[3] Executing NSGA-II Genetic Algorithm (pymoo)...")
    print("    - Objective 1: Maximize Annualized Return (-Expected Return)")
    print("    - Objective 2: Minimize Portfolio Volatility / Risk")
    print("    - Objective 3: Maximize Liquidity Score (-Liquidity)")
    print("    - Constraints: Long-only (w_i >= 0), sum(w_i) == 1.0")

    optimizer = PortfolioOptimizer(db)
    result = optimizer.optimize(symbols=symbols, pop_size=30, generations=30)

    print("\n" + "=" * 80)
    print("                            PARETO FRONTIER SUMMARY                           ")
    print("=" * 80)
    print(f"Algorithm:           {result['algorithm']}")
    print(f"Population Size:     {result['population_size']}")
    print(f"Generations:         {result['generations']}")
    print(f"Pareto Portfolios:   {result['num_solutions']}")
    print("-" * 80)
    print(f"{'ID':<4} | {'Exp Return':<10} | {'Volatility':<10} | {'Liquidity':<10} | {'Sharpe Ratio':<12} | {'Top Allocations'}")
    print("-" * 80)

    for p in result['pareto_portfolios'][:8]:  # Show top 8 representative solutions
        p_id = p['portfolio_id']
        m = p['metrics']
        w = p['weights']
        top_w = ", ".join([f"{k.split('.')[0]}:{v*100:.1f}%" for k, v in w.items() if v >= 0.05])
        print(f"{p_id:<4} | {m['expected_return']*100:>8.2f}% | {m['volatility']*100:>8.2f}% | {m['liquidity_score']:>10.4f} | {m['sharpe_ratio']:>12.4f} | {top_w}")

    print("-" * 80)
    print("\n[4] Complete JSON Payload (Sample 1st Optimal Portfolio):")
    sample_res = dict(result)
    sample_res['pareto_portfolios'] = result['pareto_portfolios'][:2]
    print(json.dumps(sample_res, indent=2))
    print("\n" + "=" * 80)
    print("                      DEMONSTRATION COMPLETED SUCCESSFULLY                    ")
    print("=" * 80)


if __name__ == "__main__":
    run_evaluation_demo()
