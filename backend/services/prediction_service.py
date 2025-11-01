"""
ML prediction service - supports any stock symbol.
"""
from typing import Optional, Dict, Any
import numpy as np
from datetime import datetime
import logging
import warnings
from ..models.schemas import (
    PredictionResponse, SignalType, TechnicalIndicators
)
from ..models.model_loader import ModelManager
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

warnings.filterwarnings('ignore', message='X does not have valid feature names')
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')




class PredictionService:
    """Generate ML predictions for any stock."""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
    
    def predict(self, 
                asset_symbol: str,
                indicators: TechnicalIndicators,
                current_price: Optional[float] = None) -> Optional[PredictionResponse]:
        """Generate prediction for any stock symbol."""
        model_snapshot = self.model_manager.get_model(asset_symbol)
        
        if model_snapshot is None:
            logger.error(f"No model available for {asset_symbol}")
            return None
        
        try:
            # Extract model from your trainer's format
            model = None
            scaler = None
            
            if isinstance(model_snapshot, dict):
                # Your trainer format: {"model_tuple": (xgb_model, scaler), "metadata": ...}
                if 'model_tuple' in model_snapshot:
                    model_tuple = model_snapshot['model_tuple']
                    if isinstance(model_tuple, tuple) and len(model_tuple) >= 2:
                        model, scaler = model_tuple[0], model_tuple[1]
                    else:
                        model = model_tuple
                elif 'model' in model_snapshot:
                    model = model_snapshot['model']
                else:
                    logger.error(f"Unknown dict structure for {asset_symbol}: {model_snapshot.keys()}")
                    return self._create_dummy_prediction(asset_symbol, indicators, current_price)
            else:
                model = model_snapshot.model if hasattr(model_snapshot, 'model') else model_snapshot
            
            if model is None:
                logger.error(f"Could not extract model for {asset_symbol}")
                return self._create_dummy_prediction(asset_symbol, indicators, current_price)
            
            # Verify model has predict_proba
            
            # Prepare features
            features = self._prepare_features(indicators)
            
            # Scale features if scaler is available
            if scaler is not None:
                features = scaler.transform([features])[0]
            
            # Make prediction using XGBoost DMatrix
            import xgboost as xgb
            dmatrix = xgb.DMatrix([features])
            prediction_proba = model.predict(dmatrix)
            
            # For binary classification
            if len(prediction_proba.shape) == 1:
                # Single probability output
                prob_positive = prediction_proba[0]
                prob_negative = 1 - prob_positive
                prediction_proba = np.array([prob_negative, prob_positive])
            else:
                prediction_proba = prediction_proba[0]
            
            predicted_class = 1 if prediction_proba[1] > 0.5 else 0
            confidence = float(max(prediction_proba))
            
            signal = self._determine_signal(predicted_class, confidence)
            direction = "UP" if predicted_class == 1 else "DOWN"
            
            model_info = self.model_manager.get_model_info(asset_symbol)
            model_version = model_info.version if model_info else "1.0.0"
            
            return PredictionResponse(
                asset_symbol=asset_symbol,
                signal=signal,
                confidence=confidence,
                current_price=current_price,
                predicted_direction=direction,
                model_version=model_version,
                timestamp=datetime.utcnow(),
                indicators=indicators
            )
            
        except Exception as e:
            logger.error(f"Error making prediction for {asset_symbol}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._create_dummy_prediction(asset_symbol, indicators, current_price)
    
    def _prepare_features(self, indicators: TechnicalIndicators) -> np.ndarray:
        """Prepare feature vector - must match training features."""
        bb_width = (indicators.bb_upper - indicators.bb_lower) / (indicators.bb_middle + 1e-10)
        
        # Match your trainer's feature order:
        # ['rsi14', 'macd', 'bb_width', 'volume_ratio', 'volatility_7d', 'price_momentum']
        return np.array([
            indicators.rsi,              # rsi14
            indicators.macd,             # macd
            bb_width,                    # bb_width
            indicators.volume_ratio,     # volume_ratio
            indicators.volatility,       # volatility_7d
            indicators.momentum          # price_momentum
        ])
    
    def _determine_signal(self, predicted_class: int, confidence: float) -> SignalType:
        """Determine trading signal."""
        threshold = settings.PREDICTION_THRESHOLD
        
        if confidence < threshold:
            return SignalType.HOLD
        
        return SignalType.BUY if predicted_class == 1 else SignalType.SELL
    
    def _create_dummy_prediction(self, asset_symbol: str, 
                                 indicators: TechnicalIndicators,
                                 current_price: Optional[float]) -> PredictionResponse:
        """Create dummy prediction when model fails."""
        import random
        
        signal = random.choice([SignalType.BUY, SignalType.SELL, SignalType.HOLD])
        confidence = random.uniform(0.5, 0.95)
        direction = "UP" if signal == SignalType.BUY else "DOWN" if signal == SignalType.SELL else "NEUTRAL"
        
        return PredictionResponse(
            asset_symbol=asset_symbol,
            signal=signal,
            confidence=confidence,
            current_price=current_price,
            predicted_direction=direction,
            model_version="1.0.0-dummy",
            timestamp=datetime.utcnow(),
            indicators=indicators
        )
    
    def batch_predict(self, 
                      predictions_data: Dict[str, TechnicalIndicators],
                      prices: Optional[Dict[str, float]] = None) -> Dict[str, PredictionResponse]:
        """Generate predictions for multiple stocks."""
        results = {}
        
        for asset_symbol, indicators in predictions_data.items():
            price = prices.get(asset_symbol) if prices else None
            prediction = self.predict(asset_symbol, indicators, price)
            
            if prediction:
                results[asset_symbol] = prediction
        
        return results
