/**
 * Patient header component with name, ID, and key demographics
 */
'use client';

import { Patient } from '@/lib/patientService';
import { RiskBadge, RiskLevel } from '../RiskBadge';

interface PatientHeaderProps {
  patient: Patient;
  riskLevel?: RiskLevel;
}

export function PatientHeader({ patient, riskLevel = 'routine' }: PatientHeaderProps) {
  return (
    <div className="bg-white shadow rounded-xl border border-gray-200 p-6 mb-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-4 mb-3">
            <div className="flex items-center justify-center h-12 w-12 rounded-full bg-indigo-100">
              <svg className="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{patient.name}</h1>
              <p className="text-sm text-gray-500 mt-0.5">Patient ID: {patient.id.slice(0, 8)}...</p>
            </div>
            <RiskBadge level={riskLevel} />
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-start">
              <svg className="w-5 h-5 text-gray-400 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="text-xs text-gray-500">Age</p>
                <p className="text-sm font-semibold text-gray-900">{patient.age} years</p>
                {patient.date_of_birth && (
                  <p className="text-xs text-gray-400 mt-0.5">
                    Born: {new Date(patient.date_of_birth).toLocaleDateString('fi-FI')}
                  </p>
                )}
              </div>
            </div>
            <div className="flex items-start">
              <svg className="w-5 h-5 text-gray-400 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <div>
                <p className="text-xs text-gray-500">Sex</p>
                <p className="text-sm font-semibold text-gray-900">{patient.sex}</p>
              </div>
            </div>
            {patient.henkilotunnus && (
              <div className="flex items-start">
                <svg className="w-5 h-5 text-gray-400 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
                </svg>
                <div>
                  <p className="text-xs text-gray-500">Henkilötunnus</p>
                  <p className="text-sm font-semibold text-gray-900">{patient.henkilotunnus}</p>
                </div>
              </div>
            )}
            {patient.kela_card_number && (
              <div className="flex items-start">
                <svg className="w-5 h-5 text-gray-400 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
                <div>
                  <p className="text-xs text-gray-500">Kela Card</p>
                  <p className="text-sm font-semibold text-gray-900">{patient.kela_card_number}</p>
                </div>
              </div>
            )}
            {patient.primary_diagnosis && (
              <div className="flex items-start col-span-2 md:col-span-1">
                <svg className="w-5 h-5 text-gray-400 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <div>
                  <p className="text-xs text-gray-500">Primary Diagnosis</p>
                  <p className="text-sm font-semibold text-gray-900 line-clamp-1">{patient.primary_diagnosis}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

