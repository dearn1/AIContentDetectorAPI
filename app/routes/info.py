# app/routes/info.py
from fastapi import APIRouter, status
from datetime import datetime

from app.models.schemas import HealthResponse, PricingResponse, PricingTier
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


@router.get(
    "/pricing",
    response_model=PricingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get pricing information",
    description="Retrieve pricing tiers and features"
)
async def get_pricing():
    """Return pricing information"""
    pricing = {
        'free': PricingTier(
            requests_per_month=1000,
            price=0,
            features=[
                'Basic detection',
                'Single text analysis',
                'Email support'
            ]
        ),
        'starter': PricingTier(
            requests_per_month=10000,
            price=29.99,
            features=[
                'Advanced detection',
                'Batch analysis (up to 10)',
                'Priority email support',
                'API access'
            ]
        ),
        'professional': PricingTier(
            requests_per_month=100000,
            price=99.99,
            features=[
                'All features',
                'Batch analysis (up to 50)',
                'Priority support',
                'Custom models',
                'Webhooks',
                'Detailed analytics'
            ]
        ),
        'enterprise': PricingTier(
            requests_per_month='Unlimited',
            price='Custom',
            features=[
                'Everything in Professional',
                'Unlimited requests',
                'Dedicated infrastructure',
                '24/7 support',
                'SLA guarantee',
                'Custom integrations',
                'Training sessions'
            ]
        )
    }

    return PricingResponse(
        status="success",
        pricing_tiers=pricing
    )
