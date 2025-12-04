/**
 * Research Analytics Page
 * Displays MAPE-K effectiveness metrics and user behavior analytics
 * Enhanced with Phase 8 metrics and A/B testing dashboards
 */
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { TopHeader } from '@/components/layout/TopHeader';
import { ResearchAnalyticsDashboard } from '@/components/research/ResearchAnalyticsDashboard';
import { MetricsDashboard } from '@/components/research/MetricsDashboard';
import RegretAnalysisChart from '@/components/research/RegretAnalysisChart';

export default function ResearchPage() {
  const { user, isAuthenticated, isLoading, checkAuth } = useAuthStore();
  const router = useRouter();
  const [activeView, setActiveView] = useState<'analytics' | 'metrics' | 'regret'>('analytics');

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <TopHeader currentPage="Analytics" />
      
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Research Analytics</h1>
          <p className="text-gray-600 mt-2">
            Track MAPE-K adaptation effectiveness and analyze user behavior patterns for research evaluation.
          </p>
        </div>

        {/* View Toggle */}
        <div className="mb-6 flex gap-2 flex-wrap">
          <button
            onClick={() => setActiveView('analytics')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeView === 'analytics'
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
            }`}
          >
            Analytics Overview
          </button>
          <button
            onClick={() => setActiveView('regret')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeView === 'regret'
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
            }`}
          >
            Regret Analysis
          </button>
          <button
            onClick={() => setActiveView('metrics')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeView === 'metrics'
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
            }`}
          >
            Detailed Metrics & A/B Studies
          </button>
        </div>

        {/* Quick Stats Banner */}
        <div className="mb-8 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold mb-2">Research Dashboard</h2>
              <p className="text-indigo-100 text-sm">
                Comprehensive metrics for your self-adaptive AI-assisted EHR research.
                All data is anonymized and GDPR-compliant.
              </p>
            </div>
            <div className="hidden md:flex items-center gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold">MAPE-K</div>
                <div className="text-xs text-indigo-200">Architecture</div>
              </div>
              <div className="h-12 w-px bg-indigo-400"></div>
              <div className="text-center">
                <div className="text-3xl font-bold">XAI</div>
                <div className="text-xs text-indigo-200">Explainable AI</div>
              </div>
              <div className="h-12 w-px bg-indigo-400"></div>
              <div className="text-center">
                <div className="text-3xl font-bold">FI</div>
                <div className="text-xs text-indigo-200">Finnish EHR</div>
              </div>
            </div>
          </div>
        </div>

        {/* Dashboard Content */}
        {activeView === 'analytics' && <ResearchAnalyticsDashboard />}
        
        {activeView === 'regret' && (
          <div className="space-y-6">
            <RegretAnalysisChart />
            
            {/* Regret Analysis Info */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Understanding Regret Analysis</h3>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-800 mb-2">What is Regret?</h4>
                  <p className="text-sm text-gray-600">
                    <strong>Instantaneous Regret:</strong> The difference between the optimal action's reward and 
                    the chosen action's reward at each step: r<sub>t</sub> = μ* - μ<sub>chosen</sub>
                  </p>
                  <p className="text-sm text-gray-600 mt-2">
                    <strong>Cumulative Regret:</strong> The sum of all instantaneous regrets over time: 
                    R<sub>T</sub> = Σ r<sub>t</sub>
                  </p>
                </div>
                <div>
                  <h4 className="font-medium text-gray-800 mb-2">Why It Matters</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>✓ Measures algorithm's learning efficiency</li>
                    <li>✓ Compares to theoretical O(√KT log T) bound</li>
                    <li>✓ Detects convergence to optimal policy</li>
                    <li>✓ Essential for academic publications</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {activeView === 'metrics' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <MetricsDashboard />
          </div>
        )}

        {/* Research Info Footer */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <h3 className="font-semibold text-gray-900 mb-3">MAPE-K Adaptations</h3>
            <p className="text-sm text-gray-600">
              Monitor → Analyze → Plan → Execute → Knowledge loop continuously
              adapts the UI based on clinician behavior patterns.
            </p>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <h3 className="font-semibold text-gray-900 mb-3">Explainable AI</h3>
            <p className="text-sm text-gray-600">
              Every AI suggestion includes evidence level, clinical guidelines,
              PubMed citations, and pathophysiological mechanisms.
            </p>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <h3 className="font-semibold text-gray-900 mb-3">Research Export</h3>
            <p className="text-sm text-gray-600">
              Export all metrics as JSON for statistical analysis.
              Includes timestamps, user IDs (anonymized), and full audit trails.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

