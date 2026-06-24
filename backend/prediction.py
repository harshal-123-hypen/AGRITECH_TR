from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Prediction, PredictionType
from ml.schemas import (
    ProfitPredictionRequest, ProfitPredictionResponse,
    RiskPredictionRequest, RiskPredictionResponse
)
from ml.profit_predictor import ProfitPredictor
from ml.risk_predictor import RiskPredictor
from weather import get_current_weather
from market import get_market_prices
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)
profit_predictor = ProfitPredictor()
risk_predictor = RiskPredictor()

@router.post("/profit", response_model=ProfitPredictionResponse)
async def predict_profit(
    request: ProfitPredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Predict profit using real weather, market, and crop data.
    Uses current weather and market prices from APIs.
    """
    try:
        weather = await get_current_weather(request.district, db)
        market_prices = await get_market_prices(request.district, request.crop, db)
        
        if not market_prices:
            raise HTTPException(status_code=404, detail="Market data not available")
        
        market_price = market_prices[0].today_price if market_prices else 0
        
        prediction = profit_predictor.predict_profit(
            crop=request.crop,
            rainfall=500,
            temperature=weather.temperature,
            market_price=market_price,
            area_hectares=request.area_hectares
        )
        
        return {
            "predicted_profit": prediction["predicted_profit"],
            "expected_yield": prediction["expected_yield"],
            "market_price_forecast": prediction["expected_price"],
            "confidence": prediction["confidence"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting profit: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to predict profit")

@router.post("/profit-detailed")
async def predict_profit_detailed(
    request: ProfitPredictionRequest,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """Get detailed profit prediction with all factors"""
    try:
        weather = await get_current_weather(request.district, db)
        market_prices = await get_market_prices(request.district, request.crop, db)
        
        market_price = market_prices[0].today_price if market_prices else 0
        
        prediction = profit_predictor.predict_profit(
            crop=request.crop,
            rainfall=500,
            temperature=weather.temperature,
            market_price=market_price,
            area_hectares=request.area_hectares
        )
        
        if user_id:
            db_prediction = Prediction(
                user_id=user_id,
                prediction_type=PredictionType.profit,
                crop=request.crop,
                district=request.district,
                input_data=json.dumps({
                    "area_hectares": request.area_hectares,
                    "temperature": weather.temperature,
                    "market_price": market_price
                }),
                result=json.dumps(prediction),
                confidence=prediction["confidence"]
            )
            db.add(db_prediction)
            db.commit()
        
        return prediction
    except Exception as e:
        logger.error(f"Error in detailed profit prediction: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to predict profit")

@router.post("/risk", response_model=RiskPredictionResponse)
async def predict_risk(
    request: RiskPredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Predict risk using weather and market factors.
    Real-time data from APIs.
    """
    try:
        weather = await get_current_weather(request.district, db)
        market_prices = await get_market_prices(request.district, request.crop, db)
        
        market_volatility = 0.15
        if len(market_prices) > 1:
            avg_price = sum(p.today_price for p in market_prices[:5]) / min(len(market_prices), 5)
            volatility = sum(abs(p.today_price - avg_price) for p in market_prices[:5]) / (avg_price * min(len(market_prices), 5))
            market_volatility = volatility
        
        prediction = risk_predictor.predict_risk(
            crop=request.crop,
            rainfall=500,
            temperature=weather.temperature,
            humidity=weather.humidity,
            market_volatility=market_volatility
        )
        
        return {
            "risk_level": prediction["risk_level"],
            "risk_score": prediction["overall_risk_score"],
            "rainfall_risk": prediction["rainfall_risk"],
            "pest_risk": prediction["pest_risk"],
            "market_risk": prediction["market_risk"],
            "recommendations": prediction["recommendations"]
        }
    except Exception as e:
        logger.error(f"Error predicting risk: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to predict risk")

@router.post("/risk-detailed")
async def predict_risk_detailed(
    request: RiskPredictionRequest,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """Get detailed risk prediction"""
    try:
        weather = await get_current_weather(request.district, db)
        market_prices = await get_market_prices(request.district, request.crop, db)
        
        market_volatility = 0.15
        if len(market_prices) > 1:
            avg_price = sum(p.today_price for p in market_prices[:5]) / min(len(market_prices), 5)
            volatility = sum(abs(p.today_price - avg_price) for p in market_prices[:5]) / (avg_price * min(len(market_prices), 5))
            market_volatility = volatility
        
        prediction = risk_predictor.predict_risk(
            crop=request.crop,
            rainfall=500,
            temperature=weather.temperature,
            humidity=weather.humidity,
            market_volatility=market_volatility
        )
        
        if user_id:
            db_prediction = Prediction(
                user_id=user_id,
                prediction_type=PredictionType.risk,
                crop=request.crop,
                district=request.district,
                input_data=json.dumps({
                    "temperature": weather.temperature,
                    "humidity": weather.humidity,
                    "market_volatility": market_volatility
                }),
                result=json.dumps(prediction),
                confidence=prediction["confidence"]
            )
            db.add(db_prediction)
            db.commit()
        
        return prediction
    except Exception as e:
        logger.error(f"Error in detailed risk prediction: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to predict risk")

@router.get("/history/{user_id}")
async def get_prediction_history(user_id: int, db: Session = Depends(get_db)):
    """Get prediction history for a user"""
    predictions = db.query(Prediction).filter(
        Prediction.user_id == user_id
    ).order_by(Prediction.created_at.desc()).limit(20).all()
    
    return {
        "user_id": user_id,
        "total_predictions": len(predictions),
        "predictions": [
            {
                "id": p.id,
                "type": p.prediction_type.value,
                "crop": p.crop,
                "district": p.district,
                "confidence": p.confidence,
                "created_at": p.created_at.isoformat()
            } for p in predictions
        ]
    }
