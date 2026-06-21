from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Prediction, PredictionType
from schemas import DiseaseDetectionRequest, DiseaseDetectionResponse
from ml.disease_detector import DiseaseDetector
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)
detector = DiseaseDetector()

@router.post("/detect", response_model=DiseaseDetectionResponse)
async def detect_disease(request: DiseaseDetectionRequest, db: Session = Depends(get_db)):
    """
    Detect crop disease from image using OpenCV and ML model.
    Accepts base64 encoded image.
    """
    try:
        prediction = detector.predict(request.image_base64)
        
        return {
            "disease": prediction["disease"],
            "confidence": prediction["confidence"],
            "treatment": prediction["treatment"],
            "severity": prediction["severity"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error detecting disease: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to detect disease")

@router.post("/detect-detailed")
async def detect_disease_detailed(
    request: DiseaseDetectionRequest,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Get detailed disease detection with recommendations.
    """
    try:
        prediction = detector.predict(request.image_base64)
        
        if user_id:
            db_prediction = Prediction(
                user_id=user_id,
                prediction_type=PredictionType.disease,
                crop=request.crop,
                district=request.district,
                input_data=json.dumps({"image_size": len(request.image_base64)}),
                result=json.dumps(prediction),
                confidence=prediction["confidence"]
            )
            db.add(db_prediction)
            db.commit()
        
        return prediction
    except Exception as e:
        logger.error(f"Error in detailed disease detection: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze image")

@router.get("/analysis-history/{user_id}")
async def get_disease_analysis_history(user_id: int, db: Session = Depends(get_db)):
    """Get past disease detection analyses for a user"""
    predictions = db.query(Prediction).filter(
        Prediction.user_id == user_id,
        Prediction.prediction_type == PredictionType.disease
    ).order_by(Prediction.created_at.desc()).limit(10).all()
    
    return {
        "user_id": user_id,
        "total_analyses": len(predictions),
        "analyses": [
            {
                "id": p.id,
                "crop": p.crop,
                "district": p.district,
                "result": json.loads(p.result),
                "confidence": p.confidence,
                "analyzed_at": p.created_at.isoformat()
            } for p in predictions
        ]
    }
