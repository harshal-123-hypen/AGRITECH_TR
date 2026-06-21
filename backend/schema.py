from pydantic import BaseModel
from typing import Optional, List, Dict, Any


# =========================================================
# Disease Detection Schemas
# =========================================================

class DiseaseDetectionRequest(BaseModel):
    image_base64: str
    crop: Optional[str] = None
    district: Optional[str] = None


class DiseaseDetectionResponse(BaseModel):
    disease: str
    confidence: float
    treatment: str
    severity: str


class DiseaseDetectionDetailedResponse(BaseModel):
    disease: str
    confidence: float
    treatment: str
    severity: str
    recommendations: Optional[List[str]] = None


# =========================================================
# Government Schemes Schemas
# =========================================================

class GovernmentSchemeResponse(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    ministry: str
    eligibility: str
    benefits: str
    application_link: Optional[str] = None

    class Config:
        from_attributes = True   # जर error आला तर orm_mode = True कर


class PopularSchemeItem(BaseModel):
    name: str
    description: str
    ministry: str
    eligibility: str
    benefits: str
    application_link: str
    coverage: str


class PopularSchemesResponse(BaseModel):
    schemes: List[PopularSchemeItem]
    total: int
    fetched_at: str


class SubsidySchemeItem(BaseModel):
    crop: str
    subsidy_type: str
    amount: str
    ministry: str
    application_process: str


class SubsidySchemesResponse(BaseModel):
    subsidies: List[SubsidySchemeItem]
    total: int
    updated_at: str


# =========================================================
# Profit Prediction Schemas
# =========================================================

class ProfitPredictionRequest(BaseModel):
    crop: str
    district: str
    rainfall: float
    temperature: float
    area: float
    market_price: float


class ProfitPredictionResponse(BaseModel):
    profit: float


# =========================================================
# Prediction History / Generic Prediction Schemas
# =========================================================

class PredictionHistoryItem(BaseModel):
    id: int
    crop: Optional[str] = None
    district: Optional[str] = None
    result: Dict[str, Any]
    confidence: Optional[float] = None
    analyzed_at: str


class PredictionHistoryResponse(BaseModel):
    user_id: int
    total_analyses: int
    analyses: List[PredictionHistoryItem]