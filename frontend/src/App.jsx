import React, { useState, useEffect } from 'react';
import { Activity, TrendingUp, DollarSign, RefreshCw, BarChart3 } from 'lucide-react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import SignalDashboard from './components/SignalDashboard';
import AssetCard from './components/AssetCard';
import TechnicalPanel from './components/TechnicalPanel';
import PriceChart from './components/PriceChart';
import ModelStatus from './components/ModelStatus';
import PaperTradingPage from './pages/PaperTradingPage';
import { signalAPI, healthAPI } from './services/api';

function DashboardContent() {
  const [signals, setSignals] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [filter, setFilter] = useState('ALL');

  const fetchSignals = async () => {
    setLoading(true);
    try {
      const response = await signalAPI.getAllSignals();
      setSignals(response.data);
      setLastUpdate(new Date());
      
      if (!selectedAsset && response.data.length > 0) {
        setSelectedAsset(response.data[0]);
      }
    } catch (error) {
      console.error('Error fetching signals:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchHealth = async () => {
    try {
      const response = await healthAPI.check();
      setHealth(response.data);
    } catch (error) {
      console.error('Error fetching health:', error);
    }
  };

  useEffect(() => {
    fetchSignals();
    fetchHealth();

    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchSignals();
        fetchHealth();
      }, 30000);

      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const handleAssetClick = (signal) => {
    setSelectedAsset(signal);
  };

  const handleRefresh = () => {
    fetchSignals();
    fetchHealth();
  };

  const filteredSignals = filter === 'ALL' 
    ? signals 
    : signals.filter(s => s.signal === filter);

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      <header className="border-b border-dark-border bg-dark-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Activity className="w-8 h-8 text-blue-500" />
              <div>
                <h1 className="text-2xl font-bold">ML Trading Dashboard</h1>
                <p className="text-sm text-gray-400">
                  Real-time predictions for {signals.length} stocks
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {health && (
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <span className="text-sm text-gray-400">
                    {health.models_loaded} models loaded
                  </span>
                </div>
              )}

              <button
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={`btn-secondary ${autoRefresh ? 'bg-blue-600' : ''}`}
              >
                Auto-refresh {autoRefresh ? 'ON' : 'OFF'}
              </button>

              <button
                onClick={handleRefresh}
                disabled={loading}
                className="btn-primary flex items-center space-x-2"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>
          </div>

          {lastUpdate && (
            <div className="mt-2 text-xs text-gray-500">
              Last updated: {lastUpdate.toLocaleTimeString()}
            </div>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading && signals.length === 0 ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-500" />
              <p className="text-gray-400">Loading signals...</p>
            </div>
          </div>
        ) : (
          <div className="space-y-8">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setFilter('ALL')}
                className={`px-4 py-2 rounded ${filter === 'ALL' ? 'bg-blue-600' : 'bg-dark-card'}`}
              >
                All ({signals.length})
              </button>
              <button
                onClick={() => setFilter('BUY')}
                className={`px-4 py-2 rounded ${filter === 'BUY' ? 'bg-green-600' : 'bg-dark-card'}`}
              >
                BUY ({signals.filter(s => s.signal === 'BUY').length})
              </button>
              <button
                onClick={() => setFilter('SELL')}
                className={`px-4 py-2 rounded ${filter === 'SELL' ? 'bg-red-600' : 'bg-dark-card'}`}
              >
                SELL ({signals.filter(s => s.signal === 'SELL').length})
              </button>
              <button
                onClick={() => setFilter('HOLD')}
                className={`px-4 py-2 rounded ${filter === 'HOLD' ? 'bg-yellow-600' : 'bg-dark-card'}`}
              >
                HOLD ({signals.filter(s => s.signal === 'HOLD').length})
              </button>
            </div>

            <section>
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2 text-blue-500" />
                Trading Signals
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                {filteredSignals.map((signal) => (
                  <AssetCard
                    key={signal.asset_symbol}
                    signal={signal}
                    isSelected={selectedAsset?.asset_symbol === signal.asset_symbol}
                    onClick={() => handleAssetClick(signal)}
                  />
                ))}
              </div>
            </section>

            {selectedAsset && (
              <>
                <section>
                  <h2 className="text-xl font-semibold mb-4 flex items-center">
                    <DollarSign className="w-5 h-5 mr-2 text-blue-500" />
                    {selectedAsset.asset_symbol} Analysis
                  </h2>
                  <PriceChart assetClass={selectedAsset.asset_symbol} />
                </section>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <TechnicalPanel indicators={selectedAsset.indicators} />
                  <SignalDashboard signal={selectedAsset} />
                </div>

                <ModelStatus assetClass={selectedAsset.asset_symbol} />
              </>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

function Navigation() {
  const location = useLocation();
  
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-dark-card border-t border-dark-border md:relative md:border-t-0">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-center md:justify-start space-x-2 py-3">
        <Link
          to="/"
          className={`flex items-center space-x-2 px-4 py-2 rounded transition ${
            location.pathname === '/'
              ? 'bg-blue-600 text-white'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <TrendingUp className="w-5 h-5" />
          <span>Dashboard</span>
        </Link>

        <Link
          to="/paper-trading"
          className={`flex items-center space-x-2 px-4 py-2 rounded transition ${
            location.pathname === '/paper-trading'
              ? 'bg-blue-600 text-white'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <BarChart3 className="w-5 h-5" />
          <span>Paper Trading</span>
        </Link>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="pb-20 md:pb-0">
        <Routes>
          <Route path="/" element={<DashboardContent />} />
          <Route path="/paper-trading" element={<PaperTradingPage />} />
        </Routes>
        <Navigation />
      </div>
    </Router>
  );
}

export default App;
