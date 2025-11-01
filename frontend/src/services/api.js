import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Predefined market cap order for sorting
const MARKET_CAP_ORDER = [
  'NVDA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'BRK_B',
  'AVGO', 'JPM', 'LLY', 'V', 'UNH', 'WMT', 'MA', 'XOM', 'ORCL',
  'HD', 'COST', 'NFLX', 'BAC', 'CRM', 'AMD', 'CSCO', 'INTC',
  'QCOM', 'PLTR', 'ADBE', 'PANW', 'CRWD', 'APP', 'AXP', 'GS',
  'MS', 'BLK', 'C', 'WFC', 'BA', 'CAT', 'CVX', 'JNJ', 'MRK',
  'BTC_USD', 'ETH_USD'
];

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health endpoints
export const healthAPI = {
  check: () => api.get('/health/'),
  listModels: () => api.get('/health/models'),
};

// Prediction endpoints
export const predictionAPI = {
  predict: (assetSymbol, indicators = null) => 
    api.post('/predictions/predict', {
      asset_symbol: assetSymbol,
      indicators: indicators,
    }),
  
  predictBatch: (assets) => 
    api.post('/predictions/predict/batch', {
      assets: assets,
    }),
  
  getModelInfo: (assetSymbol) => 
    api.get(`/predictions/models/${assetSymbol}`),
};

// Signal endpoints
export const signalAPI = {
  getSignal: (assetSymbol) => 
    api.get(`/signals/signal/${assetSymbol}`),
  
  getAllSignals: async () => {
    const response = await api.get('/signals/signals/all');
    
    // Sort by market cap order
    response.data.sort((a, b) => {
      const indexA = MARKET_CAP_ORDER.indexOf(a.asset_symbol);
      const indexB = MARKET_CAP_ORDER.indexOf(b.asset_symbol);
      return (indexA === -1 ? 999 : indexA) - (indexB === -1 ? 999 : indexB);
    });
    
    return response;
  },
  
  getMarketData: (assetSymbol) => 
    api.get(`/signals/market/${assetSymbol}`),
};

export default api;
