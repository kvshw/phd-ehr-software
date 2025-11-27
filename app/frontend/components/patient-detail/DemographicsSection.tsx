/**
 * Demographics section component
 */
'use client';

import { Patient } from '@/lib/patientService';

interface DemographicsSectionProps {
  patient: Patient;
}

export function DemographicsSection({ patient }: DemographicsSectionProps) {
  return (
    <div className="bg-white shadow rounded-xl border border-gray-200 p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-indigo-100">
          <svg className="h-5 w-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-gray-900">Demographics</h2>
      </div>
      {/* Basic Demographics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Name</label>
          </div>
          <p className="text-base font-semibold text-gray-900">{patient.name}</p>
        </div>
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Age</label>
          </div>
          <p className="text-base font-semibold text-gray-900">{patient.age} years</p>
          {patient.date_of_birth && (
            <p className="text-xs text-gray-500 mt-1">
              Born: {new Date(patient.date_of_birth).toLocaleDateString('fi-FI', { year: 'numeric', month: 'long', day: 'numeric' })}
            </p>
          )}
        </div>
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Sex</label>
          </div>
          <p className="text-base font-semibold text-gray-900">{patient.sex}</p>
        </div>
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
            </svg>
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Patient ID</label>
          </div>
          <p className="text-base font-mono text-sm text-gray-900 break-all">{patient.id}</p>
        </div>
      </div>

      {/* Finnish Identification */}
      {(patient.henkilotunnus || patient.kela_card_number) && (
        <div className="mb-6 pt-6 border-t border-gray-200">
          <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <svg className="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            Finnish Healthcare Identification
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {patient.henkilotunnus && (
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
                  </svg>
                  <label className="text-xs font-semibold text-blue-700 uppercase tracking-wide">Henkilötunnus</label>
                </div>
                <p className="text-sm font-semibold text-blue-900 font-mono">{patient.henkilotunnus}</p>
              </div>
            )}
            {patient.kela_card_number && (
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                  </svg>
                  <label className="text-xs font-semibold text-blue-700 uppercase tracking-wide">Kela Card Number</label>
                </div>
                <p className="text-base font-semibold text-blue-900">{patient.kela_card_number}</p>
                {patient.kela_eligible !== false && (
                  <p className="text-xs text-blue-600 mt-1">✓ Eligible for Kela benefits</p>
                )}
              </div>
            )}
            {patient.municipality_name && (
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <label className="text-xs font-semibold text-blue-700 uppercase tracking-wide">Municipality</label>
                </div>
                <p className="text-base font-semibold text-blue-900">{patient.municipality_name}</p>
                {patient.municipality_code && (
                  <p className="text-xs text-blue-600 mt-1">Code: {patient.municipality_code}</p>
                )}
                {patient.primary_care_center && (
                  <p className="text-xs text-blue-600 mt-1">Primary Care: {patient.primary_care_center}</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Contact Information */}
      {(patient.phone || patient.email || patient.address) && (
        <div className="mb-6 pt-6 border-t border-gray-200">
          <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <svg className="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
            Contact Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {patient.phone && (
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Phone</label>
                </div>
                <p className="text-base font-semibold text-gray-900">{patient.phone}</p>
              </div>
            )}
            {patient.email && (
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Email</label>
                </div>
                <p className="text-base font-semibold text-gray-900">{patient.email}</p>
              </div>
            )}
            {patient.address && (
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200 md:col-span-2">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Address</label>
                </div>
                <p className="text-base font-semibold text-gray-900">{patient.address}</p>
                {(patient.postal_code || patient.city) && (
                  <p className="text-sm text-gray-600 mt-1">
                    {patient.postal_code} {patient.city}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Emergency Contact */}
      {patient.emergency_contact_name && (
        <div className="pt-6 border-t border-gray-200">
          <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            Emergency Contact
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-4 bg-red-50 rounded-lg border border-red-200">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <label className="text-xs font-semibold text-red-700 uppercase tracking-wide">Name</label>
              </div>
              <p className="text-base font-semibold text-red-900">{patient.emergency_contact_name}</p>
              {patient.emergency_contact_relation && (
                <p className="text-xs text-red-600 mt-1">Relation: {patient.emergency_contact_relation}</p>
              )}
            </div>
            {patient.emergency_contact_phone && (
              <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  <label className="text-xs font-semibold text-red-700 uppercase tracking-wide">Phone</label>
                </div>
                <p className="text-base font-semibold text-red-900">{patient.emergency_contact_phone}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

