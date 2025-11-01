"""
Signal generation API endpoints - supports any stock.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
import logging
from ..services.signal_service import SignalService
from ..models.schemas import PredictionResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/signals", tags=["Signals"])


def get_signal_service() -> SignalService:
    """Dependency: Get signal service instance."""
    if not hasattr(get_signal_service, "instance"):
        get_signal_service.instance = SignalService()
    return get_signal_service.instance


@router.get("/list")
async def list_available_assets(service: SignalService = Depends(get_signal_service)):
    """Get list of all available assets with trained models."""
    try:
        assets = service.model_manager.get_available_assets()
        return {
            "total": len(assets),
            "assets": assets
        }
    except Exception as e:
        logger.error(f"Error listing assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals/all", response_model=List[PredictionResponse])
async def get_all_signals(service: SignalService = Depends(get_signal_service)):
    """Generate signals for ALL available stocks."""
    try:
        signals = await service.generate_all_signals()
        return signals
    except Exception as e:
        logger.error(f"Error generating signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals/{symbol}", response_model=PredictionResponse)
async def get_signal_for_asset(
    symbol: str,
    service: SignalService = Depends(get_signal_service)
):
    """Get trading signal for a specific asset."""
    try:
        signal = await service.generate_signal(symbol)
        if not signal:
            raise HTTPException(status_code=404, detail=f"No signal available for {symbol}")
        return signal
    except Exception as e:
        logger.error(f"Error generating signal for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market/{symbol}")
async def get_market_data(
    symbol: str,
    period: str = "1mo",
    service: SignalService = Depends(get_signal_service)
):
    """Get historical market data for a symbol."""
    try:
        market_data = service.market_data.get_historical_data(symbol, period)
        if not market_data:
            raise HTTPException(status_code=404, detail=f"No market data available for {symbol}")
        return market_data
    except Exception as e:
        logger.error(f"Error fetching market data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    """Get signal for a specific stock symbol."""
    try:
        signal = await service.generate_signal(symbol.upper())
        if not signal:
            raise HTTPException(status_code=404, detail=f"No model found for {symbol}")
        return signal
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating signal for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/price/{symbol}")
async def get_current_price(
    symbol: str,
    service: SignalService = Depends(get_signal_service)
):
    """Get current price for any stock."""
    try:
        price = service.market_service.get_current_price(symbol.upper())
        if price is None:
            raise HTTPException(status_code=404, detail=f"Could not fetch price for {symbol}")
        return {
            "symbol": symbol.upper(),
            "price": price
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/market/{symbol}")
async def get_market_data(symbol: str):
    """Get historical market data for chart."""
    try:
        import yfinance as yf
        
        # Handle crypto symbols
        if symbol == 'BTC_USD':
            ticker = yf.Ticker('BTC-USD')
        elif symbol == 'ETH_USD':
            ticker = yf.Ticker('ETH-USD')
        else:
            ticker = yf.Ticker(symbol)
        
        hist = ticker.history(period="30d", interval="1d")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        data = []
        for timestamp, row in hist.iterrows():
            data.append({
                "timestamp": timestamp.isoformat(),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        return {
            "symbol": symbol,
            "data": data
        }
    except Exception as e:
        logger.error(f"Error fetching market data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/{symbol}")
async def get_market_data(symbol: str):
    """Get historical market data for chart."""
    try:
        from ..services.market_data_service import MarketDataService
        import yfinance as yf
        
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="30d", interval="1h")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        data = []
        for timestamp, row in hist.iterrows():
            data.append({
                "timestamp": timestamp.isoformat(),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        return {
            "symbol": symbol,
            "data": data
        }
    except Exception as e:
        logger.error(f"Error fetching market data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 