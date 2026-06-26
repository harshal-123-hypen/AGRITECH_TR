from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
import aiohttp
import logging
from database import get_db
from models import MarketData
from ml.schemas import MarketDataResponse
from ml.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

PRIMARY_CROPS = [
    "Soybean", "Cotton", "Sugarcane", "Onion", "Tomato",
    "Wheat", "Rice", "Grapes", "Pomegranate", "Tur", "Chana"
]

@router.get("/prices/{district}/{crop}", response_model=list[MarketDataResponse])
async def get_market_prices(
    district: str,
    crop: str,
    db: Session = Depends(get_db)
):
    """
    Get real-time market prices from Agmarknet API.
    Fetches today's, min, max, and modal prices.
    """
    if crop not in PRIMARY_CROPS:
        raise HTTPException(status_code=400, detail=f"Crop {crop} not supported")
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.agmarknet.gov.in/web/crop_price?district={district}&commodity={crop}&latest=10"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    db_prices = db.query(MarketData).filter(
                        and_(MarketData.district == district, MarketData.crop == crop)
                    ).all()
                    if db_prices:
                        return db_prices
                    raise HTTPException(status_code=503, detail="Market API unavailable")
                
                data = await resp.json()
                
                if not data or not data.get("data"):
                    db_prices = db.query(MarketData).filter(
                        and_(MarketData.district == district, MarketData.crop == crop)
                    ).all()
                    if db_prices:
                        return db_prices
                    return []
                
                prices = []
                for record in data["data"][:10]:
                    market_data = MarketData(
                        district=district,
                        market_name=record.get("market", "Market"),
                        crop=crop,
                        today_price=float(record.get("price", 0)),
                        min_price=float(record.get("min_price", 0)),
                        max_price=float(record.get("max_price", 0)),
                        modal_price=float(record.get("modal_price", 0)),
                        arrival=int(record.get("arrival", 0)),
                        last_updated=datetime.utcnow()
                    )
                    db.add(market_data)
                    prices.append(market_data)
                
                db.commit()
                return prices
    except aiohttp.ClientError as e:
        logger.warning(f"Agmarknet API error: {str(e)}, returning cached data")
        db_prices = db.query(MarketData).filter(
            and_(MarketData.district == district, MarketData.crop == crop)
        ).order_by(MarketData.last_updated.desc()).all()
        return db_prices
    except Exception as e:
        logger.error(f"Error fetching market prices: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch market data")

@router.get("/all-prices/{district}")
async def get_all_crop_prices(district: str, db: Session = Depends(get_db)):
    """Get prices for all primary crops in a district"""
    all_prices = {}
    
    for crop in PRIMARY_CROPS:
        try:
            prices = await get_market_prices(district, crop, db)
            all_prices[crop] = [price.dict() for price in prices]
        except Exception as e:
            logger.warning(f"Error fetching {crop} prices: {str(e)}")
            all_prices[crop] = []
    
    return {
        "district": district,
        "crops": all_prices,
        "updated_at": datetime.utcnow().isoformat()
    }

@router.get("/trends/{district}/{crop}")
async def get_price_trends(
    district: str,
    crop: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get historical price trends for a crop"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    trends = db.query(MarketData).filter(
        and_(
            MarketData.district == district,
            MarketData.crop == crop,
            MarketData.last_updated >= cutoff_date
        )
    ).order_by(MarketData.last_updated.asc()).all()
    
    return {
        "district": district,
        "crop": crop,
        "days": days,
        "data_points": len(trends),
        "trends": [
            {
                "date": t.last_updated.isoformat(),
                "price": t.today_price,
                "min": t.min_price,
                "max": t.max_price,
                "modal": t.modal_price,
                "market": t.market_name
            } for t in trends
        ]
    }

@router.post("/cache-all")
async def cache_all_prices(db: Session = Depends(get_db)):
    """Cache market data for all districts and crops"""
    districts = ["Pune", "Nashik", "Nagpur", "Kolhapur", "Sangli"]
    cached_count = 0
    errors = []
    
    for district in districts:
        for crop in PRIMARY_CROPS:
            try:
                await get_market_prices(district, crop, db)
                cached_count += 1
            except Exception as e:
                errors.append({"district": district, "crop": crop, "error": str(e)})
    
    return {
        "cached_count": cached_count,
        "total_combinations": len(districts) * len(PRIMARY_CROPS),
        "errors": errors
    }
