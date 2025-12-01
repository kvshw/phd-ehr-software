/**
 * Bandit Adaptation Indicator Component
 * Shows when Thompson Sampling is being used for layout adaptation
 */
'use client';

import React, { useState, useEffect } from 'react';
import { banditService, BanditStatus, FeatureBelief } from '@/lib/banditService';

interface BanditIndicatorProps {
  className?: string;
  showDetails?: boolean;
}

export function BanditIndicator({ className = '', showDetails = false }: BanditIndicatorProps) {
  const [status, setStatus] = useState<BanditStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const data = await banditService.getStatus();
      setStatus(data);
    } catch (error) {
      console.warn('Failed to fetch bandit status:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return null;
  }

  if (!status?.using_bandit) {
    // Not using bandit, show minimal indicator
    return (
      <div className={`text-xs text-gray-400 flex items-center gap-1 ${className}`}>
        <span className="w-2 h-2 rounded-full bg-gray-300"></span>
        <span>Rule-based adaptation</span>
      </div>
    );
  }

  return (
    <div className={`${className}`}>
      {/* Main Indicator */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-purple-50 to-indigo-50 
                   border border-purple-200 rounded-lg hover:border-purple-300 transition-all"
      >
        <div className="flex items-center gap-1.5">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-purple-500"></span>
          </span>
          <span className="text-xs font-medium text-purple-700">
            AI Learning Active
          </span>
        </div>
        <svg 
          className={`w-3.5 h-3.5 text-purple-500 transition-transform ${expanded ? 'rotate-180' : ''}`}
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expanded Details */}
      {expanded && showDetails && status && (
        <div className="mt-2 p-4 bg-white border border-purple-100 rounded-lg shadow-sm">
          <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <svg className="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Thompson Sampling Adaptation
          </h4>
          
          <p className="text-xs text-gray-600 mb-3">
            The system is learning your preferences to optimize the interface layout. 
            Features you use frequently will be promoted, while rarely-used features may be demoted.
          </p>

          {/* Feature Beliefs */}
          <div className="space-y-2">
            <h5 className="text-xs font-medium text-gray-700">Feature Preferences (learned)</h5>
            <div className="grid grid-cols-2 gap-2">
              {status.feature_beliefs
                .sort((a, b) => b.expected_value - a.expected_value)
                .slice(0, 6)
                .map((belief) => (
                  <FeatureBeliefCard key={belief.feature_key} belief={belief} />
                ))}
            </div>
          </div>

          {/* Recent Adaptations */}
          {status.recent_adaptations.length > 0 && (
            <div className="mt-4">
              <h5 className="text-xs font-medium text-gray-700 mb-2">Recent Changes</h5>
              <div className="space-y-1">
                {status.recent_adaptations.slice(0, 3).map((adaptation, idx) => (
                  <div 
                    key={idx}
                    className={`text-xs px-2 py-1 rounded flex items-center justify-between
                      ${adaptation.action === 'promoted' ? 'bg-green-50 text-green-700' : ''}
                      ${adaptation.action === 'demoted' ? 'bg-amber-50 text-amber-700' : ''}
                      ${adaptation.action === 'maintained' ? 'bg-gray-50 text-gray-600' : ''}
                    `}
                  >
                    <span className="capitalize">{adaptation.feature_key.replace('_', ' ')}</span>
                    <span className="flex items-center gap-1">
                      {adaptation.action === 'promoted' && '↑'}
                      {adaptation.action === 'demoted' && '↓'}
                      {adaptation.action === 'maintained' && '−'}
                      {adaptation.action}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Research Note */}
          <div className="mt-4 pt-3 border-t border-gray-100">
            <p className="text-[10px] text-gray-400 flex items-center gap-1">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Research mode: All adaptation decisions are logged for analysis
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Feature Belief Card - shows learned preference for a feature
 */
function FeatureBeliefCard({ belief }: { belief: FeatureBelief }) {
  const confidence = belief.expected_value;
  const width = `${Math.round(confidence * 100)}%`;
  
  return (
    <div className="p-2 bg-gray-50 rounded border border-gray-100">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-medium text-gray-700 capitalize">
          {belief.feature_key.replace('_', ' ')}
        </span>
        {belief.is_critical && (
          <span className="text-[10px] px-1 py-0.5 bg-red-100 text-red-600 rounded">
            Critical
          </span>
        )}
      </div>
      <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-purple-400 to-indigo-500 rounded-full transition-all duration-500"
          style={{ width }}
        />
      </div>
      <div className="flex justify-between mt-1 text-[10px] text-gray-500">
        <span>{Math.round(confidence * 100)}% preference</span>
        <span>{belief.total_interactions} interactions</span>
      </div>
    </div>
  );
}

/**
 * Compact version for header/toolbar
 */
export function BanditIndicatorCompact({ className = '' }: { className?: string }) {
  const [usingBandit, setUsingBandit] = useState(false);

  useEffect(() => {
    banditService.getStatus()
      .then(status => setUsingBandit(status.using_bandit))
      .catch(() => setUsingBandit(false));
  }, []);

  if (!usingBandit) return null;

  return (
    <div 
      className={`flex items-center gap-1 px-2 py-1 bg-purple-100 rounded text-xs text-purple-700 ${className}`}
      title="AI is learning your preferences to optimize the interface"
    >
      <span className="relative flex h-1.5 w-1.5">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
        <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-purple-500"></span>
      </span>
      <span>AI Learning</span>
    </div>
  );
}

export default BanditIndicator;

