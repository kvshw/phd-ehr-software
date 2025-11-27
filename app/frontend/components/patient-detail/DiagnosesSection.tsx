/**
 * Diagnoses section component
 */
'use client';

import { Patient } from '@/lib/patientService';

interface DiagnosesSectionProps {
  patient: Patient;
}

export function DiagnosesSection({ patient }: DiagnosesSectionProps) {
  return (
    <div className="bg-white shadow rounded-xl border border-gray-200 p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-indigo-100">
          <svg className="h-5 w-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-gray-900">Diagnoses</h2>
      </div>
      {patient.primary_diagnosis ? (
        <div className="space-y-3">
          <div className="flex items-start p-3 bg-gray-50 rounded-lg">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-indigo-100 text-indigo-800">
                  Primary
                </span>
              </div>
              <p className="text-gray-900 font-medium">{patient.primary_diagnosis}</p>
            </div>
          </div>
        </div>
      ) : (
        <p className="text-gray-500 italic">No diagnoses recorded</p>
      )}
    </div>
  );
}

