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
else:
    print("profit_model.pkl not found")

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
# Profit Prediction Route
# =========================================================
@app.post("/api/predict", response_model=ProfitPredictionResponse)
def predict_profit(data: ProfitPredictionRequest):
    try:
        if model is None:
            raise HTTPException(status_code=500, detail="Profit model not loaded")

        prediction = model.predict([[
            data.crop,
            data.district,
            data.rainfall,
            data.temperature,
            data.area,
            data.market_price
        ]])

        return {"profit": float(prediction[0])}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")