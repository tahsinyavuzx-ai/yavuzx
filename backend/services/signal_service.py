"""
Signal generation service - generates signals for all available stocks.
"""
from typing import List, Optional
import asyncio
import logging
from ..models.model_loader import ModelManager
from ..services.market_data_service import MarketDataService
from ..services.prediction_service import PredictionService
from ..models.schemas import PredictionResponse, TechnicalIndicators

logger = logging.getLogger(__name__)


class SignalService:
    """Generate trading signals for all available stocks."""
    
    def __init__(self):
        self.model_manager = ModelManager()
        self.market_service = MarketDataService()
        self.prediction_service = PredictionService(self.model_manager)
    
    async def generate_all_signals(self) -> List[PredictionResponse]:
        """Generate signals for ALL available stocks."""
        available_assets = self.model_manager.get_available_assets()
        logger.info(f"Generating signals for {len(available_assets)} assets")
        
        signals = []
        for asset_symbol in available_assets:
            try:
                signal = await self.generate_signal(asset_symbol)
                if signal:
                    signals.append(signal)
            except Exception as e:
                logger.error(f"Error generating signal for {asset_symbol}: {e}")
        
        logger.info(f"Generated {len(signals)} signals successfully")
        return signals
    
    async def generate_signal(self, asset_symbol: str) -> Optional[PredictionResponse]:
        """Generate signal for a specific stock."""
        try:
            # Get current price
            current_price = self.market_service.get_current_price(asset_symbol)
            
            # Get technical indicators
            indicators_dict = self.market_service.get_technical_indicators(asset_symbol)
            
            if not indicators_dict:
                logger.warning(f"Could not calculate indicators for {asset_symbol}")
                return None
            
            # Create TechnicalIndicators object
            indicators = TechnicalIndicators(**indicators_dict)
            
            # Generate prediction
            prediction = self.prediction_service.predict(
                asset_symbol=asset_symbol,
                indicators=indicators,
                current_price=current_price
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error generating signal for {asset_symbol}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
