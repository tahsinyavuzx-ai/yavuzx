"""
Paper Trading API endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging
from ..services.position_service import PositionService
from ..models.paper_trading import (
    CreatePositionRequest, UpdatePositionRequest, ClosePositionRequest,
    Position, PositionWithPnL, PortfolioStats
)
from ..database import init_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/trading", tags=["Paper Trading"])

init_db()


def get_position_service() -> PositionService:
    """Get position service instance."""
    if not hasattr(get_position_service, "instance"):
        get_position_service.instance = PositionService()
    return get_position_service.instance


@router.post("/positions", response_model=Position)
async def create_position(
    request: CreatePositionRequest,
    service: PositionService = Depends(get_position_service)
):
    """Create a new paper trading position."""
    try:
        position = service.create_position(
            asset_class=request.asset_class,
            asset_symbol=request.asset_symbol,
            position_type=request.position_type.value,
            entry_price=request.entry_price,
            quantity=request.quantity,
            leverage=request.leverage,
            notes=request.notes
        )
        return position
    except Exception as e:
        logger.error(f"Error creating position: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions", response_model=List[Position])
async def get_all_positions(
    status: str = None,
    service: PositionService = Depends(get_position_service)
):
    """Get all positions."""
    try:
        positions = service.get_all_positions(status=status)
        return positions
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions/{position_id}", response_model=Position)
async def get_position(
    position_id: int,
    service: PositionService = Depends(get_position_service)
):
    """Get a specific position."""
    try:
        position = service.get_position(position_id)
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        return position
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching position: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions/open/with-pnl", response_model=List[PositionWithPnL])
async def get_open_positions_with_pnl(
    service: PositionService = Depends(get_position_service)
):
    """Get all open positions with real-time P&L."""
    try:
        positions = service.get_positions_with_pnl()
        return positions
    except Exception as e:
        logger.error(f"Error fetching positions with P&L: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/positions/{position_id}", response_model=Position)
async def update_position(
    position_id: int,
    request: UpdatePositionRequest,
    service: PositionService = Depends(get_position_service)
):
    """Update a position."""
    try:
        position = service.update_position(
            position_id=position_id,
            quantity=request.quantity,
            leverage=request.leverage,
            notes=request.notes
        )
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        return position
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating position: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/positions/{position_id}/close", response_model=Position)
async def close_position(
    position_id: int,
    request: ClosePositionRequest,
    service: PositionService = Depends(get_position_service)
):
    """Close an open position."""
    try:
        position = service.close_position(
            position_id=position_id,
            exit_price=request.exit_price,
            notes=request.notes
        )
        if not position:
            raise HTTPException(status_code=404, detail="Position not found")
        return position
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error closing position: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/positions/{position_id}")
async def delete_position(
    position_id: int,
    service: PositionService = Depends(get_position_service)
):
    """Delete a position."""
    try:
        success = service.delete_position(position_id)
        if not success:
            raise HTTPException(status_code=404, detail="Position not found or already closed")
        return {"message": "Position deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting position: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio/stats", response_model=PortfolioStats)
async def get_portfolio_stats(
    service: PositionService = Depends(get_position_service)
):
    """Get portfolio statistics."""
    try:
        stats = service.get_portfolio_stats()
        return stats
    except Exception as e:
        logger.error(f"Error fetching portfolio stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
