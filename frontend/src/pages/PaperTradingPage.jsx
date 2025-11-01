import React, { useState, useEffect } from 'react';
import { Plus, RefreshCw } from 'lucide-react';
import CreatePositionForm from '../components/PaperTrading/CreatePositionForm';
import PositionCard from '../components/PaperTrading/PositionCard';
import PortfolioStats from '../components/PaperTrading/PortfolioStats';
import tradingAPI from '../services/tradingApi';

const PaperTradingPage = () => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [positions, setPositions] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('OPEN');

  // Fetch data
  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch positions with P&L
      const positionsRes = await tradingAPI.getOpenPositionsWithPnL();
      
      // Fetch portfolio stats
      const statsRes = await tradingAPI.getPortfolioStats();

      setPositions(positionsRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Error fetching trading data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchData();
    // Refresh every 10 seconds for real-time P&L updates
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handlePositionCreated = () => {
    fetchData();
  };

  const handlePositionClosed = () => {
    fetchData();
  };

  const filteredPositions = positions.filter(p => 
    filter === 'OPEN' ? p.status === 'OPEN' : true
  );

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Header */}
      <header className="border-b border-dark-border bg-dark-card sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Paper Trading</h1>
              <p className="text-sm text-gray-400 mt-1">
                Simulate trades and track potential gains/losses
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={fetchData}
                disabled={loading}
                className="btn-secondary flex items-center space-x-2"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>

              <button
                onClick={() => setShowCreateForm(true)}
                className="btn-primary flex items-center space-x-2"
              >
                <Plus className="w-5 h-5" />
                <span>New Position</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Portfolio Stats */}
        {stats && (
          <>
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <BarChart3 className="w-5 h-5 mr-2 text-blue-500" />
              Portfolio Statistics
            </h2>
            <PortfolioStats stats={stats} />
            <div className="my-8"></div>
          </>
        )}

        {/* Positions Section */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Your Positions</h2>

          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-500" />
                <p className="text-gray-400">Loading positions...</p>
              </div>
            </div>
          ) : filteredPositions.length === 0 ? (
            <div className="card text-center py-12">
              <p className="text-gray-400 mb-4">No open positions</p>
              <button
                onClick={() => setShowCreateForm(true)}
                className="btn-primary"
              >
                Create Your First Position
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredPositions.map(position => (
                <PositionCard
                  key={position.id}
                  position={position}
                  onClosed={handlePositionClosed}
                  onUpdated={handlePositionClosed}
                />
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Create Position Modal */}
      {showCreateForm && (
        <CreatePositionForm
          onPositionCreated={handlePositionCreated}
          onClose={() => setShowCreateForm(false)}
        />
      )}
    </div>
  );
};

export default PaperTradingPage;
