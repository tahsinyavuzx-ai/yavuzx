"""
Configuration settings for ML Trading Dashboard.
Production-grade configuration with environment variable support.
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "ML Trading Dashboard"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    
    # Azure Storage
    AZURE_STORAGE_CONNECTION_STRING: str
    MODELS_CONTAINER: str = "trained-models"
    DATA_CONTAINER: str = "training-data"
    HISTORY_CONTAINER: str = "training-history"
    
    # Model Settings
    MODEL_CACHE_TTL: int = 3600  # Cache models for 1 hour
    PREDICTION_THRESHOLD: float = 0.5
    
    # Asset Classes
    SUPPORTED_ASSETS: List[str] = ["NASDAQ", "CRYPTO", "GOLD", "SILVER", "PALLADIUM"]
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Market Data APIs
    YFINANCE_ENABLED: bool = True
    CCXT_EXCHANGE: str = "binance"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
