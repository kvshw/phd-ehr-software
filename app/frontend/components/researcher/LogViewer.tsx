/**
 * Log Viewer Component
 * Displays audit logs with filtering and search
 */
'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/apiClient';

interface AuditLogEntry {
  id: string;
  type: string;
  timestamp: string;
  user_id?: string;
  patient_id?: string;
  category: string;
  metadata: Record<string, any>;
}

interface AuditLogResponse {
  items: AuditLogEntry[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export function LogViewer() {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [actionTypeFilter, setActionTypeFilter] = useState<string>('all');

  useEffect(() => {
    fetchLogs();
  }, [page, categoryFilter, actionTypeFilter]);

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const params: any = {
        page,
        page_size: 50,
      };
      
      if (categoryFilter !== 'all') {
        params.category = categoryFilter;
      }
      
      if (actionTypeFilter !== 'all') {
        params.action_type = actionTypeFilter;
      }
      
      const response = await apiClient.get<AuditLogResponse>('/audit/logs', { params });
      setLogs(response.data.items);
      setTotalPages(response.data.total_pages);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load logs');
      console.error('Error fetching logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      user_navigation: 'bg-blue-100 text-blue-800',
      user_interaction: 'bg-green-100 text-green-800',
      system_event: 'bg-purple-100 text-purple-800',
      ai_activity: 'bg-yellow-100 text-yellow-800',
      ai_suggestion: 'bg-indigo-100 text-indigo-800',
      system_adaptation: 'bg-pink-100 text-pink-800',
      other: 'bg-gray-100 text-gray-800',
    };
    return colors[category] || colors.other;
  };

  const filteredLogs = logs.filter((log) => {
    if (!searchTerm) return true;
    const searchLower = searchTerm.toLowerCase();
    return (
      log.type.toLowerCase().includes(searchLower) ||
      log.category.toLowerCase().includes(searchLower) ||
      JSON.stringify(log.metadata).toLowerCase().includes(searchLower)
    );
  });

  return (
    <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Audit Logs</h3>
        <button
          onClick={fetchLogs}
          className="text-sm text-indigo-600 hover:text-indigo-800"
        >
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Search
          </label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search logs..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Category
          </label>
          <select
            value={categoryFilter}
            onChange={(e) => {
              setCategoryFilter(e.target.value);
              setPage(1);
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">All Categories</option>
            <option value="user_navigation">User Navigation</option>
            <option value="user_interaction">User Interaction</option>
            <option value="system_event">System Events</option>
            <option value="ai_activity">AI Activity</option>
            <option value="ai_suggestion">AI Suggestions</option>
            <option value="system_adaptation">System Adaptations</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Action Type
          </label>
          <select
            value={actionTypeFilter}
            onChange={(e) => {
              setActionTypeFilter(e.target.value);
              setPage(1);
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">All Types</option>
            <option value="navigation">Navigation</option>
            <option value="suggestion_action">Suggestion Actions</option>
            <option value="risk_change">Risk Changes</option>
            <option value="model_output">Model Outputs</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Details
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredLogs.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-6 py-12 text-center text-gray-500">
                      No logs found
                    </td>
                  </tr>
                ) : (
                  filteredLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatTimestamp(log.timestamp)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {log.type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getCategoryColor(
                            log.category
                          )}`}
                        >
                          {log.category.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        <div className="max-w-md truncate">
                          {JSON.stringify(log.metadata).substring(0, 100)}
                          {JSON.stringify(log.metadata).length > 100 && '...'}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between border-t border-gray-200 pt-4 mt-4">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="text-sm text-gray-700">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

