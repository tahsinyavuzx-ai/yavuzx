# continuous_learning_trainer_local.py - FIXED VERSION
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd
import pickle
import json
import logging
from pathlib import Path
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Top 100+ Stocks
TOP_100_STOCKS = {
    "NVDA": "NVIDIA", "AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Alphabet",
    "AMZN": "Amazon", "META": "Meta", "TSLA": "Tesla", "AVGO": "Broadcom",
    "ORCL": "Oracle", "NFLX": "Netflix", "AMD": "AMD", "CSCO": "Cisco",
    "INTC": "Intel", "QCOM": "Qualcomm", "PLTR": "Palantir", "CRM": "Salesforce",
    "ADBE": "Adobe", "PANW": "Palo Alto", "CRWD": "CrowdStrike", "APP": "AppLovin",
    "BRK-B": "Berkshire", "JPM": "JPMorgan", "V": "Visa", "MA": "Mastercard",
    "BAC": "Bank of America", "WFC": "Wells Fargo", "MS": "Morgan Stanley",
    "GS": "Goldman Sachs", "AXP": "Amex", "BLK": "BlackRock", "C": "Citigroup",
    "LLY": "Eli Lilly", "JNJ": "Johnson & Johnson", "UNH": "UnitedHealth",
    "MRK": "Merck", "WMT": "Walmart", "COST": "Costco", "HD": "Home Depot",
    "XOM": "Exxon", "CVX": "Chevron", "CAT": "Caterpillar", "BA": "Boeing",
    "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum",
}

@dataclass
class TrainingHistory:
    run_id: str
    timestamp: datetime
    ticker: str
    samples_trained: int
    cumulative_samples: int
    accuracy: float
    training_duration_seconds: float
    data_start_date: str
    data_end_date: str

@dataclass
class ModelSnapshot:
    version: int
    model_name: str
    ticker: str
    created_at: datetime
    total_training_samples: int
    accuracy: float
    feature_names: List[str]
    is_incremental_update: bool
    parent_version: Optional[int]

