from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
import os

from database import Base, engine
from disease import router as disease_router
from schemes import router as schemes_router
from schema import ProfitPredictionRequest, ProfitPredictionResponse

# =========================================================
# FastAPI App
# =========================================================
app = FastAPI(title="Maharashtra Agriculture API")

# =========================================================
# Create Database Tables
# =========================================================
Base.metadata.create_all(bind=engine)

# =========================================================
# CORS Configuration
# =========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # development साठी
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# Load Profit Prediction Model
# =========================================================
MODEL_PATH = "profit_model.pkl"
model = None

if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
        print("Profit model loaded successfully")
    except Exception as e:
        print(f"Error loading profit model: {e}")
        model = None
else:
    print("profit_model.pkl not found - using fallback profit calculation")

# =========================================================
# Include Routers
# =========================================================
app.include_router(disease_router, prefix="/api/disease", tags=["Disease"])
app.include_router(schemes_router, prefix="/api/schemes", tags=["Schemes"])

# =========================================================
# Home Route
# =========================================================
@app.get("/")
def home():
    return {"message": "Agriculture ML API is running!"}

# =========================================================
# Fallback Profit Formula
# =========================================================
def calculate_fallback_profit(crop, district, rainfall, temperature, area, market_price):
    """
    Simple temporary profit estimation formula when ML model is not available.
    """

    crop_yield_map = {
        "soybean": 12,
        "cotton": 18,
        "sugarcane": 350,
        "onion": 120,
        "tomato": 180,
        "wheat": 22,
        "rice": 28,
        "grapes": 100,
        "pomegranate": 80,
        "tur": 10,
        "chana": 14
    }

    crop_cost_map = {
        "soybean": 18000,
        "cotton": 30000,
        "sugarcane": 85000,
        "onion": 55000,
        "tomato": 65000,
        "wheat": 22000,
        "rice": 28000,
        "grapes": 120000,
        "pomegranate": 100000,
        "tur": 20000,
        "chana": 18000
    }

    crop_key = crop.strip().lower()

    # base yield per hectare
    base_yield = crop_yield_map.get(crop_key, 20)

    # cost per hectare
    base_cost = crop_cost_map.get(crop_key, 25000)

    # rainfall factor
    rainfall_factor = 1.0
    if rainfall < 500:
        rainfall_factor = 0.75
    elif rainfall < 700:
        rainfall_factor = 0.9
    elif rainfall <= 1200:
        rainfall_factor = 1.05
    else:
        rainfall_factor = 0.95

    # temperature factor
    temp_factor = 1.0
    if temperature < 18:
        temp_factor = 0.85
    elif temperature <= 32:
        temp_factor = 1.05
    else:
        temp_factor = 0.9

    # final yield estimate
    expected_yield = base_yield * rainfall_factor * temp_factor * area

    # gross revenue
    revenue = expected_yield * market_price

    # total cost
    total_cost = base_cost * area

    # final profit
    profit = revenue - total_cost

    return round(profit, 2)

# =========================================================
# Profit Prediction Route
# =========================================================
@app.post("/api/predict", response_model=ProfitPredictionResponse)
def predict_profit(data: ProfitPredictionRequest):
    try:
        # If model exists, use ML prediction
        if model is not None:
            prediction = model.predict([[
                data.crop,
                data.district,
                data.rainfall,
                data.temperature,
                data.area,
                data.market_price
            ]])

            return {"profit": float(prediction[0])}

        # Otherwise use fallback formula
        fallback_profit = calculate_fallback_profit(
            crop=data.crop,
            district=data.district,
            rainfall=data.rainfall,
            temperature=data.temperature,
            area=data.area,
            market_price=data.market_price
        )

        return {"profit": fallback_profit}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")