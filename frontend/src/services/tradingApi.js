import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const tradingAPI = {
  // Positions CRUD
  createPosition: (data) =>
    axios.post(`${API_BASE_URL}/trading/positions`, data),
  
  getAllPositions: (status = null) => {
    const params = status ? `?status=${status}` : '';
    return axios.get(`${API_BASE_URL}/trading/positions${params}`);
  },
  
  getPosition: (positionId) =>
    axios.get(`${API_BASE_URL}/trading/positions/${positionId}`),
  
  getOpenPositionsWithPnL: () =>
    axios.get(`${API_BASE_URL}/trading/positions/open/with-pnl`),
  
  updatePosition: (positionId, data) =>
    axios.put(`${API_BASE_URL}/trading/positions/${positionId}`, data),
  
  closePosition: (positionId, data) =>
    axios.post(`${API_BASE_URL}/trading/positions/${positionId}/close`, data),
  
  deletePosition: (positionId) =>
    axios.delete(`${API_BASE_URL}/trading/positions/${positionId}`),
  
  // Portfolio stats
  getPortfolioStats: () =>
    axios.get(`${API_BASE_URL}/trading/portfolio/stats`),
};

export default tradingAPI;
