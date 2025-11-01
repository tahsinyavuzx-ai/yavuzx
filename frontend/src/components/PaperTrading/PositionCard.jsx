import React, { useState } from 'react';
import { TrendingUp, TrendingDown, X, Edit2 } from 'lucide-react';
import tradingAPI from '../../services/tradingApi';

const PositionCard = ({ position, onClosed, onUpdated }) => {
  const [showCloseForm, setShowCloseForm] = useState(false);
  const [exitPrice, setExitPrice] = useState('');
  const [loading, setLoading] = useState(false);

  const isPnLPositive = position.pnl_with_leverage >= 0;
  const isLong = position.position_type === 'LONG';

  const handleClose = async () => {
    if (!exitPrice) return;
    
    setLoading(true);
    try {
      await tradingAPI.closePosition(position.id, {
        exit_price: parseFloat(exitPrice),
        notes: `Closed at ${exitPrice}`
      });
      onClosed();
      setShowCloseForm(false);
    } catch (err) {
      console.error('Error closing position:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Delete this position?')) {
      try {
        await tradingAPI.deletePosition(position.id);
        onClosed();
      } catch (err) {
        console.error('Error deleting position:', err);
      }
    }
  };

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          {isLong ? (
            <TrendingUp className="w-6 h-6 text-green-500" />
          ) : (
            <TrendingDown className="w-6 h-6 text-red-500" />
          )}
          <div>
            <h4 className="font-bold text-lg">{position.asset_symbol}</h4>
            <p className="text-xs text-gray-500">{position.asset_class}</p>
          </div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => setShowCloseForm(!showCloseForm)}
            className="text-gray-400 hover:text-blue-400 transition"
            title="Close position"
          >
            <X className="w-5 h-5" />
          </button>
          <button
            onClick={handleDelete}
            className="text-gray-400 hover:text-red-400 transition"
            title="Delete position"
          >
            <Edit2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Position Details */}
      <div className="grid grid-cols-2 gap-3 mb-3 p-3 bg-dark-bg rounded">
        <div>
          <p className="text-xs text-gray-500">Entry Price</p>
          <p className="font-mono">${position.entry_price.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Current Price</p>
          <p className="font-mono">${position.current_price?.toFixed(2) || 'N/A'}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Quantity</p>
          <p className="font-mono">{position.quantity.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Leverage</p>
          <p className="font-mono">{position.leverage.toFixed(1)}x</p>
        </div>
      </div>

      {/* P&L Display */}
      <div className="p-3 bg-dark-bg rounded mb-3">
        <p className="text-xs text-gray-500 mb-1">P&L (with leverage)</p>
        <p className={`text-2xl font-bold ${isPnLPositive ? 'text-green-500' : 'text-red-500'}`}>
          ${position.pnl_with_leverage.toFixed(2)}
        </p>
        <p className={`text-sm ${isPnLPositive ? 'text-green-500' : 'text-red-500'}`}>
          {isPnLPositive ? '+' : ''}{position.pnl_with_leverage_percent.toFixed(2)}%
        </p>
      </div>

      {/* Close Form */}
      {showCloseForm && (
        <div className="p-3 bg-dark-bg rounded border border-dark-border mb-3 space-y-2">
          <input
            type="number"
            value={exitPrice}
            onChange={(e) => setExitPrice(e.target.value)}
            placeholder="Exit price"
            step="0.01"
            className="w-full bg-dark-border border border-dark-border rounded px-2 py-1 text-white text-sm focus:border-blue-500 outline-none"
          />
          <button
            onClick={handleClose}
            disabled={loading || !exitPrice}
            className="w-full btn-primary text-sm py-1"
          >
            {loading ? 'Closing...' : 'Close Position'}
          </button>
        </div>
      )}

      {/* Entry Time */}
      <p className="text-xs text-gray-600">
        Opened: {new Date(position.entry_time).toLocaleDateString()}
      </p>
    </div>
  );
};

export default PositionCard;
