/**
 * Adaptation Configuration Component
 * Allows admins to configure MAPE-K adaptation rules
 */
'use client';

import { useState, useEffect } from 'react';
import { adminService, AdaptationConfig } from '@/lib/adminService';

export function AdaptationConfigPanel() {
  const [config, setConfig] = useState<AdaptationConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminService.getAdaptationConfig();
      setConfig(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load configuration');
      console.error('Error fetching config:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!config) return;

    setSaving(true);
    setError(null);
    setSuccess(false);

    try {
      await adminService.updateAdaptationConfig(config);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save configuration');
      console.error('Error saving config:', err);
    } finally {
      setSaving(false);
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

  if (!config) {
    return (
      <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
        <p className="text-gray-500">Configuration not available</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Adaptation Configuration</h3>
      <p className="text-sm text-gray-600 mb-6">
        Configure thresholds and rules for the MAPE-K adaptation engine.
      </p>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm text-green-800">Configuration saved successfully!</p>
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Navigation Threshold
          </label>
          <input
            type="number"
            min="1"
            max="100"
            step="1"
            value={config.navigation_threshold}
            onChange={(e) =>
              setConfig({ ...config, navigation_threshold: parseFloat(e.target.value) })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
          <p className="text-xs text-gray-500 mt-1">
            Minimum visits to consider a section frequently visited
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Ignore Rate Threshold
          </label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.1"
            value={config.ignore_rate_threshold}
            onChange={(e) =>
              setConfig({ ...config, ignore_rate_threshold: parseFloat(e.target.value) })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
          <p className="text-xs text-gray-500 mt-1">
            If ignore rate exceeds this, reduce suggestion density (0.0-1.0)
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Acceptance Rate Threshold
          </label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.1"
            value={config.acceptance_rate_threshold}
            onChange={(e) =>
              setConfig({ ...config, acceptance_rate_threshold: parseFloat(e.target.value) })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
          <p className="text-xs text-gray-500 mt-1">
            If acceptance rate exceeds this, maintain or increase density (0.0-1.0)
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Risk Escalation Threshold
          </label>
          <input
            type="number"
            min="0"
            max="10"
            step="1"
            value={config.risk_escalation_threshold}
            onChange={(e) =>
              setConfig({ ...config, risk_escalation_threshold: parseFloat(e.target.value) })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
          <p className="text-xs text-gray-500 mt-1">
            If risk escalations exceed this, prioritize monitoring sections
          </p>
        </div>
      </div>

      <div className="mt-6">
        <button
          onClick={handleSave}
          disabled={saving}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            saving
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-700'
          } text-white`}
        >
          {saving ? 'Saving...' : 'Save Configuration'}
        </button>
      </div>
    </div>
  );
}

