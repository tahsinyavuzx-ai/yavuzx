"""
Model loader - uses LOCAL models for any stock
"""
from typing import Optional, Dict, Any, List
from ..utils.local_storage import LocalModelStorage
from ..models.schemas import ModelInfo
import logging

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages ML models from LOCAL storage."""
    
    def __init__(self):
        self.storage = LocalModelStorage()
        self.models: Dict[str, Any] = {}
        self.load_all_models()
        
        # Initialize with dummy models if no models found
        if not self.models:
            logger.warning("No models found in storage, initializing with dummy models")
            self._initialize_dummy_models()
    
    def load_all_models(self):
        """Load all available models."""
        logger.info("Loading all available models from LOCAL storage...")
        
        try:
            available_assets = self.storage.list_available_assets()
            logger.info(f"Found {len(available_assets)} assets with trained models")
            
            for asset in available_assets:
                model = self.storage.load_model(asset)
                if model:
                    self.models[asset] = model
                    logger.info(f"✅ Loaded {asset} model")
                else:
                    logger.warning(f"❌ Failed to load model for {asset}")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            
    def _initialize_dummy_models(self):
        """Initialize dummy models for development."""
        from sklearn.dummy import DummyClassifier
        import numpy as np
        
        # Default stock list
        default_stocks = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA',
            'BRK_B', 'JPM', 'V', 'WMT', 'BAC', 'CRM', 'AMD', 'INTC'
        ]
        
        for symbol in default_stocks:
            # Create a dummy classifier that predicts randomly
            dummy = DummyClassifier(strategy='stratified')
            dummy.fit(np.array([[0]]), np.array([0]))  # Minimal fit
            
            # Add predict_proba method if not present
            if not hasattr(dummy, 'predict_proba'):
                def predict_proba(X):
                    n_samples = len(X)
                    return np.random.uniform(0, 1, size=(n_samples, 2))
                dummy.predict_proba = predict_proba
            
            self.models[symbol] = {
                'model': dummy,
                'version': '1.0.0-dummy'
            }
            logger.info(f"✅ Initialized dummy model for {symbol}")
    
    def get_model(self, asset_symbol: str) -> Optional[Any]:
        """Get a trained model by symbol (AAPL, TSLA, etc)."""
        return self.models.get(asset_symbol.upper())
    
    def get_available_assets(self) -> List[str]:
        """Get list of all assets with loaded models."""
        return list(self.models.keys())
    
    def get_model_info(self, asset_symbol: str) -> Optional[ModelInfo]:
        """Get model information."""
        if asset_symbol.upper() not in self.models:
            return None
        
        timestamp = self.storage.get_model_timestamp(asset_symbol)
        
        return ModelInfo(
            asset_symbol=asset_symbol,
            version="1.0.0",
            loaded=True,
            last_updated=timestamp.isoformat() if timestamp else "Unknown"
        )
