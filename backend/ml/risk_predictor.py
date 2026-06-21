import numpy as np
import logging

logger = logging.getLogger(__name__)

class RiskPredictor:
    def __init__(self):
        self.risk_thresholds = {
            "rainfall_low": 300,
            "rainfall_high": 1000,
            "temperature_low": 15,
            "temperature_high": 35,
            "humidity_high": 85
        }
        
        self.pest_risk_by_crop = {
            "Cotton": {"thrips": 0.3, "bollworm": 0.4, "whitefly": 0.3},
            "Soybean": {"leaf_hopper": 0.25, "pod_borer": 0.35, "spider_mite": 0.2},
            "Sugarcane": {"top_borer": 0.3, "stem_borer": 0.4, "scale": 0.2},
            "Onion": {"thrips": 0.5, "purple_blotch": 0.3, "downy_mildew": 0.2},
            "Tomato": {"whitefly": 0.35, "early_blight": 0.3, "late_blight": 0.25},
            "Wheat": {"armyworm": 0.25, "blast": 0.2, "septoria": 0.3},
            "Rice": {"blast": 0.4, "brown_spot": 0.3, "gall_midge": 0.25},
            "Grapes": {"powdery_mildew": 0.4, "downy_mildew": 0.3, "anthracnose": 0.25},
            "Pomegranate": {"leaf_blotch": 0.3, "fruit_rot": 0.4, "butterfly_bore": 0.2},
            "Tur": {"pod_borer": 0.4, "leaf_roll": 0.2, "sterility_mosaic": 0.25},
            "Chana": {"pod_borer": 0.35, "ascochyta_blight": 0.3, "root_rot": 0.2}
        }
    
    def predict_risk(self, crop: str, rainfall: float, temperature: float, 
                    humidity: float, market_volatility: float) -> dict:
        """
        Predict risk using weather and market factors.
        """
        
        rainfall_risk = 0.0
        if rainfall < self.risk_thresholds["rainfall_low"]:
            rainfall_risk = (self.risk_thresholds["rainfall_low"] - rainfall) / 300
        elif rainfall > self.risk_thresholds["rainfall_high"]:
            rainfall_risk = (rainfall - self.risk_thresholds["rainfall_high"]) / 500
        
        temp_risk = 0.0
        if temperature < self.risk_thresholds["temperature_low"]:
            temp_risk = (self.risk_thresholds["temperature_low"] - temperature) / 20
        elif temperature > self.risk_thresholds["temperature_high"]:
            temp_risk = (temperature - self.risk_thresholds["temperature_high"]) / 15
        
        humidity_risk = 0.0
        if humidity > self.risk_thresholds["humidity_high"]:
            humidity_risk = (humidity - self.risk_thresholds["humidity_high"]) / 15
        
        pest_risk_dict = self.pest_risk_by_crop.get(crop, {})
        base_pest_risk = sum(pest_risk_dict.values()) / len(pest_risk_dict) if pest_risk_dict else 0.3
        pest_risk = base_pest_risk * (1 + humidity_risk) * (1 + temp_risk)
        
        market_risk = market_volatility * 0.5
        
        rainfall_risk = min(rainfall_risk, 1.0)
        temp_risk = min(temp_risk, 1.0)
        humidity_risk = min(humidity_risk, 1.0)
        pest_risk = min(pest_risk, 1.0)
        market_risk = min(market_risk, 1.0)
        
        overall_risk = (rainfall_risk * 0.25 + temp_risk * 0.2 + 
                       humidity_risk * 0.15 + pest_risk * 0.3 + market_risk * 0.1)
        
        if overall_risk < 0.3:
            risk_level = "low"
        elif overall_risk < 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        recommendations = self._get_risk_recommendations(
            crop, risk_level, rainfall_risk, pest_risk, market_risk
        )
        
        return {
            "crop": crop,
            "overall_risk_score": float(overall_risk),
            "risk_level": risk_level,
            "rainfall_risk": float(rainfall_risk),
            "temperature_risk": float(temp_risk),
            "humidity_risk": float(humidity_risk),
            "pest_risk": float(pest_risk),
            "market_risk": float(market_risk),
            "recommendations": recommendations,
            "confidence": 0.85
        }
    
    def _get_risk_recommendations(self, crop: str, risk_level: str, 
                                 rainfall_risk: float, pest_risk: float, 
                                 market_risk: float) -> list:
        """Generate recommendations based on identified risks"""
        recommendations = []
        
        if rainfall_risk > 0.5:
            recommendations.append("Install drip/micro irrigation system to manage water")
        if pest_risk > 0.5:
            recommendations.append("Increase monitoring for pest infestation")
            recommendations.append("Prepare integrated pest management plan")
        if market_risk > 0.5:
            recommendations.append("Consider crop insurance to manage price volatility")
            recommendations.append("Explore contract farming opportunities")
        
        if risk_level == "high":
            recommendations.append("URGENT: Consult with agricultural extension officer")
            recommendations.append("Consider diversifying crops")
        
        if risk_level == "low":
            recommendations.append("Maintain current practices")
            recommendations.append("Continue regular monitoring")
        
        return recommendations if recommendations else ["Continue regular farm monitoring"]
