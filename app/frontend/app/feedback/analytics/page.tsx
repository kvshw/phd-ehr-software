'use client';

/**
 * Feedback Analytics Page
 * 
 * Shows how clinicians interact with AI suggestions and how the AI learns from feedback.
 * Includes:
 * - Acceptance/rejection rates over time
 * - Learning events (self-adaptive AI)
 * - Confidence adjustments
 * - Detailed feedback history
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { TopHeader } from '@/components/layout/TopHeader';
import { apiClient } from '@/lib/apiClient';

interface FeedbackStats {
  total_feedback: number;
  acceptance_rate: number;
  actions: Record<string, number>;
  by_source: Record<string, number>;
  avg_ratings: Record<string, number>;
  learning_ready: boolean;
  period_days: number;
}

interface TimelinePoint {
  period: string;
  total: number;
  accepted: number;
  ignored: number;
  not_relevant: number;
  acceptance_rate: number;
}

interface LearningEvent {
  id: string;
  event_type: string;
  affected_source: string;
  affected_rule_id: string | null;
  previous_value: any;
  new_value: any;
  trigger_reason: string;
  feedback_count_used: number;
  created_at: string;
  is_active: boolean;
}

interface ConfidenceAdjustment {
  adjustment: number;
  description: string;
}

export default function FeedbackAnalyticsPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, checkAuth } = useAuthStore();
  
  const [stats, setStats] = useState<FeedbackStats | null>(null);
  const [timeline, setTimeline] = useState<TimelinePoint[]>([]);
  const [learningEvents, setLearningEvents] = useState<LearningEvent[]>([]);
  const [confidenceAdjustments, setConfidenceAdjustments] = useState<Record<string, ConfidenceAdjustment>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDays, setSelectedDays] = useState(30);
  const [authChecked, setAuthChecked] = useState(false);

  // Check auth on mount
  useEffect(() => {
    const verifyAuth = async () => {
      await checkAuth();
      setAuthChecked(true);
    };
    verifyAuth();
  }, [checkAuth]);

  // Fetch data when authenticated and has access
  useEffect(() => {
    // Wait for auth check to complete
    if (!authChecked || isLoading) return;
    
    const role = user?.role?.toLowerCase();
    const hasAccess = role === 'researcher' || role === 'admin';
    
    console.log('Auth check:', { isAuthenticated, role, hasAccess, user });
    
    if (isAuthenticated && hasAccess) {
      fetchData();
    }
  }, [isAuthenticated, user, selectedDays, isLoading, authChecked]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsRes, timelineRes, eventsRes, adjustmentsRes] = await Promise.all([
        apiClient.get(`/feedback/stats?days=${selectedDays}`).catch(err => {
          if (err.response?.status === 500 || err.code === 'ERR_NETWORK') {
            throw new Error('Database tables may not be created. Please run the SQL migration in Supabase.');
          }
          throw err;
        }),
        apiClient.get(`/feedback/timeline?days=${selectedDays}`).catch(() => ({ data: [] })),
        apiClient.get('/feedback/learning-events?limit=20').catch(() => ({ data: [] })),
        apiClient.get('/feedback/confidence-adjustments').catch(() => ({ data: {} })),
      ]);
      
      setStats(statsRes.data);
      setTimeline(timelineRes.data || []);
      setLearningEvents(eventsRes.data || []);
      setConfidenceAdjustments(adjustmentsRes.data || {});
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load analytics';
      setError(errorMessage);
      console.error('Error fetching feedback analytics:', err);
      
      // If it's a database error, show helpful message
      if (errorMessage.includes('relation') || errorMessage.includes('table') || errorMessage.includes('does not exist')) {
        setError('Database tables not found. Please run the SQL migration script in Supabase SQL Editor: scripts/create_feedback_tables.sql');
      }
    } finally {
      setLoading(false);
    }
  };

  // Show loading while checking auth
  if (isLoading || !authChecked) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // Check if user has admin or researcher role (case-insensitive)
  const role = user?.role?.toLowerCase();
  const hasAccess = role === 'researcher' || role === 'admin';

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Not Authenticated</h2>
          <p className="text-gray-600">Please log in to access this page.</p>
          <button 
            onClick={() => router.push('/login')}
            className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  if (!hasAccess) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600">This page is only available to researchers and admins.</p>
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-700 mb-2">Debug Info:</p>
            <p className="text-xs text-gray-600">Current role: <strong>{user?.role || 'Unknown'}</strong></p>
            <p className="text-xs text-gray-600">User ID: {user?.id || 'N/A'}</p>
            <p className="text-xs text-gray-600">Email: {user?.email || 'N/A'}</p>
          </div>
          <div className="mt-4 flex gap-3 justify-center">
            <button 
              onClick={() => router.push('/dashboard')}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              Go to Dashboard
            </button>
            <button 
              onClick={() => router.push('/login')}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Re-login
            </button>
          </div>
        </div>
      </div>
    );
  }

  const getActionColor = (action: string) => {
    switch (action) {
      case 'accept': return 'bg-green-100 text-green-800';
      case 'ignore': return 'bg-yellow-100 text-yellow-800';
      case 'not_relevant': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSourceColor = (source: string) => {
    switch (source) {
      case 'rules': return 'bg-gray-100 text-gray-800';
      case 'ai_model': return 'bg-green-100 text-green-800';
      case 'hybrid': return 'bg-orange-100 text-orange-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  const getSourceDisplayName = (source: string): string => {
    // Professional labels for PhD/research context
    const sourceLabels: Record<string, string> = {
      'rules': 'Rule-Based System',
      'ai_model': 'Machine Learning Model',
      'hybrid': 'Hybrid System',
      'vital_risk': 'Vital Risk Predictor',
      'image_analysis': 'Image Analysis Model',
      'diagnosis_helper': 'Diagnosis Assistant',
    };
    return sourceLabels[source] || source.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className="min-h-screen bg-white">
      <TopHeader currentPage="Research" />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4">
            <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-indigo-100">
              <svg className="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Feedback Analytics</h1>
              <p className="mt-1 text-gray-600">
                How clinicians interact with AI suggestions and how the AI learns
              </p>
            </div>
          </div>
          
          {/* Period Selector */}
          <div className="mt-4 flex gap-2">
            {[7, 14, 30, 90].map((days) => (
              <button
                key={days}
                onClick={() => setSelectedDays(days)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedDays === days
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Last {days} days
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-red-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">
                <h3 className="font-semibold text-red-900 mb-2">Error Loading Analytics</h3>
                <p className="text-red-800 mb-3">{error}</p>
                {error.includes('Database tables') && (
                  <div className="bg-white border border-red-200 rounded p-4 mt-3">
                    <p className="text-sm text-red-900 font-medium mb-2">To fix this:</p>
                    <ol className="text-sm text-red-800 list-decimal list-inside space-y-1">
                      <li>Go to Supabase Dashboard → SQL Editor</li>
                      <li>Open the file: <code className="bg-red-50 px-1 rounded">scripts/create_feedback_tables.sql</code></li>
                      <li>Copy and paste the SQL into the editor</li>
                      <li>Click "Run" to create the tables</li>
                      <li>Refresh this page</li>
                    </ol>
                  </div>
                )}
                {error.includes('CORS') && (
                  <div className="bg-white border border-red-200 rounded p-4 mt-3">
                    <p className="text-sm text-red-900 font-medium mb-2">CORS Error:</p>
                    <p className="text-sm text-red-800">The backend may not be running or CORS is misconfigured. Try restarting the backend.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading analytics...</p>
          </div>
        ) : stats ? (
          <div className="space-y-8">
            {/* Overview Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white border border-gray-200 rounded-xl shadow p-6">
                <div className="text-sm text-gray-500 mb-1">Total Feedback</div>
                <div className="text-3xl font-bold text-gray-900">{stats.total_feedback}</div>
                <div className="text-xs text-gray-400 mt-1">Last {selectedDays} days</div>
              </div>
              
              <div className="bg-white border border-gray-200 rounded-xl shadow p-6">
                <div className="text-sm text-gray-500 mb-1">Acceptance Rate</div>
                <div className={`text-3xl font-bold ${
                  stats.acceptance_rate >= 0.7 ? 'text-green-600' :
                  stats.acceptance_rate >= 0.4 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {(stats.acceptance_rate * 100).toFixed(1)}%
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {stats.acceptance_rate >= 0.7 ? 'Excellent' :
                   stats.acceptance_rate >= 0.4 ? 'Good' : 'Needs improvement'}
                </div>
              </div>
              
              <div className="bg-white border border-gray-200 rounded-xl shadow p-6">
                <div className="text-sm text-gray-500 mb-1">Learning Status</div>
                <div className={`text-3xl font-bold ${stats.learning_ready ? 'text-green-600' : 'text-gray-400'}`}>
                  {stats.learning_ready ? '✓ Ready' : '⏳ Pending'}
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {stats.learning_ready ? 'AI can adapt' : 'Need more feedback'}
                </div>
              </div>
              
              <div className="bg-white border border-gray-200 rounded-xl shadow p-6">
                <div className="text-sm text-gray-500 mb-1">Avg Rating</div>
                <div className="text-3xl font-bold text-gray-900">
                  {stats.avg_ratings?.clinical_relevance?.toFixed(1) || 'N/A'}
                </div>
                <div className="text-xs text-gray-400 mt-1">Clinical relevance (1-5)</div>
              </div>
            </div>

            {/* Actions Breakdown */}
            <div className="bg-white border border-gray-200 rounded-xl shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Feedback Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(stats.actions).map(([action, count]) => (
                  <div key={action} className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getActionColor(action)}`}>
                      {action.replace('_', ' ')}
                    </span>
                    <span className="text-2xl font-bold text-gray-900">{count}</span>
                    <span className="text-sm text-gray-500">
                      ({((count / stats.total_feedback) * 100).toFixed(1)}%)
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* By Source */}
            <div className="bg-white border border-gray-200 rounded-xl shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Feedback by Suggestion Source</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(stats.by_source).map(([source, count]) => (
                  <div key={source} className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSourceColor(source)}`}>
                      {getSourceDisplayName(source)}
                    </span>
                    <span className="text-2xl font-bold text-gray-900">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Timeline Chart */}
            {timeline.length > 0 && (
              <div className="bg-white border border-gray-200 rounded-xl shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Feedback Timeline</h2>
                <div className="overflow-x-auto">
                  <div className="flex items-end gap-2 h-48 min-w-[600px]">
                    {timeline.map((point, i) => {
                      const maxTotal = Math.max(...timeline.map(t => t.total));
                      const height = (point.total / maxTotal) * 100;
                      const acceptedHeight = (point.accepted / point.total) * height;
                      
                      return (
                        <div key={i} className="flex-1 flex flex-col items-center">
                          <div 
                            className="w-full relative rounded-t"
                            style={{ height: `${height}%` }}
                          >
                            {/* Accepted portion */}
                            <div 
                              className="absolute bottom-0 left-0 right-0 bg-green-500 rounded-t"
                              style={{ height: `${(point.accepted / point.total) * 100}%` }}
                            />
                            {/* Other portion */}
                            <div className="absolute inset-0 bg-gray-300 rounded-t opacity-50" />
                          </div>
                          <div className="text-xs text-gray-500 mt-2 text-center truncate w-full">
                            {point.period.split('-').slice(1).join('/')}
                          </div>
                          <div className="text-xs text-gray-400">{point.total}</div>
                        </div>
                      );
                    })}
                  </div>
                  <div className="flex items-center gap-4 mt-4 justify-center">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-green-500 rounded"></div>
                      <span className="text-sm text-gray-600">Accepted</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-gray-300 rounded"></div>
                      <span className="text-sm text-gray-600">Other</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Confidence Adjustments */}
            <div className="bg-white border border-gray-200 rounded-xl shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Self-Adaptive AI: Confidence Adjustments</h2>
              <p className="text-sm text-gray-600 mb-4">
                Based on clinician feedback, the AI automatically adjusts its confidence levels.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(confidenceAdjustments).map(([source, data]) => (
                  <div key={source} className={`border rounded-lg p-4 ${
                    data.adjustment > 0 ? 'border-green-200 bg-green-50' :
                    data.adjustment < 0 ? 'border-red-200 bg-red-50' :
                    'border-gray-200 bg-gray-50'
                  }`}>
                    <div className="font-medium text-gray-900 mb-1">
                      {getSourceDisplayName(source)}
                    </div>
                    <div className={`text-2xl font-bold ${
                      data.adjustment > 0 ? 'text-green-600' :
                      data.adjustment < 0 ? 'text-red-600' :
                      'text-gray-500'
                    }`}>
                      {data.adjustment > 0 ? '+' : ''}{(data.adjustment * 100).toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-600">{data.description}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Learning Events */}
            <div className="bg-white border border-gray-200 rounded-xl shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Learning Events History</h2>
              <p className="text-sm text-gray-600 mb-4">
                When the AI learns and adapts based on clinician feedback.
              </p>
              
              {learningEvents.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>No learning events yet.</p>
                  <p className="text-sm mt-2">The AI will start learning once enough feedback is collected.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {learningEvents.map((event) => (
                    <div key={event.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              event.event_type === 'confidence_adjustment' ? 'bg-blue-100 text-blue-800' :
                              'bg-purple-100 text-purple-800'
                            }`}>
                              {event.event_type.replace('_', ' ')}
                            </span>
                            <span className={`px-2 py-1 rounded text-xs font-medium ${getSourceColor(event.affected_source)}`}>
                              {getSourceDisplayName(event.affected_source)}
                            </span>
                            {event.is_active ? (
                              <span className="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">Active</span>
                            ) : (
                              <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">Inactive</span>
                            )}
                          </div>
                          <p className="mt-2 text-sm text-gray-700">{event.trigger_reason}</p>
                          <p className="mt-1 text-xs text-gray-500">
                            Based on {event.feedback_count_used} feedback items
                          </p>
                        </div>
                        <div className="text-right text-xs text-gray-500">
                          {new Date(event.created_at).toLocaleString()}
                        </div>
                      </div>
                      {event.new_value && (
                        <div className="mt-3 pt-3 border-t border-gray-100">
                          <span className="text-xs text-gray-500">Adjustment: </span>
                          <span className={`text-sm font-medium ${
                            (event.new_value.adjustment || 0) > 0 ? 'text-green-600' :
                            (event.new_value.adjustment || 0) < 0 ? 'text-red-600' : 'text-gray-600'
                          }`}>
                            {(event.new_value.adjustment || 0) > 0 ? '+' : ''}
                            {((event.new_value.adjustment || 0) * 100).toFixed(1)}% confidence
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Export Section */}
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Export Data</h2>
              <p className="text-sm text-gray-600 mb-4">
                Export feedback data for academic analysis.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    const data = { stats, timeline, learningEvents, confidenceAdjustments };
                    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `feedback-analytics-${new Date().toISOString().split('T')[0]}.json`;
                    a.click();
                  }}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  Export as JSON
                </button>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

