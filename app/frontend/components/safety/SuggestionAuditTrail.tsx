/**
 * Suggestion Audit Trail Component
 * Allows clinicians to view the history of AI suggestions and user interactions
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
  metadata: {
    suggestion_type?: string;
    source?: string;
    confidence?: number;
    text_preview?: string;
    action?: string;
    suggestion_id?: string;
  };
}

interface AuditLogResponse {
  items: AuditLogEntry[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

interface SuggestionAuditTrailProps {
  patientId: string;
}

export function SuggestionAuditTrail({ patientId }: SuggestionAuditTrailProps) {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchAuditTrail();
  }, [patientId, page]);

  const fetchAuditTrail = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<AuditLogResponse>(
        `/audit/suggestions?patient_id=${patientId}&page=${page}&page_size=20`
      );
      setLogs(response.data.items);
      setTotalPages(response.data.total_pages);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load audit trail');
      console.error('Error fetching audit trail:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getActionColor = (action?: string) => {
    switch (action) {
      case 'accept':
        return 'bg-green-100 text-green-800';
      case 'ignore':
        return 'bg-gray-100 text-gray-800';
      case 'not_relevant':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-blue-100 text-blue-800';
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
        <h3 className="text-lg font-semibold text-gray-900">Suggestion Audit Trail</h3>
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          Research Only
        </span>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {logs.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No audit trail entries found for this patient.</p>
        </div>
      ) : (
        <>
          <div className="space-y-3 mb-4">
            {logs.map((log) => (
              <div
                key={log.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs font-medium text-gray-500">
                        {log.type === 'suggestion' ? 'Suggestion Created' : 'User Interaction'}
                      </span>
                      {log.metadata.action && (
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getActionColor(
                            log.metadata.action
                          )}`}
                        >
                          {log.metadata.action.charAt(0).toUpperCase() + log.metadata.action.slice(1)}
                        </span>
                      )}
                    </div>
                    {log.metadata.text_preview && (
                      <p className="text-sm text-gray-700 mb-2">{log.metadata.text_preview}</p>
                    )}
                    <div className="flex flex-wrap gap-4 text-xs text-gray-600">
                      {log.metadata.source && (
                        <span>
                          <span className="font-medium">Source:</span>{' '}
                          {log.metadata.source.replace('_', ' ')}
                        </span>
                      )}
                      {log.metadata.confidence !== undefined && (
                        <span>
                          <span className="font-medium">Confidence:</span>{' '}
                          {(log.metadata.confidence * 100).toFixed(0)}%
                        </span>
                      )}
                      <span>
                        <span className="font-medium">Time:</span> {formatTimestamp(log.timestamp)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between border-t border-gray-200 pt-4">
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

      {/* Privacy Notice */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start gap-2">
          <svg
            className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
              clipRule="evenodd"
            />
          </svg>
          <div>
            <p className="text-sm font-medium text-blue-800">Audit Trail Privacy</p>
            <p className="text-xs text-blue-700 mt-1">
              This audit trail is for research and transparency purposes only. All patient
              identifiers have been removed or anonymized. No PHI is stored in audit logs.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

