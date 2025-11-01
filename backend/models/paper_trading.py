"""
Pydantic models for Paper Trading positions.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class PositionType(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class PositionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class CreatePositionRequest(BaseModel):
    asset_class: str
    asset_symbol: str
    position_type: PositionType
    entry_price: float = Field(..., gt=0)
    quantity: float = Field(..., gt=0)
    leverage: float = Field(default=1.0, ge=1.0, le=100.0)
    notes: Optional[str] = None


class UpdatePositionRequest(BaseModel):
    quantity: Optional[float] = Field(None, gt=0)
    leverage: Optional[float] = Field(None, ge=1.0, le=100.0)
    notes: Optional[str] = None


class ClosePositionRequest(BaseModel):
    exit_price: float = Field(..., gt=0)
    notes: Optional[str] = None


class Position(BaseModel):
    id: int
    asset_class: str
    asset_symbol: str
    position_type: str
    entry_price: float
    quantity: float
    leverage: float
    entry_time: datetime
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PositionWithPnL(Position):
    current_price: Optional[float] = None
    pnl: float
    pnl_percent: float
    pnl_with_leverage: float
    pnl_with_leverage_percent: float


class PortfolioStats(BaseModel):
    total_positions: int
    open_positions: int
    closed_positions: int
    total_pnl: float
    total_pnl_percent: float
    win_rate: float
    largest_win: float
    largest_loss: float
    avg_win: float
    avg_loss: float
