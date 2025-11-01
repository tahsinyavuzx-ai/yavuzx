"""
Prediction endpoints.
ML model inference API.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
import logging
from ..models.schemas import (
    PredictionRequest, PredictionResponse, BatchPredictionRequest,
    BatchPredictionResponse, AssetClass, ModelInfo
)
from ..models.model_loader import ModelManager
from ..services.prediction_service import PredictionService
from ..services.market_data_service import MarketDataService
from ..utils.indicators import TechnicalIndicatorCalculator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


def get_model_manager() -> ModelManager:
    """Dependency: Get model manager instance."""
    if not hasattr(get_model_manager, "instance"):
        get_model_manager.instance = ModelManager()
    return get_model_manager.instance


def get_prediction_service(model_manager: ModelManager = Depends(get_model_manager)) -> PredictionService:
    """Dependency: Get prediction service instance."""
    return PredictionService(model_manager)


def get_market_data_service() -> MarketDataService:
    """Dependency: Get market data service instance."""
    if not hasattr(get_market_data_service, "instance"):
        get_market_data_service.instance = MarketDataService()
    return get_market_data_service.instance


@router.post("/predict", response_model=PredictionResponse)
async def predict_asset(
    request: PredictionRequest,
    prediction_service: PredictionService = Depends(get_prediction_service),
    market_service: MarketDataService = Depends(get_market_data_service)
):
    """
    Generate prediction for a single asset.
    
    Args:
        request: Prediction request with asset class and optional indicators
        
    Returns:
        Prediction response with signal and confidence
    """
    try:
        # If indicators not provided, calculate from live data
        if request.indicators is None:
            df = market_service.get_historical_data(request.asset_class, period="3mo", interval="1d")
            
            if df is None or df.empty:
                raise HTTPException(status_code=503, detail="Unable to fetch market data")
            
            indicators_dict = TechnicalIndicatorCalculator.calculate_all_indicators(
                prices=df['close'],
                volumes=df.get('volume')
            )
            
            from ..models.schemas import TechnicalIndicators
            indicators = TechnicalIndicators(**indicators_dict)
        else:
            indicators = request.indicators
        
        # Get current price
        current_price = market_service.get_current_price(request.asset_class)
        
        # Generate prediction
        prediction = prediction_service.predict(
            asset_class=request.asset_class,
            indicators=indicators,
            current_price=current_price
        )
        
        if prediction is None:
            raise HTTPException(status_code=500, detail="Prediction failed")
        
        return prediction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in predict endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(
    request: BatchPredictionRequest,
    prediction_service: PredictionService = Depends(get_prediction_service),
    market_service: MarketDataService = Depends(get_market_data_service)
):
    """
    Generate predictions for multiple assets.
    
    Args:
        request: Batch prediction request with list of asset classes
        
    Returns:
        Batch prediction response with all predictions
    """
    try:
        predictions = []
        
        for asset_class in request.assets:
            try:
                # Get historical data
                df = market_service.get_historical_data(asset_class, period="3mo", interval="1d")
                
                if df is None or df.empty:
                    logger.warning(f"No data available for {asset_class}")
                    continue
                
                # Calculate indicators
                indicators_dict = TechnicalIndicatorCalculator.calculate_all_indicators(
                    prices=df['close'],
                    volumes=df.get('volume')
                )
                
                from ..models.schemas import TechnicalIndicators
                indicators = TechnicalIndicators(**indicators_dict)
                
                # Get current price
                current_price = market_service.get_current_price(asset_class)
                
                # Generate prediction
                prediction = prediction_service.predict(
                    asset_class=asset_class,
                    indicators=indicators,
                    current_price=current_price
                )
                
                if prediction:
                    predictions.append(prediction)
                    
            except Exception as e:
                logger.error(f"Error predicting {asset_class}: {e}")
                continue
        
        return BatchPredictionResponse(
            predictions=predictions,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error in batch predict endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


def get_model_manager() -> ModelManager:
    if not hasattr(get_model_manager, "instance"):
        get_model_manager.instance = ModelManager()
    return get_model_manager.instance


@router.get("/models/{symbol}")
async def get_model_info(
    symbol: str,
    model_manager: ModelManager = Depends(get_model_manager)
):
    """Get model info for a stock."""
    try:
        info = model_manager.get_model_info(symbol)
        if not info:
            raise HTTPException(status_code=404, detail=f"No model found for {symbol}")
        return info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching model info for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{asset_class}", response_model=ModelInfo)
async def get_model_info(
    asset_class: AssetClass,
    model_manager: ModelManager = Depends(get_model_manager)
):
    """
    Get information about a specific model.
    
    Args:
        asset_class: Asset class to get model info for
        
    Returns:
        Model information
    """
    model_info = model_manager.get_model_info(asset_class)
    
    if model_info is None:
        raise HTTPException(status_code=404, detail=f"Model not found for {asset_class.value}")
    
    return model_info
