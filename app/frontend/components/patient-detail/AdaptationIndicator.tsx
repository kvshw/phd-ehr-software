/**
 * Adaptation Indicator Component
 * Shows when UI adaptations are active and allows reset
 * Enhanced with transparency information
 */
'use client';

import { usePatientDetailStore } from '@/store/patientDetailStore';
import { useState } from 'react';

export function AdaptationIndicator() {
  const {
    adaptationActive,
    adaptationExplanation,
    resetAdaptation,
  } = usePatientDetailStore();
  const [showDetails, setShowDetails] = useState(false);

  if (!adaptationActive) {
    return null;
  }

  return (
    <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <svg
              className="w-5 h-5 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
            <h3 className="text-sm font-semibold text-blue-900">
              UI Adapted for You
            </h3>
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
              Experimental
            </span>
          </div>
          {adaptationExplanation && (
            <p className="text-sm text-blue-800 mb-2">{adaptationExplanation}</p>
          )}
          <p className="text-xs text-blue-700 mb-2">
            The interface has been customized based on your usage patterns.
          </p>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-xs text-blue-600 hover:text-blue-800 underline"
          >
            {showDetails ? 'Hide' : 'Show'} adaptation details
          </button>
          {showDetails && (
            <div className="mt-2 p-3 bg-white rounded border border-blue-200 text-xs text-gray-700">
              <p className="font-medium mb-1">How adaptations work:</p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>Section order is adjusted based on your navigation patterns</li>
                <li>Suggestion density adapts to your interaction rates</li>
                <li>All adaptations are logged for research purposes</li>
                <li>You can reset to default layout at any time</li>
              </ul>
              <p className="mt-2 text-gray-600">
                <strong>Transparency:</strong> This adaptation system is experimental and for
                research purposes only. Your usage patterns are analyzed to improve the system,
                but no PHI or identifiable information is stored.
              </p>
            </div>
          )}
        </div>
        <button
          onClick={resetAdaptation}
          className="ml-4 text-xs text-blue-600 hover:text-blue-800 underline whitespace-nowrap"
          title="Reset to default layout"
        >
          Reset Layout
        </button>
      </div>
    </div>
  );
}

