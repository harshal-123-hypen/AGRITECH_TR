from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from datetime import datetime
from database import Base


# =========================================================
# Government Schemes Table
# =========================================================
class GovernmentScheme(Base):
    __tablename__ = "government_schemes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    ministry = Column(String(255), default="")
    eligibility = Column(Text, default="")
    benefits = Column(Text, default="")
    application_link = Column(String(500), nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)


# =========================================================
# Prediction History Table
# =========================================================
class PredictionType:
    disease = "disease"
    profit = "profit"


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    prediction_type = Column(String(50), nullable=False)
    crop = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    input_data = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)