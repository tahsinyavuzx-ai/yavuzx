"""
Local file-based model storage - supports any stock/asset
"""
from pathlib import Path
import pickle
import logging
from datetime import datetime, timedelta
from typing import List, Optional

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).parent.parent / "models_local" / "trained-models"


class LocalModelStorage:
    """Load models from local filesystem."""
    
    def __init__(self):
        self._cache = {}
        self._cache_timestamps = {}
        MODELS_DIR.mkdir(exist_ok=True)
        logger.info(f"📁 Using local models directory: {MODELS_DIR}")
    
    def list_available_assets(self) -> List[str]:
        """List all available assets with trained models."""
        try:
            files = list(MODELS_DIR.glob("*_4h_v1_*.pkl"))
            # Extract unique asset names (e.g., AAPL, TSLA, BTC_USD)
            assets = set()
            for f in files:
                asset_name = f.name.split('_4h_')[0]
                assets.add(asset_name)
            return sorted(list(assets))
        except Exception as e:
            logger.error(f"Error listing assets: {e}")
            return []
    
    def load_model(self, asset_symbol: str, cache_ttl: int = 3600):
        """
        Load model for any asset symbol.
        
        Args:
            asset_symbol: Stock symbol like AAPL, TSLA, BTC_USD
            cache_ttl: Cache time in seconds
        """
        cache_key = f"model_{asset_symbol.lower()}"
        
        # Check cache
        if cache_key in self._cache:
            if datetime.utcnow() - self._cache_timestamps[cache_key] < timedelta(seconds=cache_ttl):
                logger.info(f"✅ CACHED: {asset_symbol}")
                return self._cache[cache_key]
        
        # Find latest model file for this asset
        pattern = f"{asset_symbol}_4h_v1_*.pkl"
        try:
            files = sorted(
                MODELS_DIR.glob(pattern),
                key=lambda x: x.name,
                reverse=True
            )
        except Exception as e:
            logger.error(f"Error finding model for {asset_symbol}: {e}")
            return None
        
        if not files:
            logger.warning(f"⚠️ No model file for {asset_symbol}")
            return None
        
        latest_file = files[0]
        
        try:
            with open(latest_file, 'rb') as f:
                model = pickle.load(f)
            
            # Cache it
            self._cache[cache_key] = model
            self._cache_timestamps[cache_key] = datetime.utcnow()
            
            logger.info(f"✅ LOADED: {asset_symbol} from {latest_file.name}")
            return model
            
        except Exception as e:
            logger.error(f"❌ Error loading {latest_file.name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def is_connected(self) -> bool:
        """Always true for local storage."""
        return True
    
    def get_model_timestamp(self, asset_symbol: str) -> Optional[datetime]:
        """Get timestamp of latest model for an asset."""
        pattern = f"{asset_symbol}_4h_v1_*.pkl"
        try:
            files = sorted(MODELS_DIR.glob(pattern), key=lambda x: x.name, reverse=True)
            if files:
                # Parse timestamp from filename: AAPL_4h_v1_20251031_110141.pkl
                filename = files[0].stem
                date_part = filename.split('_')[-2]  # 20251031
                time_part = filename.split('_')[-1]  # 110141
                
                timestamp_str = f"{date_part}{time_part}"
                return datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
        except Exception as e:
            logger.error(f"Error parsing timestamp for {asset_symbol}: {e}")
        return None
