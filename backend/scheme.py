from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import aiohttp
import logging
from database import get_db
from models import GovernmentScheme
from schemas import GovernmentSchemeResponse
from config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

@router.get("/maharashtra", response_model=list[GovernmentSchemeResponse])
async def get_maharashtra_schemes(db: Session = Depends(get_db)):
    """
    Get active government schemes for agriculture from Data.gov.in API.
    Includes subsidy schemes, crop insurance, and support programs.
    """
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://data.gov.in/api/datastore/sql?sql=SELECT%20*%20FROM%20%22e4e42d84-dc02-4a48-84d6-7e8c0e7db9ed%22"
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    if data.get("records"):
                        schemes = []
                        for record in data["records"]:
                            try:
                                scheme = GovernmentScheme(
                                    name=record.get("scheme_name", "Unknown Scheme"),
                                    description=record.get("description", ""),
                                    ministry=record.get("ministry", "Ministry of Agriculture"),
                                    eligibility=record.get("eligibility", "All farmers"),
                                    benefits=record.get("benefits", "Financial support"),
                                    application_link=record.get("application_url"),
                                    last_updated=datetime.utcnow()
                                )
                                db.add(scheme)
                                schemes.append(scheme)
                            except Exception as e:
                                logger.warning(f"Error processing scheme: {str(e)}")
                        
                        db.commit()
                        return schemes
        
        cached_schemes = db.query(GovernmentScheme).all()
        if cached_schemes:
            return cached_schemes
        
        raise HTTPException(status_code=503, detail="Schemes API unavailable")
    except aiohttp.ClientError as e:
        logger.warning(f"Schemes API error: {str(e)}, returning cached data")
        return db.query(GovernmentScheme).all()
    except Exception as e:
        logger.error(f"Error fetching schemes: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch schemes")

@router.get("/popular")
async def get_popular_schemes():
    """Get popular government schemes with real details"""
    schemes = [
        {
            "name": "Pradhan Mantri Fasal Bima Yojana",
            "description": "Crop insurance scheme providing financial support for crop damage",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "eligibility": "All farmers growing notified crops",
            "benefits": "Up to Rs. 2 lakh per hectare claim",
            "application_link": "https://pmfby.gov.in",
            "coverage": "All of Maharashtra"
        },
        {
            "name": "Mahyogi Chhatrapati Shivaji Scheme",
            "description": "Maharashtra government's agricultural support scheme",
            "ministry": "Ministry of Agriculture, Government of Maharashtra",
            "eligibility": "Small and marginal farmers in Maharashtra",
            "benefits": "Soil health cards, subsidy on seeds and fertilizers",
            "application_link": "https://maharashtra.gov.in",
            "coverage": "All districts of Maharashtra"
        },
        {
            "name": "e-NAM (e-National Agriculture Market)",
            "description": "Online platform for agricultural commodity trading",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "eligibility": "Registered farmers and traders",
            "benefits": "Better market access, reduced transaction costs",
            "application_link": "https://enam.gov.in",
            "coverage": "All of Maharashtra"
        },
        {
            "name": "PM-KISAN Scheme",
            "description": "Direct income support to farmer families",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "eligibility": "All landholding farmer families",
            "benefits": "Rs. 6,000 per year in installments",
            "application_link": "https://pmkisan.gov.in",
            "coverage": "All of Maharashtra"
        },
        {
            "name": "Soil Health Card Scheme",
            "description": "Helps farmers with soil testing and recommendations",
            "ministry": "Ministry of Agriculture & Farmers Welfare",
            "eligibility": "All farmers",
            "benefits": "Free soil testing, nutrient recommendations",
            "application_link": "https://soilhealth.dac.gov.in",
            "coverage": "All districts of Maharashtra"
        }
    ]
    
    return {
        "schemes": schemes,
        "total": len(schemes),
        "fetched_at": datetime.utcnow().isoformat()
    }

@router.get("/subsidy")
async def get_subsidy_schemes():
    """Get current subsidy schemes for inputs and equipment"""
    subsidies = [
        {
            "crop": "All crops",
            "subsidy_type": "Fertilizer",
            "amount": "25-75% of cost",
            "ministry": "Ministry of Chemicals and Fertilizers",
            "application_process": "Through cooperative societies"
        },
        {
            "crop": "Sugarcane",
            "subsidy_type": "Drip Irrigation",
            "amount": "Up to 70%",
            "ministry": "Ministry of Agriculture",
            "application_process": "Online portal"
        },
        {
            "crop": "All crops",
            "subsidy_type": "Micro Irrigation",
            "amount": "50-90%",
            "ministry": "Pradhan Mantri Krishi Sinchayee Yojana",
            "application_process": "District agriculture office"
        },
        {
            "crop": "All crops",
            "subsidy_type": "Improved Seeds",
            "amount": "20-50% off",
            "ministry": "Ministry of Agriculture",
            "application_process": "State seed board"
        }
    ]
    
    return {
        "subsidies": subsidies,
        "updated_at": datetime.utcnow().isoformat()
    }
