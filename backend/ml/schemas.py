from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Any
import enum

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    latitude: Optional[float]
    longitude: Optional[float]
    preferred_district: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class MarketDataResponse(BaseModel):
    district: str
    market_name: str
    crop: str
    today_price: float
    min_price: float
    max_price: float
    modal_price: float
    arrival: Optional[int]
    last_updated: datetime
    
    class Config:
        from_attributes = True

class WeatherResponse(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float
    rainfall: Optional[float]
    condition: str
    icon: str
    last_updated: datetime
    
    class Config:
        from_attributes = True

class NewsArticleResponse(BaseModel):
    id: int
    title: str
    description: str
    image_url: Optional[str]
    source: str
    publish_date: datetime
    url: str
    category: Optional[str]
    
    class Config:
        from_attributes = True

class GovernmentSchemeResponse(BaseModel):
    id: int
    name: str
    description: str
    ministry: str
    eligibility: str
    benefits: str
    application_link: Optional[str]
    last_updated: datetime
    
    class Config:
        from_attributes = True

class PredictionResponse(BaseModel):
    id: int
    prediction_type: str
    crop: str
    district: str
    result: str
    confidence: Optional[float]
    image_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class DiseaseDetectionRequest(BaseModel):
    image_base64: str
    crop: str
    district: str

class DiseaseDetectionResponse(BaseModel):
    disease: str
    confidence: float
    treatment: str
    severity: str

class ProfitPredictionRequest(BaseModel):
    crop: str
    district: str
    area_hectares: float

class ProfitPredictionResponse(BaseModel):
    predicted_profit: float
    expected_yield: float
    market_price_forecast: float
    confidence: float

class RiskPredictionRequest(BaseModel):
    crop: str
    district: str

class RiskPredictionResponse(BaseModel):
    risk_level: str
    risk_score: float
    rainfall_risk: float
    pest_risk: float
    market_risk: float
    recommendations: List[str]

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class UserFavoriteRequest(BaseModel):
    crop: str
    district: str

class UserFavoriteResponse(BaseModel):
    id: int
    crop: str
    district: str
    created_at: datetime
    
    class Config:
        from_attributes = True
