/**
 * System Status Component
 * Displays system health and model service status
 */
'use client';

import { useState, useEffect } from 'react';
import { adminService, SystemStatus } from '@/lib/adminService';

export function SystemStatusPanel() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      setError(null);
      const data = await adminService.getSystemStatus();
      setStatus(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load system status');
      console.error('Error fetching system status:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    return status === 'healthy' || status === 'active' || status === 'connected'
      ? 'bg-green-100 text-green-800'
      : 'bg-red-100 text-red-800';
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
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">System Status</h3>
        <button
          onClick={fetchStatus}
          className="text-sm text-indigo-600 hover:text-indigo-800"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {status && (
        <div className="space-y-4">
          {/* Backend Status */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900">Backend API</h4>
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                  status.backend.status
                )}`}
              >
                {status.backend.status}
              </span>
            </div>
            <p className="text-sm text-gray-600">Version: {status.backend.version}</p>
          </div>

          {/* Database Status */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900">Database</h4>
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                  status.database.status
                )}`}
              >
                {status.database.status}
              </span>
            </div>
          </div>

          {/* Model Services */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-3">AI Model Services</h4>
            <div className="space-y-2">
              {Object.entries(status.model_services).map(([service, info]) => (
                <div key={service} className="flex items-center justify-between">
                  <span className="text-sm text-gray-700 capitalize">
                    {service.replace('_', ' ')}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">v{info.version}</span>
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(
                        info.status
                      )}`}
                    >
                      {info.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

