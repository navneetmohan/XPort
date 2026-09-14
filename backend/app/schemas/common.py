from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Schema for application health check endpoint."""
    status: str = Field(default="ok", description="Overall health status")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp",
    )
    version: str = Field(default="0.1.0", description="API Version")
    environment: str = Field(default="development", description="Runtime environment")
    database: str = Field(default="unknown", description="Database connectivity status")
    redis: str = Field(default="unknown", description="Redis connectivity status")


class NotImplementedResponse(BaseModel):
    """Schema returned by foundation stage placeholder endpoints."""
    detail: str = Field(..., description="Explanation of why this endpoint is not implemented yet")
    status_code: int = Field(default=501, description="HTTP Status Code")
    stage_scheduled: str = Field(..., description="SDD implementation stage where this feature will be built")
    endpoint: str = Field(..., description="Called endpoint path")
