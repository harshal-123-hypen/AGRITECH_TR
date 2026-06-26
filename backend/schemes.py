from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import aiohttp
import logging

from database import get_db
from models import GovernmentScheme
from schema import GovernmentSchemeResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/maharashtra", response_model=list[GovernmentSchemeResponse])
async def get_maharashtra_schemes(db: Session = Depends(get_db)):
    try:
        url = (
            "https://data.gov.in/api/datastore/sql?"
            "sql=SELECT%20*%20FROM%20%22e4e42d84-dc02-4a48-84d6-7e8c0e7db9ed%22"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    records = data.get("records", [])

                    if records:
                        schemes = []

                        for record in records:
                            try:
                                scheme_name = record.get("scheme_name", "Unknown Scheme")

                                existing_scheme = (
                                    db.query(GovernmentScheme)
                                    .filter(GovernmentScheme.name == scheme_name)
                                    .first()
                                )

                                if existing_scheme:
                                    schemes.append(existing_scheme)
                                    continue

                                scheme = GovernmentScheme(
                                    name=scheme_name,
                                    description=record.get("description", ""),
                                    ministry=record.get("ministry", "Ministry of Agriculture"),
                                    eligibility=record.get("eligibility", "All farmers"),
                                    benefits=record.get("benefits", "Financial support"),
                                    application_link=record.get("application_url"),
                                    last_updated=datetime.utcnow()
                                )

                                db.add(scheme)
                                db.flush()
                                schemes.append(scheme)

                            except Exception as e:
                                logger.warning(f"Error processing scheme record: {str(e)}")

                        db.commit()
                        return schemes

        cached_schemes = db.query(GovernmentScheme).all()
        if cached_schemes:
            return cached_schemes

        raise HTTPException(status_code=503, detail="Schemes API unavailable and no cached data found")

    except aiohttp.ClientError as e:
        logger.warning(f"Schemes API connection error: {str(e)}")
        cached_schemes = db.query(GovernmentScheme).all()
        if cached_schemes:
            return cached_schemes
        raise HTTPException(status_code=503, detail="Schemes API unavailable")

    except Exception as e:
        logger.error(f"Error fetching schemes: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch schemes")


@router.get("/popular")
async def get_popular_schemes():
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
        "total": len(subsidies),
        "updated_at": datetime.utcnow().isoformat()
    }