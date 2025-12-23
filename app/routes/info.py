# app/routes/info.py
from fastapi import APIRouter, status
from datetime import datetime

from app.models.schemas import HealthResponse
from app.config import settings

router = APIRouter(tags=["Information"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if the API is running"
)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        timestamp=datetime.now().isoformat()
    )
