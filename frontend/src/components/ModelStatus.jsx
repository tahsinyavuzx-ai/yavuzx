import React, { useState, useEffect } from 'react';
import { Database, Clock, CheckCircle } from 'lucide-react';
import { predictionAPI } from '../services/api';

const ModelStatus = ({ assetClass }) => {
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchModelInfo = async () => {
      setLoading(true);
      try {
        const response = await predictionAPI.getModelInfo(assetClass);
        setModelInfo(response.data);
      } catch (error) {
        console.error('Error fetching model info:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchModelInfo();
  }, [assetClass]);

  if (loading) {
    return (
      <div className="card">
        <p className="text-gray-400">Loading model information...</p>
      </div>
    );
  }

  if (!modelInfo) {
    return (
      <div className="card">
        <p className="text-gray-400">Model information not available</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4 flex items-center">
        <Database className="w-5 h-5 mr-2 text-blue-500" />
        Model Information
      </h3>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Model Version */}
        <div className="p-4 bg-dark-bg rounded-lg border border-dark-border">
          <div className="flex items-center mb-2">
            <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
            <span className="text-xs text-gray-400">Version</span>
          </div>
          <p className="text-lg font-bold">{modelInfo.version}</p>
        </div>

        {/* Accuracy */}
        <div className="p-4 bg-dark-bg rounded-lg border border-dark-border">
          <p className="text-xs text-gray-400 mb-2">Accuracy</p>
          <p className="text-lg font-bold text-green-500">
            {(modelInfo.accuracy * 100).toFixed(1)}%
          </p>
          <div className="w-full bg-dark-border rounded-full h-1 mt-2">
            <div
              className="h-1 rounded-full bg-green-500"
              style={{ width: `${modelInfo.accuracy * 100}%` }}
            />
          </div>
        </div>

        {/* Training Samples */}
        <div className="p-4 bg-dark-bg rounded-lg border border-dark-border">
          <p className="text-xs text-gray-400 mb-2">Training Samples</p>
          <p className="text-lg font-bold">
            {modelInfo.total_samples.toLocaleString()}
          </p>
        </div>

        {/* Last Updated */}
        <div className="p-4 bg-dark-bg rounded-lg border border-dark-border">
          <div className="flex items-center mb-2">
            <Clock className="w-4 h-4 text-blue-500 mr-2" />
            <span className="text-xs text-gray-400">Last Updated</span>
          </div>
          <p className="text-sm font-medium">
            {new Date(modelInfo.last_updated).toLocaleDateString()}
          </p>
        </div>
      </div>

      {/* Status Badge */}
      <div className="mt-4 flex items-center">
        <div className={`w-2 h-2 rounded-full mr-2 ${
          modelInfo.is_loaded ? 'bg-green-500' : 'bg-red-500'
        }`} />
        <span className="text-sm text-gray-400">
          {modelInfo.is_loaded ? 'Model Loaded' : 'Model Not Loaded'}
        </span>
      </div>
    </div>
  );
};

export default ModelStatus;
