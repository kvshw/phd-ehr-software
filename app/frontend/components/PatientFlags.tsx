/**
 * Patient flags component for vital risk and image status
 */
'use client';

interface PatientFlagsProps {
  hasVitalRisk: boolean;
  hasImages: boolean;
  className?: string;
}

export function PatientFlags({ hasVitalRisk, hasImages, className = '' }: PatientFlagsProps) {
  return (
    <div className={`flex gap-2 ${className}`}>
      {hasVitalRisk && (
        <span
          className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-orange-100 text-orange-800"
          title="Vital risk detected"
        >
          <svg
            className="w-3 h-3 mr-1"
            fill="currentColor"
            viewBox="0 0 20 20"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          Risk
        </span>
      )}
      {hasImages && (
        <span
          className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800"
          title="Has medical images"
        >
          <svg
            className="w-3 h-3 mr-1"
            fill="currentColor"
            viewBox="0 0 20 20"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fillRule="evenodd"
              d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
              clipRule="evenodd"
            />
          </svg>
          Images
        </span>
      )}
    </div>
  );
}

