from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.schemas.common import NotImplementedResponse

router = APIRouter()


@router.post(
    "",
    response_model=NotImplementedResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Submit What-if Scenario Request (Placeholder)",
    description="Submits a re-optimization scenario. Scheduled for Stage 9.",
)
def submit_whatif_scenario():
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "detail": "What-if scenario simulation is not implemented in the foundation phase (~15%).",
            "status_code": 501,
            "stage_scheduled": "Stage 9: Backtesting, Pareto & What-if",
            "endpoint": "/api/v1/whatif",
        },
    )


@router.get(
    "/{task_id}",
    response_model=NotImplementedResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Get What-if Scenario Task Result (Placeholder)",
)
def get_whatif_status(task_id: str):
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "detail": f"Retrieving What-if scenario task '{task_id}' is not implemented in the foundation phase.",
            "status_code": 501,
            "stage_scheduled": "Stage 9: Backtesting, Pareto & What-if",
            "endpoint": f"/api/v1/whatif/{task_id}",
        },
    )
