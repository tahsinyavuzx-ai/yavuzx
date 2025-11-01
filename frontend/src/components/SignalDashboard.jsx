import React from 'react';
import { TrendingUp, TrendingDown, Minus, DollarSign } from 'lucide-react';

const SignalDashboard = ({ signal }) => {
  if (!signal) return null;

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
        return <TrendingUp className="w-8 h-8" />;
      case 'SELL':
        return <TrendingDown className="w-8 h-8" />;
      default:
        return <Minus className="w-8 h-8" />;
    }
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4 flex items-center">
        <DollarSign className="w-5 h-5 mr-2 text-blue-500" />
        Signal Details
      </h3>

      <div className="space-y-4">
        {/* Current Price */}
        {signal.current_price && (
          <div>
            <p className="text-sm text-gray-400 mb-1">Current Price</p>
            <p className="text-2xl font-bold">
              ${signal.current_price.toFixed(2)}
            </p>
          </div>
        )}

        {/* Signal Badge */}
        <div className={`p-4 rounded border ${getSignalColor(signal.signal)}`}>
          <div className="flex items-center justify-between mb-2">
            {getSignalIcon(signal.signal)}
            <span className="text-3xl font-bold">{signal.signal}</span>
          </div>
          <div className="flex justify-between text-sm mt-2">
            <span>Confidence:</span>
            <span className="font-bold">{(signal.confidence * 100).toFixed(1)}%</span>
          </div>
          <div className="w-full bg-dark-bg rounded-full h-2 mt-2">
            <div
              className={`h-2 rounded-full ${
                signal.signal === 'BUY' ? 'bg-green-500' :
                signal.signal === 'SELL' ? 'bg-red-500' : 'bg-yellow-500'
              }`}
              style={{ width: `${signal.confidence * 100}%` }}
            />
          </div>
        </div>

        {/* Prediction */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-400 mb-1">Direction</p>
            <p className={`font-semibold ${
              signal.predicted_direction === 'UP' ? 'text-green-500' : 'text-red-500'
            }`}>
              {signal.predicted_direction}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-400 mb-1">Model Version</p>
            <p className="font-semibold text-gray-300">{signal.model_version}</p>
          </div>
        </div>

        {/* Timestamp */}
        <div className="pt-4 border-t border-dark-border">
          <p className="text-xs text-gray-500">
            Generated: {new Date(signal.timestamp).toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignalDashboard;
