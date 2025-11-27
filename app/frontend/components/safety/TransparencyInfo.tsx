/**
 * Transparency Information Component
 * Displays information about data usage and model behavior
 */
'use client';

import { useState } from 'react';

export function TransparencyInfo() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-2">
          <svg
            className="w-5 h-5 text-indigo-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900">Transparency & Data Usage</h3>
        </div>
        <svg
          className={`w-5 h-5 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {isOpen && (
        <div className="mt-4 space-y-4 text-sm text-gray-700">
          <div>
            <h4 className="font-semibold mb-2">AI Model Behavior</h4>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li>All AI models are rule-based and experimental</li>
              <li>Model versions are displayed for transparency</li>
              <li>All suggestions include explanations of reasoning</li>
              <li>No prescriptive language is used in suggestions</li>
              <li>All outputs are clearly labeled as "Experimental"</li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-2">Data Usage</h4>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li>Only synthetic/anonymized data is used</li>
              <li>No PHI (Protected Health Information) is stored or logged</li>
              <li>User interactions are logged for research purposes only</li>
              <li>All logged data is anonymized and cannot identify patients</li>
              <li>Navigation patterns are analyzed to improve UI adaptation</li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-2">Adaptation System</h4>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li>UI adaptations are based on usage patterns</li>
              <li>All adaptations are logged for research</li>
              <li>Users can reset to default layout at any time</li>
              <li>Adaptation explanations are provided</li>
              <li>No clinical decisions are made autonomously</li>
            </ul>
          </div>

          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm font-medium text-yellow-800 mb-1">
              Research Platform Notice
            </p>
            <p className="text-xs text-yellow-700">
              This platform is for research purposes only. All AI outputs are experimental and
              should not be used as the sole basis for clinical decisions. Always verify with
              clinical judgment and standard protocols.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

