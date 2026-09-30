import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
from sqlalchemy.orm import Session
from app.repositories.engineered_features_repository import EngineeredFeaturesRepository
from app.repositories.market_data_repository import MarketDataRepository

logger = logging.getLogger(__name__)


class PortfolioOptimizationProblem(ElementwiseProblem):
    """
    pymoo ElementwiseProblem formulation for Multi-Objective Portfolio Optimization.

    Objectives (all minimized):
      f1: -Expected Return (Annualized)
      f2: Portfolio Volatility / Risk (Annualized Standard Deviation)
      f3: -Portfolio Liquidity (Normalized Average Volume Score)

    Constraints:
      Long-only portfolio weights w_i >= 0, sum(w_i) == 1.
    """

    def __init__(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        liquidity_scores: np.ndarray,
    ):
        self.expected_returns = expected_returns
        self.cov_matrix = cov_matrix
        self.liquidity_scores = liquidity_scores
        n_assets = len(expected_returns)

        super().__init__(
            n_var=n_assets,
            n_obj=3,
            n_ieq_constr=0,
            xl=np.zeros(n_assets),
            xu=np.ones(n_assets),
        )

    def _evaluate(self, x: np.ndarray, out: Dict[str, Any], *args: Any, **kwargs: Any) -> None:
        # Normalize decision variables into valid portfolio weights w summing to 1
        sum_x = np.sum(x)
        if sum_x <= 1e-8:
            weights = np.ones_like(x) / len(x)
        else:
            weights = x / sum_x

        # 1. Expected Return (maximize -> minimize negative)
        exp_return = float(np.dot(weights, self.expected_returns))
        f1 = -exp_return

        # 2. Portfolio Volatility (minimize)
        port_variance = float(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        port_volatility = float(np.sqrt(max(port_variance, 1e-8)))
        f2 = port_volatility

        # 3. Portfolio Liquidity (maximize -> minimize negative)
        port_liquidity = float(np.dot(weights, self.liquidity_scores))
        f3 = -port_liquidity

        out["F"] = [f1, f2, f3]


class PortfolioOptimizer:
    """
    Service for executing NSGA-II Multi-Objective Portfolio Optimization
    using real persisted market data and engineered features.
    """

    def __init__(self, db: Session):
        self.db = db
        self.market_repo = MarketDataRepository(db)
        self.features_repo = EngineeredFeaturesRepository(db)

    def prepare_data(
        self,
        symbols: List[str],
        start_date: Optional[Any] = None,
        end_date: Optional[Any] = None,
    ) -> Tuple[List[str], np.ndarray, np.ndarray, np.ndarray]:
        """
        Fetch historical daily returns and volume data for target symbols
        and construct mean return vector, covariance matrix, and liquidity vector.
        """
        clean_symbols = [s.strip().upper() for s in symbols]
        returns_dict: Dict[str, pd.Series] = {}
        volumes_dict: Dict[str, float] = {}

        for sym in clean_symbols:
            features = self.features_repo.get_features(
                symbol=sym, start_date=start_date, end_date=end_date, limit=5000
            )
            if features:
                s_returns = pd.Series(
                    [f.daily_return for f in features if f.daily_return is not None],
                    index=[f.date for f in features if f.daily_return is not None],
                )
                returns_dict[sym] = s_returns

            market_recs, _ = self.market_repo.get_market_data(
                symbol=sym, start_date=start_date, end_date=end_date, limit=5000
            )
            if market_recs:
                vols = [m.volume for m in market_recs if m.volume is not None and m.volume > 0]
                volumes_dict[sym] = float(np.mean(vols)) if vols else 1.0
            else:
                volumes_dict[sym] = 1.0

        available_symbols = [s for s in clean_symbols if s in returns_dict and len(returns_dict[s]) >= 5]

        if len(available_symbols) < 2:
            raise ValueError(
                f"Insufficient market data available for symbols {symbols}. Need at least 2 symbols with return history."
            )

        # Align return series into a single DataFrame
        returns_df = pd.DataFrame({s: returns_dict[s] for s in available_symbols}).dropna()
        if len(returns_df) < 5:
            raise ValueError(f"Insufficient overlapping return data for symbols {available_symbols}.")

        # Annualized metrics (assuming 252 trading days/year)
        daily_mean_returns = returns_df.mean().values
        expected_returns = daily_mean_returns * 252.0

        daily_cov = returns_df.cov().values
        cov_matrix = daily_cov * 252.0

        # Liquidity vector normalized between [0, 1]
        raw_volumes = np.array([volumes_dict[s] for s in available_symbols])
        max_vol = max(np.max(raw_volumes), 1.0)
        liquidity_scores = raw_volumes / max_vol

        return available_symbols, expected_returns, cov_matrix, liquidity_scores

    def optimize(
        self,
        symbols: List[str],
        pop_size: int = 50,
        generations: int = 50,
        risk_free_rate: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Executes NSGA-II optimization and returns Pareto-optimal portfolio allocations.
        """
        target_symbols = symbols or ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]
        
        valid_symbols, exp_returns, cov_matrix, liquidity_scores = self.prepare_data(target_symbols)

        problem = PortfolioOptimizationProblem(
            expected_returns=exp_returns,
            cov_matrix=cov_matrix,
            liquidity_scores=liquidity_scores,
        )

        algorithm = NSGA2(pop_size=pop_size)

        res = minimize(
            problem,
            algorithm,
            termination=("n_gen", generations),
            seed=42,
            verbose=False,
        )

        if res.X is None or len(res.X) == 0:
            raise RuntimeError("NSGA-II optimization failed to return valid candidate solutions.")

        pareto_portfolios: List[Dict[str, Any]] = []

        # Extract Pareto solutions
        for idx in range(len(res.X)):
            x_raw = res.X[idx]
            sum_x = float(np.sum(x_raw))
            if sum_x <= 1e-8:
                raw_weights = np.ones_like(x_raw) / len(x_raw)
            else:
                raw_weights = x_raw / sum_x

            # Clean and normalize weights
            weights = np.clip(raw_weights, 0.0, 1.0)
            weights = weights / float(np.sum(weights))

            exp_ret = float(np.dot(weights, exp_returns))
            port_var = float(np.dot(weights.T, np.dot(cov_matrix, weights)))
            volatility = float(np.sqrt(max(port_var, 1e-8)))
            liquidity = float(np.dot(weights, liquidity_scores))
            sharpe = float((exp_ret - risk_free_rate) / max(volatility, 1e-4))

            weights_dict = {
                valid_symbols[i]: float(round(weights[i], 4))
                for i in range(len(valid_symbols))
            }

            # Enforce exact 1.0 total weight display tuning if needed
            total_w = sum(weights_dict.values())
            if total_w > 0:
                weights_dict = {k: round(v / total_w, 4) for k, v in weights_dict.items()}

            pareto_portfolios.append(
                {
                    "portfolio_id": idx + 1,
                    "weights": weights_dict,
                    "metrics": {
                        "expected_return": round(exp_ret, 6),
                        "volatility": round(volatility, 6),
                        "liquidity_score": round(liquidity, 6),
                        "sharpe_ratio": round(sharpe, 4),
                    },
                }
            )

        # Sort portfolios by Sharpe Ratio descending for client convenience
        pareto_portfolios.sort(key=lambda p: p["metrics"]["sharpe_ratio"], reverse=True)

        return {
            "status": "success",
            "algorithm": "NSGA-II",
            "population_size": pop_size,
            "generations": generations,
            "symbols": valid_symbols,
            "num_solutions": len(pareto_portfolios),
            "pareto_portfolios": pareto_portfolios,
        }
