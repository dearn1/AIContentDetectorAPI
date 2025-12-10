# app/routes/detection.py
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
import hashlib

from app.models.schemas import (
    TextAnalysisRequest,
    TextAnalysisResponse,
    BatchAnalysisRequest,
    BatchAnalysisResponse,
    ErrorResponse
)
from app.utils.detector import AIContentDetector
from app.security.api_auth import validate_api_key, rate_limit

router = APIRouter(prefix="/detect", tags=["Detection"], dependencies=[Depends(validate_api_key)])

# Initialize detector
detector = AIContentDetector()


@router.post(
    "",
    response_model=TextAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect AI-generated content",
    description="Analyze a single text to determine if it's AI-generated"
)
async def detect_ai_content(request: TextAnalysisRequest):
    """
    Detect if text is AI-generated

    - **text**: The text to analyze (minimum 50 characters)
    - **api_key**: Your API key for authentication

    Returns detailed analysis including:
    - AI probability score (0-100)
    - Confidence level
    - Detailed metrics
    """
    try:
        # Validate API key (simplified - in production use proper auth)
        if not request.api_key or len(request.api_key) < 10:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )

        # Analyze text
        result = detector.analyze_text(request.text)

        # Generate request ID for tracking
        request_id = hashlib.md5(
            f"{request.text[:50]}{datetime.now().isoformat()}".encode()
        ).hexdigest()

        return TextAnalysisResponse(
            status="success",
            request_id=request_id,
            timestamp=datetime.now().isoformat(),
            analysis=result,
            text_length=len(request.text),
            word_count=len(request.text.split())
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post(
    "/batch",
    response_model=BatchAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Batch detect AI content",
    description="Analyze multiple texts at once (max 10)"
)
async def batch_detect(request: BatchAnalysisRequest):
    """
    Batch detection for multiple texts

    - **texts**: Array of texts to analyze (max 10)
    - **api_key**: Your API key for authentication

    Returns analysis results for each text
    """
    try:
        # Validate API key
        if not request.api_key or len(request.api_key) < 10:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )

        # Validate batch size
        if len(request.texts) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 texts per batch request"
            )

        results = []
        for idx, text in enumerate(request.texts):
            if len(text) >= 50:
                analysis = detector.analyze_text(text)
                results.append({
                    'index': idx,
                    'text_length': len(text),
                    'word_count': len(text.split()),
                    'analysis': analysis
                })
            else:
                results.append({
                    'index': idx,
                    'error': 'Text too short (minimum 50 characters)'
                })

        return BatchAnalysisResponse(
            status="success",
            timestamp=datetime.now().isoformat(),
            total_analyzed=len(results),
            results=results
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch analysis failed: {str(e)}"
        )
