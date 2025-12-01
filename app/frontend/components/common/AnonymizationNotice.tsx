/**
 * Anonymization Notice Component
 * Displays a notice when data is anonymized for research purposes
 */
'use client';

import React from 'react';

interface AnonymizationNoticeProps {
  className?: string;
  compact?: boolean;
}

export function AnonymizationNotice({ className = '', compact = false }: AnonymizationNoticeProps) {
  if (compact) {
    return (
      <div className={`inline-flex items-center gap-1.5 px-2 py-1 bg-amber-50 border border-amber-200 rounded text-xs text-amber-800 ${className}`}>
        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <span>Anonymized Data</span>
      </div>
    );
  }

  return (
    <div className={`bg-amber-50 border-l-4 border-amber-400 p-4 rounded-lg ${className}`}>
      <div className="flex">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-amber-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fillRule="evenodd" d="M8.485 2.495c.673-1.166 2.357-1.166 3.03 0l6.28 10.875c.673 1.166-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.459-1.515-2.625L8.485 2.495zM10 6a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 6zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-amber-800">Anonymized Data</h3>
          <div className="mt-2 text-sm text-amber-700">
            <p>
              Patient identifiers have been removed for research purposes. 
              Direct identifiers (names, IDs, contact information) are not visible.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

