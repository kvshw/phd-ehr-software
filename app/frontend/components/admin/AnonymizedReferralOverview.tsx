'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/apiClient';

interface ReferralStats {
  total_referrals: number;
  by_status: Record<string, number>;
  by_specialty: Record<string, number>;
  by_priority: Record<string, number>;
  avg_wait_time_minutes: number;
  nurse_override_rate: number;
}

interface AnonymizedReferral {
  id: string;
  patient_hash: string;  // Anonymized patient ID
  specialty: string;
  priority: string;
  status: string;
  ai_suggested: string | null;
  nurse_override: boolean;
  created_at: string;
  wait_time_bucket: string;
}

interface OverviewData {
  statistics: ReferralStats;
  referrals: AnonymizedReferral[];
  period_days: number;
}

const SPECIALTY_INFO: Record<string, { name: string; color: string }> = {
  cardiology: { name: 'Cardiology', color: 'bg-red-100 text-red-800' },
  neurology: { name: 'Neurology', color: 'bg-purple-100 text-purple-800' },
  orthopedics: { name: 'Orthopedics', color: 'bg-orange-100 text-orange-800' },
  pediatrics: { name: 'Pediatrics', color: 'bg-pink-100 text-pink-800' },
  psychiatry: { name: 'Psychiatry', color: 'bg-indigo-100 text-indigo-800' },
  emergency: { name: 'Emergency', color: 'bg-red-100 text-red-800' },
  internal: { name: 'Internal Medicine', color: 'bg-blue-100 text-blue-800' },
  surgery: { name: 'Surgery', color: 'bg-green-100 text-green-800' },
  general: { name: 'General', color: 'bg-gray-100 text-gray-800' },
};

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  accepted: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-indigo-100 text-indigo-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-gray-100 text-gray-800',
};

