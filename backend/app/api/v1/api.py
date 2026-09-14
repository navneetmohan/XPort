from fastapi import APIRouter
from app.api.v1.endpoints import health, market_data, recommendations, profiles, whatif

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(
    market_data.router, prefix="/market-data", tags=["Market Data Acquisition"]
)
api_router.include_router(
    recommendations.router, prefix="/recommendations", tags=["Recommendations"]
)
api_router.include_router(profiles.router, prefix="/profiles", tags=["Profiles"])
api_router.include_router(whatif.router, prefix="/whatif", tags=["What-if Simulation"])
