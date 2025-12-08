# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.config import settings
from app.routes import detection, info

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI Content Detection API - Detect AI-generated text with high accuracy",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(detection.router, prefix=settings.API_PREFIX)
app.include_router(info.router, prefix=settings.API_PREFIX)

@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation"""
    return RedirectResponse(url="/docs")

@app.get(f"{settings.API_PREFIX}/")
async def api_root():
    """API root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "documentation": "/docs",
        "endpoints": {
            "detect": f"{settings.API_PREFIX}/detect",
            "batch_detect": f"{settings.API_PREFIX}/detect/batch",
            "health": f"{settings.API_PREFIX}/health",
            "pricing": f"{settings.API_PREFIX}/pricing"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
