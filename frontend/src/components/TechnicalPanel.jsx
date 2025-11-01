import React from 'react';
import { Activity, BarChart2, TrendingUp } from 'lucide-react';

const TechnicalPanel = ({ indicators }) => {
  if (!indicators) {
    return (
      <div className="card">
        <p className="text-gray-400">No technical indicators available</p>
      </div>
    );
  }

  const getRSIColor = (rsi) => {
    if (rsi > 70) return 'text-red-500';
    if (rsi < 30) return 'text-green-500';
    return 'text-yellow-500';
  };

  const getRSIStatus = (rsi) => {
    if (rsi > 70) return 'Overbought';
    if (rsi < 30) return 'Oversold';
    return 'Neutral';
  };

  const getVolatilityColor = (vol) => {
    if (vol > 0.03) return 'text-red-500';
    if (vol < 0.01) return 'text-green-500';
    return 'text-yellow-500';
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4 flex items-center">
        <Activity className="w-5 h-5 mr-2 text-blue-500" />
        Technical Indicators
      </h3>

      <div className="space-y-4">
        {/* RSI */}
        <div className="p-4 bg-dark-bg rounded-lg border border-dark-border">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-400">RSI (14)</span>
            <span className={`text-lg font-bold ${getRSIColor(indicators.rsi)}`}>
              {indicators.rsi.toFixed(2)}
            </span>
          </div>
          <div className="w-full bg-dark-border rounded-full h-2 mb-2">
            <div
              className={`h-2 rounded-full ${
                indicators.rsi > 70 ? 'bg-red-500' :
                indicators.rsi < 30 ? 'bg-green-500' : 'bg-yellow-500'
              }`}
              style={{ width: `${indicators.rsi}%` }}
            />
          </div>
          <p className="text-xs text-gray-500">{getRSIStatus(indicators.rsi)}</p>
        </div>

        {/* MACD */}
        <div className="p-4 bg-dark-bg rounded-lg border border-dark-border">
          <div className="flex items-center mb-3">
            <BarChart2 className="w-4 h-4 mr-2 text-blue-500" />
            <span className="text-sm font-semibold">MACD</span>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-xs text-gray-400 mb-1">MACD Line</p>
              <p className="text-base font-bold">
                {indicators.macd.toFixed(4)}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-400 mb-1">Signal Line</p>
              <p className="text-base font-bold">
                {indicators.macd_signal.toFixed(4)}
              </p>
            </div>
          </div>
          <div className="mt-2 pt-2 border-t border-dark-border">
            <p className="text-xs text-gray-400">
              {indicators.macd > indicators.macd_signal ? (
                <span className="text-green-500">Bullish (MACD above Signal)</span>
              ) : (
                <span className="text-red-500">Bearish (MACD below Signal)</span>
              )}
            </p>
          </div>
        </div>

        {/* Bollinger Bands */}
        <div className="p-4 bg-dark-bg rounded-lg border border-dark-border">
          <div className="flex items-center mb-3">
            <TrendingUp className="w-4 h-4 mr-2 text-blue-500" />
            <span className="text-sm font-semibold">Bollinger Bands</span>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-xs text-gray-400">Upper</span>
              <span className="text-sm font-mono">{indicators.bb_upper.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-gray-400">Middle</span>
              <span className="text-sm font-mono">{indicators.bb_middle.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-gray-400">Lower</span>
              <span className="text-sm font-mono">{indicators.bb_lower.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Volume & Volatility */}
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-dark-bg rounded-lg border border-dark-border">
            <p className="text-xs text-gray-400 mb-1">Volume Ratio</p>
            <p className="text-xl font-bold">
              {indicators.volume_ratio.toFixed(2)}x
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {indicators.volume_ratio > 1.5 ? 'High Volume' : 
               indicators.volume_ratio < 0.5 ? 'Low Volume' : 'Normal'}
            </p>
          </div>

          <div className="p-4 bg-dark-bg rounded-lg border border-dark-border">
            <p className="text-xs text-gray-400 mb-1">Volatility</p>
            <p className={`text-xl font-bold ${getVolatilityColor(indicators.volatility)}`}>
              {(indicators.volatility * 100).toFixed(2)}%
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {indicators.volatility > 0.03 ? 'High' : 
               indicators.volatility < 0.01 ? 'Low' : 'Moderate'}
            </p>
          </div>
        </div>

        {/* Momentum */}
        <div className="p-4 bg-dark-bg rounded-lg border border-dark-border">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-400">Momentum (10d)</span>
            <span className={`text-lg font-bold ${
              indicators.momentum > 0 ? 'text-green-500' : 'text-red-500'
            }`}>
              {(indicators.momentum * 100).toFixed(2)}%
            </span>
          </div>
          <div className="w-full bg-dark-border rounded-full h-2 mt-2">
            <div
              className={`h-2 rounded-full ${
                indicators.momentum > 0 ? 'bg-green-500' : 'bg-red-500'
              }`}
              style={{ 
                width: `${Math.min(Math.abs(indicators.momentum) * 500, 100)}%` 
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TechnicalPanel;
