/**
 * Transfer Learning Indicator Component
 * Shows cold-start/warm-start status and transfer learning progress
 */
'use client';

import React, { useState, useEffect } from 'react';
import { apiClient } from '@/lib/apiClient';

interface TransferStatus {
  user_id: string;
  specialty: string | null;
  experience_days: number;
  stage: 'cold_start' | 'warm_start' | 'personalized';
  stage_name: string;
  description: string;
  features_with_priors: number;
  source_distribution: Record<string, number>;
  blending_info: {
    prior_weight: number;
    personal_weight: number;
    prior_source: string;
  } | null;
  days_until_personalized: number;
}

interface TransferLearningIndicatorProps {
  className?: string;
  showDetails?: boolean;
}

export function TransferLearningIndicator({ 
  className = '', 
  showDetails = false 
}: TransferLearningIndicatorProps) {
  const [status, setStatus] = useState<TransferStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await apiClient.get<TransferStatus>('/mape-k/transfer/status');
      setStatus(response.data);
    } catch (error) {
      console.warn('Failed to fetch transfer status:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !status) {
    return null;
  }

  // Don't show if fully personalized (no transfer happening)
  if (status.stage === 'personalized') {
    return null;
  }

  const getStageColor = () => {
    switch (status.stage) {
      case 'cold_start':
        return 'from-blue-50 to-cyan-50 border-blue-200 text-blue-700';
      case 'warm_start':
        return 'from-amber-50 to-orange-50 border-amber-200 text-amber-700';
      default:
        return 'from-gray-50 to-gray-100 border-gray-200 text-gray-700';
    }
  };

  const getStageIcon = () => {
    switch (status.stage) {
      case 'cold_start':
        return '❄️';
      case 'warm_start':
        return '🔥';
      default:
        return '✨';
    }
  };

  return (
    <div className={className}>
      {/* Main Indicator */}
      <button
        onClick={() => setExpanded(!expanded)}
        className={`flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r ${getStageColor()} 
                   border rounded-lg hover:shadow-sm transition-all w-full text-left`}
      >
        <div className="flex items-center gap-1.5 flex-1">
          <span className="text-sm">{getStageIcon()}</span>
          <span className="text-xs font-medium">
            {status.stage_name}
          </span>
          <span className="text-xs opacity-75">
            ({status.experience_days} days)
          </span>
        </div>
        {showDetails && (
          <svg 
            className={`w-3.5 h-3.5 transition-transform ${expanded ? 'rotate-180' : ''}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        )}
      </button>

      {/* Expanded Details */}
      {expanded && showDetails && status && (
        <div className="mt-2 p-4 bg-white border border-gray-200 rounded-lg shadow-sm">
          <h4 className="text-sm font-semibold text-gray-900 mb-2">
            Transfer Learning Status
          </h4>
          
          <p className="text-xs text-gray-600 mb-3">
            {status.description}
          </p>

          {/* Progress Bar */}
          {status.stage === 'warm_start' && (
            <div className="mb-3">
              <div className="flex justify-between text-xs text-gray-600 mb-1">
                <span>Personalization Progress</span>
                <span>{status.days_until_personalized} days remaining</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-amber-400 to-orange-500 rounded-full transition-all duration-500"
                  style={{ width: `${((30 - status.days_until_personalized) / 23) * 100}%` }}
                />
              </div>
            </div>
          )}

          {/* Blending Info */}
          {status.blending_info && (
            <div className="mb-3 p-2 bg-amber-50 rounded border border-amber-100">
              <p className="text-xs font-medium text-amber-900 mb-1">Current Blending:</p>
              <div className="space-y-1 text-xs text-amber-700">
                <div className="flex justify-between">
                  <span>From {status.blending_info.prior_source}:</span>
                  <span className="font-medium">{(status.blending_info.prior_weight * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Your personal data:</span>
                  <span className="font-medium">{(status.blending_info.personal_weight * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>
          )}

          {/* Source Distribution */}
          {Object.keys(status.source_distribution).length > 0 && (
            <div className="mb-3">
              <p className="text-xs font-medium text-gray-700 mb-1">Prior Sources:</p>
              <div className="flex flex-wrap gap-1">
                {Object.entries(status.source_distribution).map(([source, count]) => (
                  <span
                    key={source}
                    className="text-[10px] px-2 py-0.5 bg-gray-100 text-gray-600 rounded"
                  >
                    {source}: {count}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Info */}
          <div className="pt-2 border-t border-gray-100">
            <p className="text-[10px] text-gray-400">
              {status.features_with_priors} features using transferred knowledge
              {status.specialty && ` • Specialty: ${status.specialty}`}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Compact version for headers
 */
export function TransferLearningIndicatorCompact({ className = '' }: { className?: string }) {
  const [status, setStatus] = useState<TransferStatus | null>(null);

  useEffect(() => {
    apiClient.get<TransferStatus>('/mape-k/transfer/status')
      .then(response => setStatus(response.data))
      .catch(() => setStatus(null));
  }, []);

  if (!status || status.stage === 'personalized') return null;

  const getStageIcon = () => {
    switch (status.stage) {
      case 'cold_start': return '❄️';
      case 'warm_start': return '🔥';
      default: return null;
    }
  };

  return (
    <div 
      className={`flex items-center gap-1 px-2 py-1 bg-blue-100 rounded text-xs text-blue-700 ${className}`}
      title={`${status.stage_name}: ${status.description}`}
    >
      <span>{getStageIcon()}</span>
      <span>{status.stage_name}</span>
    </div>
  );
}

export default TransferLearningIndicator;

