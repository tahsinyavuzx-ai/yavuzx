import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Area } from 'recharts';
import { signalAPI } from '../services/api';

const PriceChart = ({ assetSymbol }) => {
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMarketData = async () => {
      if (!assetSymbol) return;
      
      setLoading(true);
      setError(null);
      
      try {
        // Get market data from API
        const response = await signalAPI.getMarketData(assetSymbol);
        const marketData = response.data;
        
        if (!marketData || !marketData.historical) {
          throw new Error('No historical data available');
        }

        // Transform data for the chart
        const formattedData = marketData.historical.map(point => ({
          date: new Date(point.timestamp).toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          }),
          price: parseFloat(point.price.toFixed(2)),
          volume: point.volume,
        }));

        setChartData(formattedData);
      } catch (error) {
        console.error('Error fetching market data:', error);
        setError('Failed to load chart data');
        
        // Generate fallback data if needed
        if (process.env.NODE_ENV === 'development') {
          const mockData = generateMockData(assetSymbol);
          setChartData(mockData);
          setError(null);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchMarketData();
  }, [assetSymbol]);

  // Fallback mock data generator for development
  const generateMockData = (symbol) => {
    const data = [];
    const days = 30;
    const basePrice = Math.random() * 1000 + 100; // Random base price between 100 and 1100
    
    for (let i = days; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      const variance = basePrice * 0.15;
      const price = basePrice + (Math.random() - 0.5) * variance;
      
      data.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        price: parseFloat(price.toFixed(2)),
        volume: Math.floor(Math.random() * 1000000) + 500000,
      });
    }
    
    return data;
  };

  if (loading) {
    return (
      <div className="card h-96 flex items-center justify-center">
        <p className="text-gray-400">Loading chart...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card h-96 flex items-center justify-center">
        <p className="text-red-400">{error}</p>
      </div>
    );
  }

  return (
    <div className="card">
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
          <XAxis 
            dataKey="date" 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
            domain={['auto', 'auto']}
            tickFormatter={(value) => `$${value.toLocaleString()}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1a1a1a',
              border: '1px solid #2a2a2a',
              borderRadius: '8px',
              color: '#fff'
            }}
            formatter={(value, name) => [
              name === 'Price' ? `$${value.toLocaleString()}` : value.toLocaleString(),
              name
            ]}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="price"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            name="Price"
          />
          {chartData[0]?.volume && (
            <Area
              type="monotone"
              dataKey="volume"
              fill="#3b82f633"
              stroke="#3b82f6"
              opacity={0.3}
              name="Volume"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PriceChart;
