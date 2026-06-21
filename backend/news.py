from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import aiohttp
import logging
from database import get_db
from models import NewsArticle
from schemas import NewsArticleResponse
from config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

@router.get("/agriculture", response_model=list[NewsArticleResponse])
async def get_agriculture_news(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get latest agriculture news from NewsAPI.
    Real-time articles about farming and agriculture.
    """
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://newsapi.org/v2/everything?q=agriculture+farming+crop&language=en&sortBy=publishedAt&pageSize=50"
            headers = {"X-Api-Key": settings.news_api_key}
            
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    cached_news = db.query(NewsArticle).order_by(
                        NewsArticle.publish_date.desc()
                    ).limit(limit).all()
                    if cached_news:
                        return cached_news
                    raise HTTPException(status_code=503, detail="News API unavailable")
                
                data = await resp.json()
                
                if not data.get("articles"):
                    return db.query(NewsArticle).order_by(
                        NewsArticle.publish_date.desc()
                    ).limit(limit).all()
                
                articles = []
                for article in data["articles"][:limit]:
                    try:
                        news = NewsArticle(
                            title=article["title"],
                            description=article.get("description", ""),
                            image_url=article.get("urlToImage"),
                            source=article["source"]["name"],
                            publish_date=datetime.fromisoformat(article["publishedAt"].replace("Z", "+00:00")),
                            url=article["url"],
                            category="Agriculture",
                            cached_at=datetime.utcnow()
                        )
                        db.add(news)
                        articles.append(news)
                    except Exception as e:
                        logger.warning(f"Error processing article: {str(e)}")
                
                db.commit()
                return articles
    except aiohttp.ClientError as e:
        logger.warning(f"NewsAPI error: {str(e)}, returning cached data")
        return db.query(NewsArticle).order_by(
            NewsArticle.publish_date.desc()
        ).limit(limit).all()
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch news")

@router.get("/maharashtra")
async def get_maharashtra_agriculture_news(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get agriculture news specific to Maharashtra"""
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://newsapi.org/v2/everything?q=Maharashtra+agriculture+farming&language=en&sortBy=publishedAt&pageSize=50"
            headers = {"X-Api-Key": settings.news_api_key}
            
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    cached_news = db.query(NewsArticle).filter(
                        NewsArticle.category == "Maharashtra"
                    ).order_by(NewsArticle.publish_date.desc()).limit(limit).all()
                    if cached_news:
                        return cached_news
                    raise HTTPException(status_code=503, detail="News API unavailable")
                
                data = await resp.json()
                
                if not data.get("articles"):
                    return db.query(NewsArticle).filter(
                        NewsArticle.category == "Maharashtra"
                    ).order_by(NewsArticle.publish_date.desc()).limit(limit).all()
                
                articles = []
                for article in data["articles"][:limit]:
                    try:
                        news = NewsArticle(
                            title=article["title"],
                            description=article.get("description", ""),
                            image_url=article.get("urlToImage"),
                            source=article["source"]["name"],
                            publish_date=datetime.fromisoformat(article["publishedAt"].replace("Z", "+00:00")),
                            url=article["url"],
                            category="Maharashtra",
                            cached_at=datetime.utcnow()
                        )
                        db.add(news)
                        articles.append(news)
                    except Exception as e:
                        logger.warning(f"Error processing article: {str(e)}")
                
                db.commit()
                return articles
    except aiohttp.ClientError as e:
        logger.warning(f"NewsAPI error: {str(e)}, returning cached data")
        return db.query(NewsArticle).filter(
            NewsArticle.category == "Maharashtra"
        ).order_by(NewsArticle.publish_date.desc()).limit(limit).all()
    except Exception as e:
        logger.error(f"Error fetching Maharashtra news: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch news")

@router.get("/trending")
async def get_trending_news(limit: int = 15):
    """Get trending agriculture news from GNews API"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://gnews.io/api/v4/search?q=agriculture+farming&lang=en&max=50&apikey={settings.gnews_api_key}"
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=503, detail="GNews API unavailable")
                
                data = await resp.json()
                
                articles = []
                for article in data.get("articles", [])[:limit]:
                    articles.append({
                        "title": article["title"],
                        "description": article.get("description", ""),
                        "image": article.get("image", ""),
                        "source": article["source"]["name"],
                        "publish_date": article["publishedAt"],
                        "url": article["url"]
                    })
                
                return {
                    "articles": articles,
                    "total": len(articles),
                    "fetched_at": datetime.utcnow().isoformat()
                }
    except Exception as e:
        logger.error(f"Error fetching trending news: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch trending news")
