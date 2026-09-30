from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class RecommendationRequest(BaseModel):
    """Payload for submitting an NSGA-II portfolio optimization job."""

    symbols: Optional[List[str]] = Field(
        default=None,
        description="Target asset universe for portfolio optimization. Uses standard Indian equities/ETFs if omitted.",
        json_schema_extra={"example": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]},
    )
    pop_size: Optional[int] = Field(
        default=50,
        description="NSGA-II population size.",
        ge=10,
        le=500,
    )
    generations: Optional[int] = Field(
        default=50,
        description="NSGA-II number of generations.",
        ge=10,
        le=500,
    )


class PortfolioMetrics(BaseModel):
    expected_return: float
    volatility: float
    liquidity_score: float
    sharpe_ratio: float


class ParetoPortfolioItem(BaseModel):
    portfolio_id: int
    weights: Dict[str, float]
    metrics: PortfolioMetrics


class RecommendationResponse(BaseModel):
    """Asynchronous response when submitting a portfolio recommendation job."""

    task_id: str
    recommendation_id: str
    status: str = "PENDING"
    message: str = "NSGA-II optimization task dispatched to background worker"
    symbols: List[str]


class RecommendationStatusResponse(BaseModel):
    """Response when querying recommendation task status or result."""

    recommendation_id: str
    task_id: Optional[str] = None
    status: str
    result_data: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)