export function AnonymizedReferralOverview() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(7);
  const [activeTab, setActiveTab] = useState<'overview' | 'details'>('overview');

  useEffect(() => {
    fetchData();
  }, [days]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get(`/referrals/admin/overview?days=${days}`);
      setData(response.data.overview);
    } catch (error) {
      console.error('Error fetching admin overview:', error);
      // Demo data
      setData({
        statistics: {
          total_referrals: 47,
          by_status: { pending: 8, accepted: 12, in_progress: 5, completed: 22 },
          by_specialty: { cardiology: 15, neurology: 10, pediatrics: 8, orthopedics: 7, internal: 7 },
          by_priority: { critical: 3, urgent: 18, standard: 20, non_urgent: 6 },
          avg_wait_time_minutes: 14.3,
          nurse_override_rate: 18.5,
        },
        referrals: [
          { id: '1', patient_hash: 'a3f2b1c8', specialty: 'cardiology', priority: 'urgent', status: 'completed', ai_suggested: 'cardiology', nurse_override: false, created_at: new Date().toISOString(), wait_time_bucket: '5-15 min' },
          { id: '2', patient_hash: 'b7d4e2f9', specialty: 'neurology', priority: 'standard', status: 'accepted', ai_suggested: 'neurology', nurse_override: false, created_at: new Date().toISOString(), wait_time_bucket: '15-30 min' },
          { id: '3', patient_hash: 'c9a1b3d5', specialty: 'pediatrics', priority: 'urgent', status: 'pending', ai_suggested: 'internal', nurse_override: true, created_at: new Date().toISOString(), wait_time_bucket: 'pending' },
        ],
        period_days: days,
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
        <p className="mt-2 text-gray-500">Loading analytics...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6 text-center text-gray-500">
        No data available
      </div>
    );
  }

  const { statistics, referrals } = data;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold flex items-center gap-2">
              Anonymized Referral Analytics
            </h2>
            <p className="text-indigo-200 text-sm mt-1">
              Patient identities are hashed for privacy compliance
            </p>
          </div>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="bg-white/20 border border-white/30 rounded-lg px-3 py-2 text-white"
          >
            <option value={7} className="text-gray-900">Last 7 days</option>
            <option value={14} className="text-gray-900">Last 14 days</option>
            <option value={30} className="text-gray-900">Last 30 days</option>
          </select>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow p-4 border-l-4 border-indigo-500">
          <div className="text-3xl font-bold text-indigo-600">{statistics.total_referrals}</div>
          <div className="text-sm text-gray-600">Total Referrals</div>
        </div>
        <div className="bg-white rounded-xl shadow p-4 border-l-4 border-green-500">
          <div className="text-3xl font-bold text-green-600">{statistics.by_status.completed || 0}</div>
          <div className="text-sm text-gray-600">Completed</div>
        </div>
        <div className="bg-white rounded-xl shadow p-4 border-l-4 border-blue-500">
          <div className="text-3xl font-bold text-blue-600">{statistics.avg_wait_time_minutes.toFixed(1)} min</div>
          <div className="text-sm text-gray-600">Avg Wait Time</div>
        </div>
        <div className="bg-white rounded-xl shadow p-4 border-l-4 border-amber-500">
          <div className="text-3xl font-bold text-amber-600">{statistics.nurse_override_rate.toFixed(1)}%</div>
          <div className="text-sm text-gray-600">AI Override Rate</div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-xl shadow-sm border p-1 flex gap-1">
        <button
          onClick={() => setActiveTab('overview')}
          className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all ${
            activeTab === 'overview' ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          Statistics
        </button>
        <button
          onClick={() => setActiveTab('details')}
          className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all ${
            activeTab === 'details' ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          Anonymized Records
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-3 gap-6">
          {/* By Status */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="font-semibold text-gray-900 mb-4">By Status</h3>
            <div className="space-y-3">
              {Object.entries(statistics.by_status).map(([status, count]) => (
                <div key={status} className="flex items-center justify-between">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[status] || 'bg-gray-100'}`}>
                    {status}
                  </span>
                  <span className="font-semibold text-gray-900">{count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* By Specialty */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="font-semibold text-gray-900 mb-4">By Specialty</h3>
            <div className="space-y-3">
              {Object.entries(statistics.by_specialty).slice(0, 5).map(([spec, count]) => (
                <div key={spec} className="flex items-center justify-between">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${SPECIALTY_INFO[spec]?.color || 'bg-gray-100'}`}>
                    {SPECIALTY_INFO[spec]?.name || spec}
                  </span>
                  <span className="font-semibold text-gray-900">{count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* By Priority */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="font-semibold text-gray-900 mb-4">By Priority</h3>
            <div className="space-y-3">
              {Object.entries(statistics.by_priority).map(([priority, count]) => (
                <div key={priority} className="flex items-center justify-between">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${
                    priority === 'critical' ? 'bg-red-500 text-white' :
                    priority === 'urgent' ? 'bg-orange-500 text-white' :
                    priority === 'standard' ? 'bg-yellow-500 text-white' :
                    'bg-green-500 text-white'
                  }`}>
                    {priority.replace('_', ' ').toUpperCase()}
                  </span>
                  <span className="font-semibold text-gray-900">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Details Tab - Anonymized Records */}
      {activeTab === 'details' && (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="bg-gray-50 px-6 py-3 border-b flex items-center gap-2">
            <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            <span className="text-sm text-gray-600">
              Patient IDs are hashed. No personal information is displayed.
            </span>
          </div>
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Patient Hash</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Specialty</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">AI Override</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Wait Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {referrals.map((ref) => (
                <tr key={ref.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <code className="text-xs bg-gray-100 px-2 py-1 rounded font-mono">
                      {ref.patient_hash}
                    </code>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${SPECIALTY_INFO[ref.specialty]?.color || 'bg-gray-100'}`}>
                      {SPECIALTY_INFO[ref.specialty]?.name || ref.specialty}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      ref.priority === 'critical' ? 'bg-red-500 text-white' :
                      ref.priority === 'urgent' ? 'bg-orange-500 text-white' :
                      ref.priority === 'standard' ? 'bg-yellow-500 text-white' :
                      'bg-green-500 text-white'
                    }`}>
                      {ref.priority.replace('_', ' ').toUpperCase()}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[ref.status] || 'bg-gray-100'}`}>
                      {ref.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {ref.nurse_override ? (
                      <span className="text-amber-600 text-xs font-medium">Yes</span>
                    ) : (
                      <span className="text-green-600 text-xs">No</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {ref.wait_time_bucket}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

