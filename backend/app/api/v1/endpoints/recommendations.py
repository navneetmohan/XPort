from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.schemas.common import NotImplementedResponse

router = APIRouter()


@router.post(
    "",
    response_model=NotImplementedResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Submit Portfolio Recommendation Request (Placeholder)",
    description="Submits an NSGA-II optimization task. Scheduled for full implementation in Stage 7.",
)
def submit_recommendation():
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "detail": "Portfolio recommendation generation is not implemented in the foundation phase (~15%).",
            "status_code": 501,
            "stage_scheduled": "Stage 7: NSGA-II Optimization",
            "endpoint": "/api/v1/recommendations",
        },
    )


@router.get(
    "/{task_id}",
    response_model=NotImplementedResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Get Recommendation Task Status/Result (Placeholder)",
)
def get_recommendation_status(task_id: str):
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "detail": f"Retrieving recommendation task '{task_id}' is not implemented in the foundation phase.",
            "status_code": 501,
            "stage_scheduled": "Stage 5: Backend Services & Stage 7: NSGA-II",
            "endpoint": f"/api/v1/recommendations/{task_id}",
        },
    )


@router.get(
    "/{recommendation_id}/explanation",
    response_model=NotImplementedResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Get SHAP & Rule-Based Explanation (Placeholder)",
)
def get_recommendation_explanation(recommendation_id: str):
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "detail": f"SHAP explanation for recommendation '{recommendation_id}' is not implemented in the foundation phase.",
            "status_code": 501,
            "stage_scheduled": "Stage 8: SHAP Explainability",
            "endpoint": f"/api/v1/recommendations/{recommendation_id}/explanation",
        },
    )


@router.get(
    "/{recommendation_id}/backtest",
    response_model=NotImplementedResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Get Historical Backtest (Placeholder)",
)
def get_recommendation_backtest(recommendation_id: str):
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "detail": f"Historical backtest for recommendation '{recommendation_id}' is not implemented in the foundation phase.",
            "status_code": 501,
            "stage_scheduled": "Stage 9: Backtesting & What-if Simulation",
            "endpoint": f"/api/v1/recommendations/{recommendation_id}/backtest",
        },
    )
