/**
 * Modern Patient Card Grid Component
 * Card-based layout for patient list
 */
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Patient, patientService, PatientFilters } from '@/lib/patientService';
import { RiskBadge, RiskLevel } from '../RiskBadge';
import { PatientFlags } from '../PatientFlags';

export function PatientCardGrid() {
  const router = useRouter();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(12);
  const [totalPages, setTotalPages] = useState(0);
  const [total, setTotal] = useState(0);
  
  const [filters, setFilters] = useState<PatientFilters>({
    page: 1,
    page_size: 12,
  });
  const [searchName, setSearchName] = useState('');
  const [filterSex, setFilterSex] = useState<string>('');
  const [filterRisk, setFilterRisk] = useState<string>('');

  const [patientMetadata, setPatientMetadata] = useState<Record<string, {
    hasVitalRisk: boolean;
    hasImages: boolean;
    riskLevel: RiskLevel;
  }>>({});

  const fetchPatients = async () => {
    setLoading(true);
    setError(null);
    try {
      const updatedFilters: PatientFilters = {
        ...filters,
        page,
        page_size: pageSize,
        name: searchName || undefined,
        sex: filterSex || undefined,
      };
      
      const response = await patientService.getPatients(updatedFilters);
      setPatients(response.items);
      setTotal(response.total);
      setTotalPages(Math.ceil(response.total / pageSize));

      // Fetch metadata for all patients
      if (response.items.length > 0) {
        const patientIds = response.items.map(p => p.id);
        try {
          const metadata = await patientService.getPatientsMetadata(patientIds);
          const metadataMap: Record<string, any> = {};
          Object.entries(metadata).forEach(([id, data]) => {
            metadataMap[id] = {
              hasVitalRisk: data.has_vitals,
              hasImages: data.has_images,
              riskLevel: data.risk_level as RiskLevel,
            };
          });
          setPatientMetadata(metadataMap);
        } catch (err) {
          console.error('Error fetching metadata:', err);
        }
      }
    } catch (err: any) {
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        setError('Request timeout - the server is taking longer than expected. Please try again.');
        console.error('Timeout fetching patients:', err);
      } else {
        setError(err.response?.data?.detail || 'Failed to load patients');
        console.error('Error fetching patients:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, [page, searchName, filterSex, filterRisk]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (page === 1) {
        fetchPatients();
      } else {
        setPage(1);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [searchName, filterSex, filterRisk]);

  if (loading && patients.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading patients...</p>
        </div>
      </div>
    );
  }

  if (error && patients.length === 0) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
        <p className="text-red-800">{error}</p>
        <button
          onClick={fetchPatients}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Filters */}
      <div className="mb-6 bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          <h3 className="text-sm font-semibold text-gray-900">Search & Filter</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <input
              type="text"
              value={searchName}
              onChange={(e) => {
                setSearchName(e.target.value);
                setPage(1);
              }}
              placeholder="Search by name..."
              className="w-full px-4 py-2.5 border border-blue-200 rounded-xl shadow focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
            />
          </div>
          <div>
            <select
              value={filterSex}
              onChange={(e) => {
                setFilterSex(e.target.value);
                setPage(1);
              }}
              className="w-full px-4 py-2.5 border border-blue-200 rounded-xl shadow focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
            >
              <option value="">All Genders</option>
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div>
            <select
              value={filterRisk}
              onChange={(e) => {
                setFilterRisk(e.target.value);
                setPage(1);
              }}
              className="w-full px-4 py-2.5 border border-blue-200 rounded-xl shadow focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
            >
              <option value="">All Risk Levels</option>
              <option value="routine">Routine</option>
              <option value="needs_attention">Needs Attention</option>
              <option value="high_concern">High Concern</option>
            </select>
          </div>
        </div>
      </div>

      {/* Patient Cards Grid */}
      {patients.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 shadow p-12 text-center">
          <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <p className="text-gray-500 text-lg">No patients found</p>
          <p className="text-gray-400 text-sm mt-2">Try adjusting your filters</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {patients.map((patient) => {
              const metadata = patientMetadata[patient.id] || {
                hasVitalRisk: false,
                hasImages: false,
                riskLevel: 'routine' as RiskLevel,
              };

              return (
                <div
                  key={patient.id}
                  onClick={() => router.push(`/patients/${patient.id}`)}
                  className="bg-white rounded-2xl shadow border border-gray-200 p-6 hover:shadow-md hover:border-blue-300 cursor-pointer transition-all duration-300 group"
                >
                  {/* Card Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white font-bold text-lg shadow group-hover:scale-110 transition-transform">
                        {patient.name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <h3 className="font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
                          {patient.name}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {patient.age} Years • {patient.sex}
                        </p>
                      </div>
                    </div>
                    <RiskBadge level={metadata.riskLevel} />
                  </div>

                  {/* Patient Info */}
                  <div className="space-y-2 mb-4">
                    {patient.primary_diagnosis && (
                      <div className="flex items-center gap-2 text-sm">
                        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span className="text-gray-700">{patient.primary_diagnosis}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <span>Updated {new Date(patient.updated_at).toLocaleDateString()}</span>
                    </div>
                  </div>

                  {/* Flags */}
                  <div className="flex items-center gap-2 pt-4 border-t border-gray-100">
                    <PatientFlags
                      hasVitalRisk={metadata.hasVitalRisk}
                      hasImages={metadata.hasImages}
                    />
                    <div className="ml-auto">
                      <svg className="w-5 h-5 text-gray-400 group-hover:text-blue-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-8 flex items-center justify-between">
              <div className="text-sm text-gray-600">
                Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of {total} patients
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg text-sm font-medium hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

