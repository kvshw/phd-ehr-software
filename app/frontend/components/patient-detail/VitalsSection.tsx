/**
 * Vitals section component with trend graph
 */
'use client';

import { VitalsTrendGraph } from './VitalsTrendGraph';

interface VitalsSectionProps {
  patientId: string;
}

export function VitalsSection({ patientId }: VitalsSectionProps) {
  return (
    <div className="space-y-4">
      <VitalsTrendGraph patientId={patientId} />
      {/* Safety Notice for AI Risk Predictions */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start gap-2">
          <svg
            className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          <div>
            <p className="text-sm font-medium text-yellow-800">
              AI Risk Assessment - Experimental
            </p>
            <p className="text-xs text-yellow-700 mt-1">
              Any AI-generated risk assessments displayed here are experimental and for research
              purposes only. Always verify with clinical judgment and standard protocols.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

