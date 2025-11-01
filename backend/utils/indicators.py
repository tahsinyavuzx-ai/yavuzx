"""
Technical indicator calculations.
Production-grade implementation with proper error handling.
"""
import pandas as pd
import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicatorCalculator:
    """Calculate technical indicators from price data."""
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            prices: Price series
            period: RSI period (default 14)
            
        Returns:
            RSI value (0-100)
        """
        if len(prices) < period + 1:
            logger.warning(f"Insufficient data for RSI calculation: {len(prices)} < {period + 1}")
            return 50.0  # Neutral value
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else 50.0
    
    @staticmethod
    def calculate_macd(prices: pd.Series, 
                       fast: int = 12, 
                       slow: int = 26, 
                       signal: int = 9) -> Tuple[float, float]:
        """
        Calculate MACD and signal line.
        
        Args:
            prices: Price series
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
            
        Returns:
            Tuple of (macd_value, signal_value)
        """
        if len(prices) < slow + signal:
            logger.warning(f"Insufficient data for MACD calculation")
            return 0.0, 0.0
        
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        
        return float(macd_line.iloc[-1]), float(signal_line.iloc[-1])
    
    @staticmethod
    def calculate_bollinger_bands(prices: pd.Series, 
                                   period: int = 20, 
                                   std_dev: float = 2.0) -> Tuple[float, float, float]:
        """
        Calculate Bollinger Bands.
        
        Args:
            prices: Price series
            period: Moving average period
            std_dev: Standard deviation multiplier
            
        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        if len(prices) < period:
            logger.warning(f"Insufficient data for Bollinger Bands calculation")
            last_price = float(prices.iloc[-1])
            return last_price * 1.02, last_price, last_price * 0.98
        
        middle_band = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        return (
            float(upper_band.iloc[-1]),
            float(middle_band.iloc[-1]),
            float(lower_band.iloc[-1])
        )
    
    @staticmethod
    def calculate_volume_ratio(volumes: pd.Series, period: int = 20) -> float:
        """
        Calculate volume ratio (current volume / average volume).
        
        Args:
            volumes: Volume series
            period: Average period
            
        Returns:
            Volume ratio
        """
        if len(volumes) < period:
            return 1.0
        
        avg_volume = volumes.rolling(window=period).mean().iloc[-1]
        current_volume = volumes.iloc[-1]
        
        if avg_volume == 0:
            return 1.0
        
        return float(current_volume / avg_volume)
    
    @staticmethod
    def calculate_volatility(prices: pd.Series, period: int = 20) -> float:
        """
        Calculate price volatility (standard deviation of returns).
        
        Args:
            prices: Price series
            period: Calculation period
            
        Returns:
            Volatility value
        """
        if len(prices) < period + 1:
            return 0.01
        
        returns = prices.pct_change().dropna()
        volatility = returns.rolling(window=period).std().iloc[-1]
        
        return float(volatility) if not np.isnan(volatility) else 0.01
    
    @staticmethod
    def calculate_momentum(prices: pd.Series, period: int = 10) -> float:
        """
        Calculate price momentum (rate of change).
        
        Args:
            prices: Price series
            period: Momentum period
            
        Returns:
            Momentum value
        """
        if len(prices) < period + 1:
            return 0.0
        
        momentum = (prices.iloc[-1] - prices.iloc[-period]) / prices.iloc[-period]
        
        return float(momentum) if not np.isnan(momentum) else 0.0
    
    @classmethod
    def calculate_all_indicators(cls, 
                                  prices: pd.Series, 
                                  volumes: Optional[pd.Series] = None) -> dict:
        """
        Calculate all technical indicators at once.
        
        Args:
            prices: Price series
            volumes: Volume series (optional)
            
        Returns:
            Dictionary with all indicators
        """
        rsi = cls.calculate_rsi(prices)
        macd, macd_signal = cls.calculate_macd(prices)
        bb_upper, bb_middle, bb_lower = cls.calculate_bollinger_bands(prices)
        volatility = cls.calculate_volatility(prices)
        momentum = cls.calculate_momentum(prices)
        
        indicators = {
            "rsi": rsi,
            "macd": macd,
            "macd_signal": macd_signal,
            "bb_upper": bb_upper,
            "bb_middle": bb_middle,
            "bb_lower": bb_lower,
            "volatility": volatility,
            "momentum": momentum,
            "volume_ratio": 1.0
        }
        
        if volumes is not None:
            indicators["volume_ratio"] = cls.calculate_volume_ratio(volumes)
        
        return indicators
