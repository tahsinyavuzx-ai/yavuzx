import React, { useState } from 'react';
import { Plus, X } from 'lucide-react';
import tradingAPI from '../../services/tradingApi';

const CreatePositionForm = ({ onPositionCreated, onClose }) => {
  const [formData, setFormData] = useState({
    asset_class: 'NASDAQ',
    asset_symbol: 'AAPL',
    position_type: 'LONG',
    entry_price: '',
    quantity: '',
    leverage: 1,
    notes: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const assets = ['NASDAQ', 'CRYPTO', 'GOLD', 'SILVER', 'PALLADIUM'];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'entry_price' || name === 'quantity' || name === 'leverage'
        ? parseFloat(value) || ''
        : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await tradingAPI.createPosition(formData);
      setFormData({
        asset_class: 'NASDAQ',
        asset_symbol: 'AAPL',
        position_type: 'LONG',
        entry_price: '',
        quantity: '',
        leverage: 1,
        notes: '',
      });
      onPositionCreated();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create position');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="card w-full max-w-md mx-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold flex items-center">
            <Plus className="w-5 h-5 mr-2 text-blue-500" />
            New Position
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Asset Class */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Asset Class</label>
            <select
              name="asset_class"
              value={formData.asset_class}
              onChange={handleChange}
              className="w-full bg-dark-bg border border-dark-border rounded px-3 py-2 text-white focus:border-blue-500 outline-none"
            >
              {assets.map(asset => (
                <option key={asset} value={asset}>{asset}</option>
              ))}
            </select>
          </div>

          {/* Asset Symbol */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Symbol</label>
            <input
              type="text"
              name="asset_symbol"
              value={formData.asset_symbol}
              onChange={handleChange}
              placeholder="e.g., AAPL, BTC"
              className="w-full bg-dark-bg border border-dark-border rounded px-3 py-2 text-white focus:border-blue-500 outline-none"
              required
            />
          </div>

          {/* Position Type */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Position Type</label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, position_type: 'LONG' }))}
                className={`flex-1 py-2 rounded font-semibold transition ${
                  formData.position_type === 'LONG'
                    ? 'bg-green-600 text-white'
                    : 'bg-dark-bg border border-dark-border text-gray-400'
                }`}
              >
                LONG ↑
              </button>
              <button
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, position_type: 'SHORT' }))}
                className={`flex-1 py-2 rounded font-semibold transition ${
                  formData.position_type === 'SHORT'
                    ? 'bg-red-600 text-white'
                    : 'bg-dark-bg border border-dark-border text-gray-400'
                }`}
              >
                SHORT ↓
              </button>
            </div>
          </div>

          {/* Entry Price */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Entry Price</label>
            <input
              type="number"
              name="entry_price"
              value={formData.entry_price}
              onChange={handleChange}
              placeholder="0.00"
              step="0.01"
              className="w-full bg-dark-bg border border-dark-border rounded px-3 py-2 text-white focus:border-blue-500 outline-none"
              required
            />
          </div>

          {/* Quantity */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Quantity</label>
            <input
              type="number"
              name="quantity"
              value={formData.quantity}
              onChange={handleChange}
              placeholder="0.00"
              step="0.01"
              className="w-full bg-dark-bg border border-dark-border rounded px-3 py-2 text-white focus:border-blue-500 outline-none"
              required
            />
          </div>

          {/* Leverage */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Leverage ({formData.leverage}x)</label>
            <input
              type="range"
              name="leverage"
              min="1"
              max="10"
              step="0.5"
              value={formData.leverage}
              onChange={handleChange}
              className="w-full"
            />
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Notes (Optional)</label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              placeholder="Add notes about this position..."
              rows="2"
              className="w-full bg-dark-bg border border-dark-border rounded px-3 py-2 text-white focus:border-blue-500 outline-none"
            />
          </div>

          {error && (
            <div className="p-3 bg-red-900 border border-red-700 rounded text-red-200 text-sm">
              {error}
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-2 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary flex-1"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex-1"
            >
              {loading ? 'Creating...' : 'Create Position'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreatePositionForm;
