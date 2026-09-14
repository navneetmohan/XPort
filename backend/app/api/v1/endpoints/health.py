import redis
from fastapi import APIRouter, status
from app.core.config import settings
from app.db.session import check_db_connection
from app.schemas.common import HealthCheckResponse

router = APIRouter()


def check_redis_connection() -> bool:
    """Helper to check Redis reachability."""
    try:
        r = redis.Redis.from_url(settings.REDIS_URL, socket_timeout=1.0)
        return bool(r.ping())
    except Exception:
        return False


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Health Check",
    description="Returns overall application health, database connectivity, and Redis broker availability.",
)
def get_health() -> HealthCheckResponse:
    db_ok = check_db_connection()
    redis_ok = check_redis_connection()

    db_status = "connected" if db_ok else "unreachable"
    redis_status = "connected" if redis_ok else "unreachable"

    # In foundation stage, the service is operational even if external DB/Redis are not yet spun up
    return HealthCheckResponse(
        status="ok",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database=db_status,
        redis=redis_status,
    )
