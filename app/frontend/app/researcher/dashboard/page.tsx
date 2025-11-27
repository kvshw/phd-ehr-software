/**
 * Researcher Dashboard
 * Displays analytics, logs, and model performance metrics
 */
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { researchService, MetricsSummary, SuggestionMetrics, NavigationMetrics, AdaptationMetrics, ModelPerformanceMetrics } from '@/lib/researchService';
import { MetricsCard } from '@/components/researcher/MetricsCard';
import { LogViewer } from '@/components/researcher/LogViewer';
import { TopHeader } from '@/components/layout/TopHeader';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function ResearcherDashboardPage() {
  const router = useRouter();
  const { isAuthenticated, user, checkAuth, isLoading: authLoading } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState(7); // days
  
  // Metrics state
  const [summary, setSummary] = useState<MetricsSummary | null>(null);
  const [suggestionMetrics, setSuggestionMetrics] = useState<SuggestionMetrics | null>(null);
  const [navigationMetrics, setNavigationMetrics] = useState<NavigationMetrics | null>(null);
  const [adaptationMetrics, setAdaptationMetrics] = useState<AdaptationMetrics | null>(null);
  const [modelMetrics, setModelMetrics] = useState<ModelPerformanceMetrics | null>(null);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    } else if (!authLoading && user && user.role !== 'researcher' && user.role !== 'admin') {
      router.push('/dashboard');
    } else if (isAuthenticated && (user?.role === 'researcher' || user?.role === 'admin')) {
      fetchMetrics();
    }
  }, [isAuthenticated, authLoading, user, router, timeRange]);

  const fetchMetrics = async () => {
    setLoading(true);
    setError(null);
    try {
      const [summaryData, suggestions, navigation, adaptations, models] = await Promise.all([
        researchService.getAuditSummary(timeRange),
        researchService.getSuggestionMetrics(timeRange),
        researchService.getNavigationMetrics(timeRange),
        researchService.getAdaptationMetrics(timeRange),
        researchService.getModelPerformanceMetrics(timeRange),
      ]);
      
      setSummary(summaryData);
      setSuggestionMetrics(suggestions);
      setNavigationMetrics(navigation);
      setAdaptationMetrics(adaptations);
      setModelMetrics(models);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load metrics');
      console.error('Error fetching metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const data = await researchService.exportResearchData(timeRange);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `research-data-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error exporting data:', err);
      alert('Failed to export data');
    }
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || (user?.role !== 'researcher' && user?.role !== 'admin')) {
    return null;
  }

  // Prepare chart data
  const sectionVisitData = navigationMetrics
    ? Object.entries(navigationMetrics.section_visits)
        .map(([section, visits]) => ({
          section: section.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
          visits,
        }))
        .sort((a, b) => b.visits - a.visits)
    : [];

  const suggestionActionData = suggestionMetrics
    ? [
        { name: 'Accepted', value: suggestionMetrics.accepted, color: '#10b981' },
        { name: 'Ignored', value: suggestionMetrics.ignored, color: '#6b7280' },
        { name: 'Not Relevant', value: suggestionMetrics.not_relevant, color: '#ef4444' },
      ]
    : [];

  const modelOutputData = modelMetrics
    ? Object.entries(modelMetrics.outputs_by_model).map(([model, count]) => ({
        model: model.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
        count,
      }))
    : [];

  return (
    <div className="min-h-screen bg-white">
      <TopHeader currentPage="Overview" />
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Researcher Dashboard</h1>
              <p className="mt-1 text-sm text-gray-600">
                Analytics, logs, and model performance metrics
              </p>
            </div>
            <div className="flex items-center gap-4">
              <select
                value={timeRange}
                onChange={(e) => {
                  setTimeRange(Number(e.target.value));
                  setLoading(true);
                }}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value={7}>Last 7 days</option>
                <option value={30}>Last 30 days</option>
                <option value={90}>Last 90 days</option>
              </select>
              <button
                onClick={handleExport}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                Export Data
              </button>
            </div>
          </div>

          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {/* Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <MetricsCard
              title="Total Events"
              value={summary?.total_events || 0}
              subtitle={`Last ${timeRange} days`}
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              }
            />
            <MetricsCard
              title="Suggestion Accept Rate"
              value={suggestionMetrics ? `${suggestionMetrics.accept_rate.toFixed(1)}%` : '0%'}
              subtitle={`${suggestionMetrics?.accepted || 0} of ${suggestionMetrics?.total || 0} accepted`}
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              }
            />
            <MetricsCard
              title="Total Adaptations"
              value={adaptationMetrics?.total_adaptations || 0}
              subtitle="UI layout changes"
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                </svg>
              }
            />
            <MetricsCard
              title="Model Outputs"
              value={modelMetrics?.total_outputs || 0}
              subtitle="AI model executions"
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              }
            />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Section Visits Chart */}
            <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Section Visits</h3>
              {sectionVisitData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={sectionVisitData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="section" angle={-45} textAnchor="end" height={100} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="visits" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center py-12 text-gray-500">No navigation data available</div>
              )}
            </div>

            {/* Suggestion Actions Chart */}
            <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Suggestion Actions</h3>
              {suggestionActionData.length > 0 && suggestionMetrics && suggestionMetrics.total > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={suggestionActionData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {suggestionActionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center py-12 text-gray-500">No suggestion data available</div>
              )}
            </div>

            {/* Model Outputs Chart */}
            <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Outputs by Type</h3>
              {modelOutputData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={modelOutputData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="model" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="count" fill="#10b981" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center py-12 text-gray-500">No model output data available</div>
              )}
            </div>

            {/* Adaptation Events Chart */}
            <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Adaptation Density Distribution</h3>
              {adaptationMetrics && Object.keys(adaptationMetrics.adaptations_by_type).length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart
                    data={Object.entries(adaptationMetrics.adaptations_by_type).map(([density, count]) => ({
                      density: density.charAt(0).toUpperCase() + density.slice(1),
                      count,
                    }))}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="density" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="count" fill="#8b5cf6" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center py-12 text-gray-500">No adaptation data available</div>
              )}
            </div>
          </div>

          {/* Log Viewer */}
          <LogViewer />

          {/* Fairness Indicators (Placeholder) */}
          <div className="mt-8 bg-white shadow rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Fairness Indicators</h3>
            <div className="text-center py-8 text-gray-500">
              <p>Fairness indicators will be implemented based on research requirements.</p>
              <p className="text-sm mt-2">
                This would include metrics on suggestion acceptance rates across different patient
                demographics, model performance across different groups, etc.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
