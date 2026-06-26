from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
import sys
import os

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.config import get_settings
from ml.database import engine, Base
from weather import router as weather_router
from market import router as market_router
from news import router as news_router
from schemes import router as schemes_router
from disease import router as disease_router
from prediction import router as predictions_router
from user import router as user_router

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Maharashtra Agriculture API",
    description="Real-time agriculture data for Maharashtra farmers",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Maharashtra Agriculture API"
    }

@app.get("/api/v1")
async def api_root():
    return {
        "message": "Maharashtra Agriculture API v1.0",
        "endpoints": {
            "health": "/health",
            "weather": "/api/v1/weather",
            "market": "/api/v1/market",
            "news": "/api/v1/news",
            "schemes": "/api/v1/schemes",
            "disease": "/api/v1/disease",
            "predictions": "/api/v1/predictions",
            "users": "/api/v1/users",
            "docs": "/api/docs"
        }
    }

app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(weather_router, prefix="/api/v1/weather", tags=["Weather"])
app.include_router(market_router, prefix="/api/v1/market", tags=["Market Data"])
app.include_router(news_router, prefix="/api/v1/news", tags=["News"])
app.include_router(schemes_router, prefix="/api/v1/schemes", tags=["Schemes"])
app.include_router(disease_router, prefix="/api/v1/disease", tags=["Disease Detection"])
app.include_router(predictions_router, prefix="/api/v1/predictions", tags=["Predictions"])

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc) if settings.debug else "Internal error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
