from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    preferred_district = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    favorites = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")

class UserFavorite(Base):
    __tablename__ = "user_favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    crop = Column(String(100))
    district = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="favorites")

class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    district = Column(String(100), index=True)
    market_name = Column(String(255))
    crop = Column(String(100), index=True)
    today_price = Column(Float)
    min_price = Column(Float)
    max_price = Column(Float)
    modal_price = Column(Float)
    arrival = Column(Integer, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class WeatherData(Base):
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    rainfall = Column(Float, nullable=True)
    condition = Column(String(100))
    icon = Column(String(20))
    last_updated = Column(DateTime, default=datetime.utcnow)

class NewsArticle(Base):
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500))
    description = Column(Text)
    image_url = Column(String(500), nullable=True)
    source = Column(String(200))
    publish_date = Column(DateTime)
    url = Column(String(500))
    category = Column(String(100), nullable=True)
    cached_at = Column(DateTime, default=datetime.utcnow)

class GovernmentScheme(Base):
    __tablename__ = "government_schemes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    ministry = Column(String(200))
    eligibility = Column(Text)
    benefits = Column(Text)
    application_link = Column(String(500), nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)

class PredictionType(str, enum.Enum):
    profit = "profit"
    risk = "risk"
    disease = "disease"

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    prediction_type = Column(SQLEnum(PredictionType))
    crop = Column(String(100))
    district = Column(String(100))
    input_data = Column(Text)
    result = Column(Text)
    confidence = Column(Float, nullable=True)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", back_populates="predictions")

class SoilData(Base):
    __tablename__ = "soil_data"
    
    id = Column(Integer, primary_key=True, index=True)
    district = Column(String(100), index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    nitrogen = Column(Float)
    phosphorus = Column(Float)
    potassium = Column(Float)
    ph = Column(Float)
    organic_matter = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)
