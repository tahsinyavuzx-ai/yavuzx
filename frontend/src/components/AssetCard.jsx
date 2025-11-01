import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const AssetCard = ({ signal, isSelected, onClick }) => {
  // Style and display helper functions
  const getSignalColor = (signalType) => {
    switch (signalType) {
      case 'BUY':
        return 'text-green-500 bg-green-900 border-green-700';
      case 'SELL':
        return 'text-red-500 bg-red-900 border-red-700';
      default:
        return 'text-yellow-500 bg-yellow-900 border-yellow-700';
    }
  };

  const getSignalIcon = (signalType) => {
    switch (signalType) {
      case 'BUY':
        return <TrendingUp className="w-5 h-5" />;
      case 'SELL':
        return <TrendingDown className="w-5 h-5" />;
      default:
        return <Minus className="w-5 h-5" />;
    }
  };

  const getDisplayName = (symbol) => {
    if (symbol === 'BTC_USD') return 'Bitcoin';
    if (symbol === 'ETH_USD') return 'Ethereum';
    return symbol;
  };

  const getAssetType = (symbol) => {
    if (symbol === 'BTC_USD' || symbol === 'ETH_USD') return 'Crypto';
    return 'Stock';
  };

  // Computed values
  const confidencePercentage = (signal.confidence * 100).toFixed(1);

  return (
    <div
      onClick={onClick}
      className={`card cursor-pointer transition-all hover:scale-105 ${
        isSelected ? 'ring-2 ring-blue-500' : ''
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-xl font-bold">{getDisplayName(signal.asset_symbol)}</h3>
          <p className="text-xs text-gray-500">{getAssetType(signal.asset_symbol)}</p>
        </div>
        <div className={`p-2 rounded ${getSignalColor(signal.signal).split(' ')[1]}`}>
          {getSignalIcon(signal.signal)}
        </div>
      </div>

      {/* Price */}
      {signal.current_price && (
        <div className="mb-3">
          <p className="text-2xl font-bold">${signal.current_price.toFixed(2)}</p>
          <p className={`text-sm ${
            signal.predicted_direction === 'UP' ? 'text-green-500' : 'text-red-500'
          }`}>
            Predicted: {signal.predicted_direction}
          </p>
        </div>
      )}

      {/* Signal Badge */}
      <div className={`py-2 px-3 rounded border ${getSignalColor(signal.signal)}`}>
        <div className="flex items-center justify-between">
          <span className="font-bold text-sm">{signal.signal}</span>
          <span className="text-sm">{confidencePercentage}%</span>
        </div>
        <div className="w-full bg-dark-bg rounded-full h-1.5 mt-2">
          <div
            className={`h-1.5 rounded-full ${
              signal.signal === 'BUY' ? 'bg-green-500' :
              signal.signal === 'SELL' ? 'bg-red-500' : 'bg-yellow-500'
            }`}
            style={{ width: `${confidencePercentage}%` }}
          />
        </div>
      </div>

      {/* Timestamp */}
      <p className="text-xs text-gray-600 mt-3">
        {new Date(signal.timestamp).toLocaleTimeString()}
      </p>
    </div>
  );
};

export default AssetCard;
