from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import aiohttp
import logging
from database import get_db
from models import WeatherData
from ml.schemas import WeatherResponse
from ml.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

MAHARASHTRA_DISTRICTS = {
    "Pune": (18.5204, 73.8567),
    "Nashik": (19.9975, 73.7898),
    "Nagpur": (21.1458, 79.0882),
    "Kolhapur": (16.7050, 73.7421),
    "Sangli": (16.8500, 73.9167),
    "Satara": (17.6773, 73.9868),
    "Solapur": (17.6726, 75.9064),
    "Ahilyanagar": (19.1136, 73.7997),
    "Chhatrapati Sambhajinagar": (19.8762, 75.3433),
    "Jalgaon": (20.9747, 75.5625),
    "Amravati": (20.8530, 77.7421),
    "Wardha": (20.7485, 78.5831),
    "Yavatmal": (20.4281, 77.7064),
    "Akola": (20.7136, 77.0076),
    "Buldhana": (20.5313, 76.1881),
    "Latur": (18.4088, 76.2296),
    "Nanded": (19.1658, 77.3269),
    "Parbhani": (19.2686, 76.7741),
    "Osmanabad": (18.1673, 76.0401),
    "Dhule": (21.1978, 74.7746),
    "Nandurbar": (21.3811, 74.2453),
}

@router.get("/current/{district}", response_model=WeatherResponse)
async def get_current_weather(district: str, db: Session = Depends(get_db)):
    """
    Get current weather for a Maharashtra district.
    Fetches real-time data from OpenWeatherMap API.
    """
    if district not in MAHARASHTRA_DISTRICTS:
        raise HTTPException(status_code=404, detail=f"District {district} not found")
    
    lat, lon = MAHARASHTRA_DISTRICTS[district]
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={settings.openweathermap_api_key}&units=metric"
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=503, detail="Weather API unavailable")
                
                data = await resp.json()
                
                weather = WeatherData(
                    latitude=lat,
                    longitude=lon,
                    temperature=data["main"]["temp"],
                    humidity=data["main"]["humidity"],
                    wind_speed=data["wind"]["speed"],
                    rainfall=data.get("rain", {}).get("1h", 0.0),
                    condition=data["weather"][0]["main"],
                    icon=data["weather"][0]["icon"],
                    last_updated=datetime.utcnow()
                )
                
                db.add(weather)
                db.commit()
                db.refresh(weather)
                
                return weather
    except Exception as e:
        logger.error(f"Error fetching weather for {district}: {str(e)}")
        raise HTTPException(status_code=503, detail="Failed to fetch weather data")

@router.get("/forecast/{district}")
async def get_weather_forecast(district: str, days: int = 5):
    """
    Get weather forecast for Maharashtra district.
    Real-time data from OpenWeatherMap API.
    """
    if district not in MAHARASHTRA_DISTRICTS:
        raise HTTPException(status_code=404, detail=f"District {district} not found")
    
    lat, lon = MAHARASHTRA_DISTRICTS[district]
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={settings.openweathermap_api_key}&units=metric"
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=503, detail="Weather API unavailable")
                
                data = await resp.json()
                
                forecast = []
                for item in data["list"][:8*days]:
                    forecast.append({
                        "datetime": item["dt_txt"],
                        "temperature": item["main"]["temp"],
                        "humidity": item["main"]["humidity"],
                        "rainfall": item.get("rain", {}).get("3h", 0.0),
                        "condition": item["weather"][0]["main"],
                        "wind_speed": item["wind"]["speed"]
                    })
                
                return {
                    "district": district,
                    "forecast": forecast,
                    "updated_at": datetime.utcnow().isoformat()
                }
    except Exception as e:
        logger.error(f"Error fetching forecast for {district}: {str(e)}")
        raise HTTPException(status_code=503, detail="Failed to fetch forecast data")

@router.post("/cache-all")
async def cache_all_weather(db: Session = Depends(get_db)):
    """Cache weather data for all Maharashtra districts"""
    cached_count = 0
    errors = []
    
    for district in MAHARASHTRA_DISTRICTS.keys():
        try:
            await get_current_weather(district, db)
            cached_count += 1
        except Exception as e:
            errors.append({"district": district, "error": str(e)})
    
    return {
        "cached_count": cached_count,
        "total_districts": len(MAHARASHTRA_DISTRICTS),
        "errors": errors
    }
