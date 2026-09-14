from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.schemas.common import NotImplementedResponse

router = APIRouter()


@router.post(
    "",
    response_model=NotImplementedResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Create Investor Profile (Placeholder)",
    description="Creates a new investor profile. Scheduled for Stage 5.",
)
def create_profile():
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "detail": "Investor profile creation is not implemented in the foundation phase (~15%).",
            "status_code": 501,
            "stage_scheduled": "Stage 4: Database Integration & Stage 5: Backend Services",
            "endpoint": "/api/v1/profiles",
        },
    )


@router.get(
    "/{profile_id}",
    response_model=NotImplementedResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Get Investor Profile (Placeholder)",
)
def get_profile(profile_id: str):
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "detail": f"Retrieving investor profile '{profile_id}' is not implemented in the foundation phase.",
            "status_code": 501,
            "stage_scheduled": "Stage 5: Backend Services",
            "endpoint": f"/api/v1/profiles/{profile_id}",
        },
    )


@router.put(
    "/{profile_id}",
    response_model=NotImplementedResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Update Investor Profile (Placeholder)",
)
def update_profile(profile_id: str):
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "detail": f"Updating investor profile '{profile_id}' is not implemented in the foundation phase.",
            "status_code": 501,
            "stage_scheduled": "Stage 5: Backend Services",
            "endpoint": f"/api/v1/profiles/{profile_id}",
        },
    )
