from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging
import json

from database import get_db
from models import Prediction, PredictionType
from schema import (
    DiseaseDetectionRequest,
    DiseaseDetectionResponse,
    DiseaseDetectionDetailedResponse,
    PredictionHistoryResponse
)
from ml.disease_detector import DiseaseDetector

router = APIRouter()
logger = logging.getLogger(__name__)
detector = DiseaseDetector()


# =========================================================
# Simple Disease Detection
# =========================================================
@router.post("/detect", response_model=DiseaseDetectionResponse)
async def detect_disease(
    request: DiseaseDetectionRequest,
    db: Session = Depends(get_db)
):
    """
    Detect crop disease from image using ML model.
    Accepts base64 encoded image.
    """
    try:
        prediction = detector.predict(request.image_base64)

        return {
            "disease": prediction.get("disease", "Unknown"),
            "confidence": prediction.get("confidence", 0.0),
            "treatment": prediction.get("treatment", "No treatment available"),
            "severity": prediction.get("severity", "Unknown")
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Error detecting disease: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to detect disease")


# =========================================================
# Detailed Disease Detection + Save to DB
# =========================================================
@router.post("/detect-detailed", response_model=DiseaseDetectionDetailedResponse)
async def detect_disease_detailed(
    request: DiseaseDetectionRequest,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Get detailed disease detection with optional DB save.
    """
    try:
        prediction = detector.predict(request.image_base64)

        # Default recommendations
        recommendations = [
            "Remove infected leaves from the crop.",
            "Spray recommended fungicide/pesticide as per disease.",
            "Avoid overwatering and monitor field regularly."
        ]

        # Save prediction only if user_id provided
        if user_id:
            try:
                db_prediction = Prediction(
                    user_id=user_id,
                    prediction_type=PredictionType.disease,
                    crop=request.crop,
                    district=request.district,
                    input_data=json.dumps({
                        "image_size": len(request.image_base64)
                    }),
                    result=json.dumps(prediction),
                    confidence=prediction.get("confidence", 0.0)
                )
                db.add(db_prediction)
                db.commit()
            except Exception as db_error:
                db.rollback()
                logger.error(f"DB save failed: {str(db_error)}")

        return {
            "disease": prediction.get("disease", "Unknown"),
            "confidence": prediction.get("confidence", 0.0),
            "treatment": prediction.get("treatment", "No treatment available"),
            "severity": prediction.get("severity", "Unknown"),
            "recommendations": recommendations
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Error in detailed disease detection: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze image")


# =========================================================
# Disease Analysis History
# =========================================================
@router.get("/analysis-history/{user_id}", response_model=PredictionHistoryResponse)
async def get_disease_analysis_history(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get last 10 disease detection analyses for a user.
    """
    try:
        predictions = (
            db.query(Prediction)
            .filter(
                Prediction.user_id == user_id,
                Prediction.prediction_type == PredictionType.disease
            )
            .order_by(Prediction.created_at.desc())
            .limit(10)
            .all()
        )

        analyses = []
        for p in predictions:
            try:
                parsed_result = json.loads(p.result) if p.result else {}
            except Exception:
                parsed_result = {}

            analyses.append({
                "id": p.id,
                "crop": p.crop,
                "district": p.district,
                "result": parsed_result,
                "confidence": p.confidence,
                "analyzed_at": p.created_at.isoformat() if p.created_at else ""
            })

        return {
            "user_id": user_id,
            "total_analyses": len(analyses),
            "analyses": analyses
        }

    except Exception as e:
        logger.error(f"Error fetching disease analysis history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch analysis history")