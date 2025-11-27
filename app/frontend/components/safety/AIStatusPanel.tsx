/**
 * AI Status Panel Component
 * Shows active AI models, their versions, and status
 */
'use client';

import { useState, useEffect } from 'react';

interface ModelInfo {
  type: string;
  name: string;
  version: string;
  status: 'active' | 'inactive' | 'unknown';
  endpoint: string;
}

export function AIStatusPanel() {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchModelStatus();
    // Refresh status every 30 seconds
    const interval = setInterval(fetchModelStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchModelStatus = async () => {
    try {
      setError(null);
      // For now, we'll use static model information
      // In production, this would call an API endpoint that checks model service health
      const modelInfo: ModelInfo[] = [
        {
          type: 'vital_risk',
          name: 'Vital Risk Assessment Model',
          version: '1.0.0',
          status: 'active',
          endpoint: '/api/v1/ai/vitals-risk',
        },
        {
          type: 'image_analysis',
          name: 'Image Analysis Model',
          version: '1.0.0',
          status: 'active',
          endpoint: '/api/v1/ai/image-analysis',
        },
        {
          type: 'diagnosis_helper',
          name: 'Diagnosis Helper Model',
          version: '1.0.0',
          status: 'active',
          endpoint: '/api/v1/ai/diagnosis-helper',
        },
      ];

      // Check health of each model service (simplified - would need actual health check endpoints)
      const checkedModels = await Promise.all(
        modelInfo.map(async (model) => {
          try {
            // In production, call health check endpoint for each service
            // For now, assume all are active
            return { ...model, status: 'active' as const };
          } catch {
            return { ...model, status: 'inactive' as const };
          }
        })
      );

      setModels(checkedModels);
    } catch (err: any) {
      setError('Failed to fetch AI model status');
      console.error('Error fetching model status:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'inactive':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active':
        return 'Active';
      case 'inactive':
        return 'Inactive';
      default:
        return 'Unknown';
    }
  };

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-4">
        <h3 className="text-lg font-semibold text-gray-900">AI Model Status</h3>
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          Experimental
        </span>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <div className="space-y-3">
        {models.map((model) => (
          <div
            key={model.type}
            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <h4 className="text-sm font-semibold text-gray-900">{model.name}</h4>
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${getStatusColor(
                      model.status
                    )}`}
                  >
                    {getStatusLabel(model.status)}
                  </span>
                </div>
                <div className="space-y-1 text-xs text-gray-600">
                  <div>
                    <span className="font-medium">Version:</span> {model.version}
                  </div>
                  <div>
                    <span className="font-medium">Type:</span>{' '}
                    {model.type.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Safety Notice */}
      <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex items-start gap-2">
          <svg
            className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          <div>
            <p className="text-sm font-medium text-yellow-800">
              All AI Models Are Experimental
            </p>
            <p className="text-xs text-yellow-700 mt-1">
              These AI models are for research purposes only. All outputs are experimental and
              should not be used as the sole basis for clinical decisions. Model versions and
              status are displayed for transparency.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

