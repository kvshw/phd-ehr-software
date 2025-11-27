/**
 * Patient list table component
 */
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Patient, patientService, PatientFilters } from '@/lib/patientService';
import { RiskBadge, RiskLevel } from './RiskBadge';
import { PatientFlags } from './PatientFlags';

type SortField = 'name' | 'age' | 'updated_at' | 'risk';
type SortDirection = 'asc' | 'desc';

interface PatientListTableProps {
  className?: string;
}

export function PatientListTable({ className = '' }: PatientListTableProps) {
  const router = useRouter();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [totalPages, setTotalPages] = useState(0);
  const [total, setTotal] = useState(0);
  
  // Sorting
  const [sortField, setSortField] = useState<SortField>('updated_at');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  
  // Filtering
  const [filters, setFilters] = useState<PatientFilters>({
    page: 1,
    page_size: 20,
  });
  const [searchName, setSearchName] = useState('');
  const [filterSex, setFilterSex] = useState<string>('');
  const [filterRisk, setFilterRisk] = useState<string>('');

  // Patient metadata (risk flags, image status)
  const [patientMetadata, setPatientMetadata] = useState<Record<string, {
    hasVitalRisk: boolean;
    hasImages: boolean;
    riskLevel: RiskLevel;
  }>>({});

  // Fetch patients
  const fetchPatients = async () => {
    setLoading(true);
    setError(null);
    try {
      const currentFilters: PatientFilters = {
        ...filters,
        page,
        page_size: pageSize,
        name: searchName || undefined,
        sex: filterSex || undefined,
      };

      const response = await patientService.getPatients(currentFilters);
      setPatients(response.items);
      setTotalPages(response.total_pages);
      setTotal(response.total);

      // Fetch metadata for all patients in a single bulk API call (much faster!)
      if (response.items.length > 0) {
        try {
          const patientIds = response.items.map(p => p.id);
          const bulkMetadata = await patientService.getPatientsMetadata(patientIds);
          
          // Convert backend format to frontend format
          const metadataMap: Record<string, { hasVitalRisk: boolean; hasImages: boolean; riskLevel: RiskLevel }> = {};
          Object.entries(bulkMetadata).forEach(([patientId, metadata]) => {
            metadataMap[patientId] = {
              hasVitalRisk: metadata.has_vitals,
              hasImages: metadata.has_images,
              riskLevel: metadata.risk_level as RiskLevel,
            };
          });
          setPatientMetadata(metadataMap);
        } catch (err) {
          // Fallback: if bulk endpoint fails, set empty metadata (don't break the UI)
          console.error('Error fetching patient metadata:', err);
          const emptyMetadata: Record<string, { hasVitalRisk: boolean; hasImages: boolean; riskLevel: RiskLevel }> = {};
          response.items.forEach(patient => {
            emptyMetadata[patient.id] = {
              hasVitalRisk: false,
              hasImages: false,
              riskLevel: 'routine',
            };
          });
          setPatientMetadata(emptyMetadata);
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load patients');
      console.error('Error fetching patients:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, [page, searchName, filterSex]);

  // Handle sorting
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Sort patients locally (in a real app, this would be done server-side)
  const sortedPatients = [...patients].sort((a, b) => {
    let aValue: any;
    let bValue: any;

    if (sortField === 'name') {
      aValue = a.name.toLowerCase();
      bValue = b.name.toLowerCase();
    } else if (sortField === 'age') {
      aValue = a.age;
      bValue = b.age;
    } else if (sortField === 'updated_at') {
      aValue = new Date(a.updated_at).getTime();
      bValue = new Date(b.updated_at).getTime();
    } else if (sortField === 'risk') {
      const aRisk = patientMetadata[a.id]?.riskLevel || 'routine';
      const bRisk = patientMetadata[b.id]?.riskLevel || 'routine';
      const riskOrder = { routine: 0, needs_attention: 1, high_concern: 2 };
      aValue = riskOrder[aRisk];
      bValue = riskOrder[bRisk];
    } else {
      return 0;
    }

    if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  // Filter by risk level
  const filteredPatients = filterRisk
    ? sortedPatients.filter((p) => {
        const risk = patientMetadata[p.id]?.riskLevel || 'routine';
        return risk === filterRisk;
      })
    : sortedPatients;

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Get sort icon
  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) {
      return (
        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      );
    }
    return sortDirection === 'asc' ? (
      <svg className="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
      </svg>
    ) : (
      <svg className="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    );
  };

  if (loading && patients.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading patients...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
        <button
          onClick={fetchPatients}
          className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Filters */}
      <div className="mb-6 bg-white p-5 rounded-xl shadow border border-gray-200">
        <div className="flex items-center gap-2 mb-4">
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          <h3 className="text-sm font-semibold text-gray-700">Filters</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="search-name" className="block text-sm font-medium text-gray-700 mb-1">
              Search by Name
            </label>
            <input
              id="search-name"
              type="text"
              value={searchName}
              onChange={(e) => {
                setSearchName(e.target.value);
                setPage(1);
              }}
              placeholder="Patient name..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          <div>
            <label htmlFor="filter-sex" className="block text-sm font-medium text-gray-700 mb-1">
              Filter by Sex
            </label>
            <select
              id="filter-sex"
              value={filterSex}
              onChange={(e) => {
                setFilterSex(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">All</option>
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div>
            <label htmlFor="filter-risk" className="block text-sm font-medium text-gray-700 mb-1">
              Filter by Risk Level
            </label>
            <select
              id="filter-risk"
              value={filterRisk}
              onChange={(e) => setFilterRisk(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">All</option>
              <option value="routine">Routine</option>
              <option value="needs_attention">Needs Attention</option>
              <option value="high_concern">High Concern</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white shadow rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
              <tr>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('name')}
                >
                  <div className="flex items-center gap-2">
                    Name
                    <SortIcon field="name" />
                  </div>
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('age')}
                >
                  <div className="flex items-center gap-2">
                    Age / Sex
                    <SortIcon field="age" />
                  </div>
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Diagnosis
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('risk')}
                >
                  <div className="flex items-center gap-2">
                    Risk Level
                    <SortIcon field="risk" />
                  </div>
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Flags
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('updated_at')}
                >
                  <div className="flex items-center gap-2">
                    Last Updated
                    <SortIcon field="updated_at" />
                  </div>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredPatients.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-16 text-center">
                    <div className="flex flex-col items-center">
                      <svg className="w-12 h-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                      <p className="text-gray-500 font-medium">No patients found</p>
                      <p className="text-sm text-gray-400 mt-1">Try adjusting your filters</p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredPatients.map((patient) => {
                  const metadata = patientMetadata[patient.id] || {
                    hasVitalRisk: false,
                    hasImages: false,
                    riskLevel: 'routine' as RiskLevel,
                  };

                  return (
                    <tr
                      key={patient.id}
                      onClick={() => router.push(`/patients/${patient.id}`)}
                      className="hover:bg-gray-50 cursor-pointer transition-colors"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{patient.name}</div>
                        <div className="text-sm text-gray-500">ID: {patient.id.slice(0, 8)}...</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{patient.age}</div>
                        <div className="text-sm text-gray-500">{patient.sex}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          {patient.primary_diagnosis || 'No diagnosis'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <RiskBadge level={metadata.riskLevel} />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <PatientFlags
                          hasVitalRisk={metadata.hasVitalRisk}
                          hasImages={metadata.hasImages}
                        />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(patient.updated_at)}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page === totalPages}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Showing <span className="font-medium">{(page - 1) * pageSize + 1}</span> to{' '}
                  <span className="font-medium">{Math.min(page * pageSize, total)}</span> of{' '}
                  <span className="font-medium">{total}</span> results
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow -space-x-px" aria-label="Pagination">
                  <button
                    onClick={() => setPage(Math.max(1, page - 1))}
                    disabled={page === 1}
                    className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <span className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    onClick={() => setPage(Math.min(totalPages, page + 1))}
                    disabled={page === totalPages}
                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

