"""
Market data service - fetches real prices for any stock.
"""
import yfinance as yf
import ccxt
from typing import Optional, Tuple
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MarketDataService:
    """Fetch market data for any stock/crypto."""
    
    def __init__(self):
        self.exchange = ccxt.binance()
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for any symbol."""
        try:
            # Check if crypto (contains _USD or _USDT)
            if '_USD' in symbol or '_USDT' in symbol or symbol in ['BTC_USD', 'ETH_USD']:
                return self._get_crypto_price(symbol)
            else:
                # Stock symbol
                return self._get_stock_price(symbol)
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None
    
    def _normalize_symbol(self, symbol: str) -> str:
        """Convert internal symbol format to provider format."""
        # Special cases for stock symbols
        symbol_map = {
            'BRK_B': 'BRK-B',
            'BF_B': 'BF-B',
        }
        return symbol_map.get(symbol, symbol)

    def _get_stock_price(self, symbol: str) -> Optional[float]:
        """Get stock price from yfinance."""
        try:
            normalized_symbol = self._normalize_symbol(symbol)
            ticker = yf.Ticker(normalized_symbol)
            data = ticker.history(period='1d')
            if not data.empty:
                return float(data['Close'].iloc[-1])
        except Exception as e:
            logger.error(f"Error fetching stock price for {symbol}: {e}")
        return None

    def get_historical_data(self, symbol: str, period: str = '1mo') -> Optional[dict]:
        """Get historical price and volume data."""
        try:
            if '_USD' in symbol or '_USDT' in symbol:
                return self._get_crypto_historical(symbol, period)
            else:
                return self._get_stock_historical(symbol, period)
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None

    def _get_stock_historical(self, symbol: str, period: str) -> Optional[dict]:
        """Get historical stock data from yfinance."""
        try:
            normalized_symbol = self._normalize_symbol(symbol)
            ticker = yf.Ticker(normalized_symbol)
            data = ticker.history(period=period, interval='1h')
            
            if data.empty:
                return None
                
            historical = []
            for timestamp, row in data.iterrows():
                historical.append({
                    'timestamp': timestamp.isoformat(),
                    'price': float(row['Close']),
                    'volume': float(row['Volume'])
                })
            
            return {
                'symbol': symbol,  # Return original symbol
                'current_price': float(data['Close'].iloc[-1]),
                'historical': historical
            }
        except Exception as e:
            logger.error(f"Error fetching stock historical for {symbol}: {e}")
            return None
    
    def _get_crypto_price(self, symbol: str) -> Optional[float]:
        """Get crypto price from ccxt."""
        try:
            # Convert BTC_USD to BTC/USDT format
            ccxt_symbol = symbol.replace('_USD', '/USDT')
            ticker = self.exchange.fetch_ticker(ccxt_symbol)
            return float(ticker['last'])
        except Exception as e:
            logger.error(f"Error fetching crypto price for {symbol}: {e}")
            return None
            
    def _get_crypto_historical(self, symbol: str, period: str) -> Optional[dict]:
        """Get historical crypto data from ccxt."""
        try:
            ccxt_symbol = symbol.replace('_USD', '/USDT')
            
            # Convert period to timestamp
            if period == '1mo':
                timeframe = '1h'
                since = datetime.now() - timedelta(days=30)
            else:
                timeframe = '1d'
                since = datetime.now() - timedelta(days=7)
                
            ohlcv = self.exchange.fetch_ohlcv(
                ccxt_symbol, 
                timeframe=timeframe,
                since=int(since.timestamp() * 1000)
            )
            
            historical = []
            for candle in ohlcv:
                timestamp, _, _, _, close, volume = candle
                historical.append({
                    'timestamp': datetime.fromtimestamp(timestamp/1000).isoformat(),
                    'price': float(close),
                    'volume': float(volume)
                })
            
            return {
                'symbol': symbol,
                'current_price': historical[-1]['price'] if historical else None,
                'historical': historical
            }
        except Exception as e:
            logger.error(f"Error fetching crypto historical for {symbol}: {e}")
            return None
    
    def get_technical_indicators(self, symbol: str) -> Optional[dict]:
        """Calculate technical indicators for any symbol."""
        try:
            # Get historical data
            if '_USD' in symbol:
                data = self._get_crypto_data(symbol)
            else:
                data = self._get_stock_data(symbol)
            
            if data is None or data.empty:
                return None
            
            # Calculate indicators
            indicators = self._calculate_indicators(data)
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol}: {e}")
            return None
    
    def _get_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get stock historical data."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1mo', interval='1h')
            return data
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return None
    
    def _get_crypto_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get crypto historical data."""
        try:
            ccxt_symbol = symbol.replace('_USD', '/USDT')
            ohlcv = self.exchange.fetch_ohlcv(ccxt_symbol, '1h', limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            logger.error(f"Error fetching crypto data for {symbol}: {e}")
            return None
    
    def _calculate_indicators(self, data: pd.DataFrame) -> dict:
        """Calculate technical indicators from OHLCV data."""
        close = data['Close'] if 'Close' in data.columns else data['close']
        high = data['High'] if 'High' in data.columns else data['high']
        low = data['Low'] if 'Low' in data.columns else data['low']
        volume = data['Volume'] if 'Volume' in data.columns else data['volume']
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        bb_middle = close.rolling(window=20).mean()
        bb_std = close.rolling(window=20).std()
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)
        
        # Volume Ratio
        avg_volume = volume.rolling(window=20).mean()
        volume_ratio = volume / avg_volume
        
        # Volatility
        returns = close.pct_change()
        volatility = returns.rolling(window=20).std() * (252 ** 0.5)  # Annualized
        
        # Momentum
        momentum = close / close.shift(10) - 1
        
        # Get latest values
        latest_idx = -1
        return {
            'rsi': float(rsi.iloc[latest_idx]),
            'macd': float(macd.iloc[latest_idx]),
            'macd_signal': float(signal.iloc[latest_idx]),
            'bb_upper': float(bb_upper.iloc[latest_idx]),
            'bb_middle': float(bb_middle.iloc[latest_idx]),
            'bb_lower': float(bb_lower.iloc[latest_idx]),
            'volume_ratio': float(volume_ratio.iloc[latest_idx]),
            'volatility': float(volatility.iloc[latest_idx]),
            'momentum': float(momentum.iloc[latest_idx])
        }
        macd_signal = macd.ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        bb_middle = close.rolling(window=20).mean()
        bb_std = close.rolling(window=20).std()
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)
        
        # Volume ratio
        volume_ma = volume.rolling(window=20).mean()
        volume_ratio = volume.iloc[-1] / volume_ma.iloc[-1] if volume_ma.iloc[-1] > 0 else 1.0
        
        # Volatility
        returns = close.pct_change()
        volatility = returns.rolling(window=20).std().iloc[-1] * 100
        
        # Momentum
        momentum = ((close.iloc[-1] - close.iloc[-10]) / close.iloc[-10]) * 100 if len(close) > 10 else 0
        
        return {
            'rsi': float(rsi.iloc[-1]),
            'macd': float(macd.iloc[-1]),
            'macd_signal': float(macd_signal.iloc[-1]),
            'bb_upper': float(bb_upper.iloc[-1]),
            'bb_middle': float(bb_middle.iloc[-1]),
            'bb_lower': float(bb_lower.iloc[-1]),
            'volume_ratio': float(volume_ratio),
            'volatility': float(volatility),
            'momentum': float(momentum)
        }
