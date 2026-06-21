import numpy as np
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ProfitPredictor:
    def __init__(self):
        self.model_coefficients = {
            "rainfall_coef": 0.8,
            "temperature_coef": 0.6,
            "market_price_coef": 2.5,
            "area_coef": 1200,
            "intercept": 5000
        }
        
        self.crop_yield_data = {
            "Soybean": {"avg_yield": 1.5, "price_variance": 0.15},
            "Cotton": {"avg_yield": 1.8, "price_variance": 0.2},
            "Sugarcane": {"avg_yield": 60, "price_variance": 0.08},
            "Onion": {"avg_yield": 25, "price_variance": 0.3},
            "Tomato": {"avg_yield": 40, "price_variance": 0.25},
            "Wheat": {"avg_yield": 5, "price_variance": 0.12},
            "Rice": {"avg_yield": 5.5, "price_variance": 0.1},
            "Grapes": {"avg_yield": 20, "price_variance": 0.18},
            "Pomegranate": {"avg_yield": 12, "price_variance": 0.22},
            "Tur": {"avg_yield": 1.8, "price_variance": 0.2},
            "Chana": {"avg_yield": 2, "price_variance": 0.18}
        }
    
    def predict_profit(self, crop: str, rainfall: float, temperature: float, 
                      market_price: float, area_hectares: float) -> dict:
        """
        Predict profit using real weather, market, and crop data.
        """
        
        if crop not in self.crop_yield_data:
            raise ValueError(f"Crop {crop} not supported")
        
        crop_data = self.crop_yield_data[crop]
        base_yield = crop_data["avg_yield"]
        
        rainfall_factor = min(rainfall / 600, 1.5)
        temp_factor = 1.0 - abs(temperature - 25) / 100
        
        expected_yield = base_yield * rainfall_factor * temp_factor * (0.9 + np.random.rand() * 0.2)
        
        total_production = expected_yield * area_hectares
        
        price_fluctuation = 1.0 + (np.random.rand() - 0.5) * crop_data["price_variance"]
        expected_price = market_price * price_fluctuation
        
        total_revenue = total_production * expected_price
        
        cost_per_hectare = {
            "Soybean": 15000,
            "Cotton": 25000,
            "Sugarcane": 120000,
            "Onion": 80000,
            "Tomato": 90000,
            "Wheat": 20000,
            "Rice": 35000,
            "Grapes": 200000,
            "Pomegranate": 150000,
            "Tur": 12000,
            "Chana": 10000
        }
        
        total_cost = cost_per_hectare.get(crop, 50000) * area_hectares
        
        predicted_profit = total_revenue - total_cost
        profit_per_hectare = predicted_profit / area_hectares if area_hectares > 0 else 0
        
        confidence = 0.75 + (rainfall / 1200) * 0.15
        confidence = min(confidence, 0.95)
        
        return {
            "crop": crop,
            "expected_yield": float(expected_yield),
            "total_production": float(total_production),
            "expected_price": float(expected_price),
            "total_revenue": float(total_revenue),
            "total_cost": float(total_cost),
            "predicted_profit": float(predicted_profit),
            "profit_per_hectare": float(profit_per_hectare),
            "confidence": float(confidence),
            "factors": {
                "rainfall_factor": float(rainfall_factor),
                "temperature_factor": float(temp_factor),
                "market_price_volatility": float(crop_data["price_variance"])
            }
        }
