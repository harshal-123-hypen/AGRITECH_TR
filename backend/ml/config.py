from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # APIs
    openweathermap_api_key: str
    news_api_key: str
    gnews_api_key: str
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Server
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # External APIs
    agmarknet_api_base: str = "https://agmarknet.gov.in/api"
    datagov_api_base: str = "https://data.gov.in/api"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()
