import React from 'react';
import { BarChart3, TrendingUp, TrendingDown, Target } from 'lucide-react';

const PortfolioStats = ({ stats }) => {
  const winRate = stats.win_rate || 0;
  const isPositive = stats.total_pnl >= 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Total P&L */}
      <div className="card">
        <div className="flex items-center mb-2">
          <BarChart3 className="w-5 h-5 text-blue-500 mr-2" />
          <span className="text-sm text-gray-400">Total P&L</span>
        </div>
        <p className={`text-2xl font-bold ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
          ${stats.total_pnl.toFixed(2)}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          {isPositive ? '+' : ''}{stats.total_pnl_percent.toFixed(2)}%
        </p>
      </div>

      {/* Win Rate */}
      <div className="card">
        <div className="flex items-center mb-2">
          <Target className="w-5 h-5 text-green-500 mr-2" />
          <span className="text-sm text-gray-400">Win Rate</span>
        </div>
        <p className="text-2xl font-bold text-green-500">
          {winRate.toFixed(1)}%
        </p>
        <p className="text-xs text-gray-500 mt-1">
          {stats.closed_positions} trades
        </p>
      </div>

      {/* Largest Win */}
      <div className="card">
        <div className="flex items-center mb-2">
          <TrendingUp className="w-5 h-5 text-green-500 mr-2" />
          <span className="text-sm text-gray-400">Best Trade</span>
        </div>
        <p className="text-2xl font-bold text-green-500">
          ${stats.largest_win.toFixed(2)}
        </p>
        <p className="text-xs text-gray-500 mt-1">Largest win</p>
      </div>

      {/* Largest Loss */}
      <div className="card">
        <div className="flex items-center mb-2">
          <TrendingDown className="w-5 h-5 text-red-500 mr-2" />
          <span className="text-sm text-gray-400">Worst Trade</span>
        </div>
        <p className="text-2xl font-bold text-red-500">
          ${stats.largest_loss.toFixed(2)}
        </p>
        <p className="text-xs text-gray-500 mt-1">Largest loss</p>
      </div>

      {/* Open Positions */}
      <div className="card">
        <p className="text-sm text-gray-400 mb-2">Open Positions</p>
        <p className="text-3xl font-bold text-blue-500">{stats.open_positions}</p>
        <p className="text-xs text-gray-500 mt-1">Active trades</p>
      </div>

      {/* Closed Positions */}
      <div className="card">
        <p className="text-sm text-gray-400 mb-2">Closed Positions</p>
        <p className="text-3xl font-bold text-gray-400">{stats.closed_positions}</p>
        <p className="text-xs text-gray-500 mt-1">Total trades</p>
      </div>

      {/* Avg Win */}
      <div className="card">
        <p className="text-sm text-gray-400 mb-2">Average Win</p>
        <p className="text-2xl font-bold text-green-500">
          ${stats.avg_win.toFixed(2)}
        </p>
        <p className="text-xs text-gray-500 mt-1">Per winning trade</p>
      </div>

      {/* Avg Loss */}
      <div className="card">
        <p className="text-sm text-gray-400 mb-2">Average Loss</p>
        <p className="text-2xl font-bold text-red-500">
          ${stats.avg_loss.toFixed(2)}
        </p>
        <p className="text-xs text-gray-500 mt-1">Per losing trade</p>
      </div>
    </div>
  );
};

export default PortfolioStats;
