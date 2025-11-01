"""
Pydantic schemas for request/response validation.
Type-safe data models for the API.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AssetClass(str, Enum):
    """Supported asset classes."""
    NASDAQ = "NASDAQ"
    CRYPTO = "CRYPTO"
    GOLD = "GOLD"
    SILVER = "SILVER"
    PALLADIUM = "PALLADIUM"


class SignalType(str, Enum):
    """Trading signal types."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class TechnicalIndicators(BaseModel):
    """Technical indicators for an asset."""
    rsi: float = Field(..., ge=0, le=100, description="Relative Strength Index")
    macd: float = Field(..., description="MACD value")
    macd_signal: float = Field(..., description="MACD signal line")
    bb_upper: float = Field(..., description="Bollinger Band upper")
    bb_middle: float = Field(..., description="Bollinger Band middle")
    bb_lower: float = Field(..., description="Bollinger Band lower")
    volume_ratio: float = Field(..., ge=0, description="Volume ratio")
    volatility: float = Field(..., ge=0, description="Price volatility")
    momentum: float = Field(..., description="Price momentum")


class PredictionRequest(BaseModel):
    """Request for price prediction."""
    asset_class: AssetClass
    indicators: Optional[TechnicalIndicators] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "asset_class": "NASDAQ",
                "indicators": {
                    "rsi": 65.5,
                    "macd": 0.025,
                    "macd_signal": 0.020,
                    "bb_upper": 15500,
                    "bb_middle": 15000,
                    "bb_lower": 14500,
                    "volume_ratio": 1.2,
                    "volatility": 0.018,
                    "momentum": 0.015
                }
            }
        }


class PredictionResponse(BaseModel):
    """Prediction response."""
    asset_symbol: str  # Changed from asset_class
    signal: SignalType
    confidence: float
    current_price: Optional[float] = None
    predicted_direction: str
    model_version: str
    timestamp: datetime
    indicators: TechnicalIndicators

class BatchPredictionRequest(BaseModel):
    """Request for multiple asset predictions."""
    assets: List[AssetClass] = Field(..., min_length=1, max_length=10)


class BatchPredictionResponse(BaseModel):
    """Response with multiple predictions."""
    predictions: List[PredictionResponse]
    timestamp: datetime


class ModelInfo(BaseModel):
    """Model metadata."""
    asset_symbol: str  # Changed from asset_class
    version: str
    loaded: bool
    last_updated: str


class MarketData(BaseModel):
    """Current market data for an asset."""
    asset_class: AssetClass
    price: float
    change_24h: float
    change_percent_24h: float
    volume_24h: float
    high_24h: float
    low_24h: float
    timestamp: datetime


class SignalResponse(BaseModel):
    """Trading signal with full context."""
    asset_class: AssetClass
    signal: SignalType
    confidence: float
    price: float
    indicators: TechnicalIndicators
    reasons: List[str]  # Human-readable reasons for signal
    timestamp: datetime


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    models_loaded: int
    local_connected: bool  # Changed from azure_connected
    version: str
