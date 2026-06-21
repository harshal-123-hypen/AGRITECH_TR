from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from config import get_settings
from database import engine, Base
from api import weather, market, news, schemes, disease, predictions, users

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

app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(weather.router, prefix="/api/v1/weather", tags=["Weather"])
app.include_router(market.router, prefix="/api/v1/market", tags=["Market Data"])
app.include_router(news.router, prefix="/api/v1/news", tags=["News"])
app.include_router(schemes.router, prefix="/api/v1/schemes", tags=["Schemes"])
app.include_router(disease.router, prefix="/api/v1/disease", tags=["Disease Detection"])
app.include_router(predictions.router, prefix="/api/v1/predictions", tags=["Predictions"])

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