class ContinuousLearningTrainer:
    def __init__(self, local_storage_path: str = "./ml_models", 
                 data_retention_days: int = 365, incremental_mode: bool = True):
        self.storage_path = Path(local_storage_path)
        self.data_retention_days = data_retention_days
        self.incremental_mode = incremental_mode
        
        self.models_dir = self.storage_path / "trained-models"
        self.data_dir = self.storage_path / "training-data"
        self.history_dir = self.storage_path / "training-history"
        
        self._ensure_directories_exist()
        
    def _ensure_directories_exist(self) -> None:
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Using local storage: {self.storage_path.absolute()}")
    
    def fetch_new_market_data(self, ticker: str, last_fetch_time: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch REAL market data with improved error handling."""
        logger.info(f"Fetching data for {ticker}...")
        
        try:
            import yfinance as yf
            
            # Add small delay to avoid rate limiting
            time.sleep(0.5)
            
            stock = yf.Ticker(ticker)
            
            # Use period instead of start date (more reliable)
            try:
                data = stock.history(period="3mo", interval="1d")
            except Exception as e:
                logger.warning(f"Failed with 3mo period, trying 1mo: {e}")
                data = stock.history(period="1mo", interval="1d")
            
            if data.empty:
                logger.warning(f"No data available for {ticker}")
                return pd.DataFrame()
            
            # Reset index and clean up
            data = data.reset_index()
            
            # Handle different date column names
            if 'Date' in data.columns:
                data.rename(columns={'Date': 'timestamp'}, inplace=True)
            elif 'Datetime' in data.columns:
                data.rename(columns={'Datetime': 'timestamp'}, inplace=True)
            
            # Standardize column names
            data.rename(columns={
                'Open': 'open', 'High': 'high', 'Low': 'low',
                'Close': 'close', 'Volume': 'volume'
            }, inplace=True)
            
            # Select only needed columns
            required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            data = data[[col for col in required_cols if col in data.columns]]
            
            # Convert timestamp to timezone-naive datetime
            data['timestamp'] = pd.to_datetime(data['timestamp']).dt.tz_localize(None)
            
            # Filter by last fetch time if provided
            if last_fetch_time is not None:
                # Ensure last_fetch_time is timezone-naive
                if hasattr(last_fetch_time, 'tzinfo') and last_fetch_time.tzinfo is not None:
                    last_fetch_time = last_fetch_time.replace(tzinfo=None)
                data = data[data['timestamp'] > last_fetch_time]
            
            logger.info(f"Fetched {len(data)} samples for {ticker}")
            return data
        
        except Exception as e:
            logger.error(f"Failed to fetch {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def compute_features(self, ohlcv_data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Compute technical indicators."""
        df = ohlcv_data.copy()
        
        df['returns'] = df['close'].pct_change()
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)  # Avoid division by zero
        df['rsi_14'] = 100 - (100 / (1 + rs))
        
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / (df['bb_middle'] + 1e-10)
        
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / (df['volume_sma'] + 1e-10)
        
        df['volatility_7d'] = df['returns'].rolling(window=7).std()
        df['price_momentum'] = df['close'].pct_change(periods=5)
        
        df['future_return'] = df['close'].shift(-1) / df['close'] - 1
        df['label'] = (df['future_return'] > 0).astype(int)
        
        feature_cols = ['rsi_14', 'macd', 'bb_width', 'volume_ratio', 
                       'volatility_7d', 'price_momentum']
        
        df_clean = df.dropna()
        
        if len(df_clean) < 30:
            raise ValueError(f"Not enough data samples: {len(df_clean)}")
        
        features = df_clean[feature_cols]
        labels = df_clean['label']
        
        logger.info(f"Computed {len(features)} feature samples")
        return features, labels
    
    def load_accumulated_data(self, ticker: str) -> Optional[pd.DataFrame]:
        file_path = self.data_dir / f"{ticker.replace('-', '_')}_data.parquet"
        try:
            df = pd.read_parquet(file_path)
            # Ensure timezone-naive
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
            logger.info(f"Loaded {len(df)} accumulated samples for {ticker}")
            return df
        except:
            return None
    
    def save_accumulated_data(self, ticker: str, accumulated_data: pd.DataFrame) -> None:
        # Keep recent data only
        cutoff_date = datetime.utcnow() - timedelta(days=self.data_retention_days)
        if 'timestamp' in accumulated_data.columns:
            # Ensure timezone-naive
            accumulated_data['timestamp'] = pd.to_datetime(accumulated_data['timestamp']).dt.tz_localize(None)
            accumulated_data = accumulated_data[accumulated_data['timestamp'] >= cutoff_date]
        
        file_path = self.data_dir / f"{ticker.replace('-', '_')}_data.parquet"
        accumulated_data.to_parquet(file_path, index=False)
        logger.info(f"Saved {len(accumulated_data)} samples for {ticker}")
    
    def load_previous_model(self, ticker: str) -> Optional[Tuple[Any, ModelSnapshot]]:
        try:
            pattern = f"{ticker.replace('-', '_')}_*.pkl"
            model_files = list(self.models_dir.glob(pattern))
            
            if not model_files:
                return None
            
            latest_model = max(model_files, key=lambda p: p.stat().st_mtime)
            
            with open(latest_model, 'rb') as f:
                model_data = pickle.load(f)
            
            logger.info(f"Loaded previous model: {latest_model.name}")
            return model_data['model_tuple'], model_data['metadata']
        except:
            return None
    
    def train_with_accumulation(self, ticker: str) -> Tuple[Any, ModelSnapshot, TrainingHistory]:
        start_time = datetime.utcnow()
        
        accumulated_ohlcv = self.load_accumulated_data(ticker)
        last_timestamp = None
        
        if accumulated_ohlcv is not None and len(accumulated_ohlcv) > 0:
            last_timestamp = accumulated_ohlcv['timestamp'].max()
        
        new_ohlcv = self.fetch_new_market_data(ticker, last_timestamp)
        
        if new_ohlcv.empty and accumulated_ohlcv is None:
            raise ValueError(f"No data available for {ticker}")
        
        if accumulated_ohlcv is not None and not new_ohlcv.empty:
            combined_ohlcv = pd.concat([accumulated_ohlcv, new_ohlcv], ignore_index=True)
            combined_ohlcv = combined_ohlcv.drop_duplicates(subset=['timestamp'])
            combined_ohlcv = combined_ohlcv.sort_values('timestamp').reset_index(drop=True)
        elif new_ohlcv.empty:
            combined_ohlcv = accumulated_ohlcv
        else:
            combined_ohlcv = new_ohlcv
        
        self.save_accumulated_data(ticker, combined_ohlcv)
        
        features, labels = self.compute_features(combined_ohlcv)
        
        previous_model_data = self.load_previous_model(ticker)
        
        if self.incremental_mode and previous_model_data is not None:
            model_tuple, metadata = self._train_incremental(features, labels, ticker, previous_model_data)
        else:
            model_tuple, metadata = self._train_from_scratch(features, labels, ticker)
        
        self._save_versioned_model(model_tuple, metadata)
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        history = TrainingHistory(
            run_id=f"{ticker}_{start_time.strftime('%Y%m%d_%H%M%S')}",
            timestamp=start_time,
            ticker=ticker,
            samples_trained=len(new_ohlcv),
            cumulative_samples=len(features),
            accuracy=metadata.accuracy,
            training_duration_seconds=duration,
            data_start_date=combined_ohlcv['timestamp'].min().isoformat(),
            data_end_date=combined_ohlcv['timestamp'].max().isoformat()
        )
        
        return model_tuple, metadata, history
    
    def _train_incremental(self, features, labels, ticker, previous_model_data):
        previous_model, previous_metadata = previous_model_data
        previous_xgb, previous_scaler = previous_model
        
        features_scaled = previous_scaler.transform(features)
        dtrain = xgb.DMatrix(features_scaled, label=labels)
        
        params = {'objective': 'binary:logistic', 'max_depth': 10, 'learning_rate': 0.01}
        
        updated_model = xgb.train(params, dtrain, num_boost_round=50, xgb_model=previous_xgb)
        
        predictions = (updated_model.predict(dtrain) > 0.5).astype(int)
        accuracy = (predictions == labels).mean()
        
        metadata = ModelSnapshot(
            version=previous_metadata.version + 1,
            model_name=f"{ticker.replace('-', '_')}_4h",
            ticker=ticker,
            created_at=datetime.utcnow(),
            total_training_samples=len(features),
            accuracy=accuracy,
            feature_names=features.columns.tolist(),
            is_incremental_update=True,
            parent_version=previous_metadata.version
        )
        
        return (updated_model, previous_scaler), metadata
    
    def _train_from_scratch(self, features, labels, ticker):
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        dtrain = xgb.DMatrix(features_scaled, label=labels)
        
        params = {'objective': 'binary:logistic', 'max_depth': 10, 'learning_rate': 0.05}
        
        model = xgb.train(params, dtrain, num_boost_round=100)
        
        predictions = (model.predict(dtrain) > 0.5).astype(int)
        accuracy = (predictions == labels).mean()
        
        metadata = ModelSnapshot(
            version=1,
            model_name=f"{ticker.replace('-', '_')}_4h",
            ticker=ticker,
            created_at=datetime.utcnow(),
            total_training_samples=len(features),
            accuracy=accuracy,
            feature_names=features.columns.tolist(),
            is_incremental_update=False,
            parent_version=None
        )
        
        return (model, scaler), metadata
    
    def _save_versioned_model(self, model_tuple, metadata):
        filename = f"{metadata.model_name}_v{metadata.version}_{metadata.created_at.strftime('%Y%m%d_%H%M%S')}.pkl"
        file_path = self.models_dir / filename
        
        with open(file_path, 'wb') as f:
            pickle.dump({'model_tuple': model_tuple, 'metadata': metadata}, f)
        
        logger.info(f"Saved model to {file_path}")
    
    def _save_training_history(self, history):
        file_path = self.history_dir / f"{history.ticker.replace('-', '_')}_history.jsonl"
        
        history_dict = asdict(history)
        history_dict['timestamp'] = history.timestamp.isoformat()
        
        with open(file_path, 'a') as f:
            f.write(json.dumps(history_dict) + "\n")


if __name__ == "__main__":
    trainer = ContinuousLearningTrainer()
    
    for ticker in ["NVDA", "AAPL", "MSFT"]:
        try:
            model, metadata, history = trainer.train_with_accumulation(ticker)
            print(f"✓ {ticker} - Accuracy: {metadata.accuracy:.2%}")
        except Exception as e:
            print(f"✗ {ticker} failed: {e}")
