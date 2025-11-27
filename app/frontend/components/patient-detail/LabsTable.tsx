/**
 * Labs Table Component
 * Displays lab results in a sortable and filterable table with abnormal value highlighting
 */
'use client';

import { useState, useEffect, useMemo } from 'react';
import { labService, Lab } from '@/lib/labService';

interface LabsTableProps {
  patientId: string;
}

type SortField = 'timestamp' | 'lab_type' | 'value';
type SortDirection = 'asc' | 'desc';

export function LabsTable({ patientId }: LabsTableProps) {
  const [labs, setLabs] = useState<Lab[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [total, setTotal] = useState(0);
  
  // Sorting
  const [sortField, setSortField] = useState<SortField>('timestamp');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  
  // Filtering
  const [filterLabType, setFilterLabType] = useState('');
  const [searchLabType, setSearchLabType] = useState('');

  useEffect(() => {
    fetchLabs();
  }, [patientId, page, filterLabType]);

  const fetchLabs = async () => {
    setLoading(true);
    setError(null);
    try {
      const filters: any = {
        page,
        page_size: pageSize,
      };
      
      if (filterLabType) {
        filters.lab_type = filterLabType;
      }

      const response = await labService.getPatientLabs(patientId, filters);
      setLabs(response.items);
      setTotal(response.total);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load lab results');
      console.error('Error fetching labs:', err);
    } finally {
      setLoading(false);
    }
  };

  // Get unique lab types for filter dropdown
  const uniqueLabTypes = useMemo(() => {
    const types = new Set<string>();
    labs.forEach((lab) => types.add(lab.lab_type));
    return Array.from(types).sort();
  }, [labs]);

  // Filter labs by search term
  const filteredLabs = useMemo(() => {
    let filtered = labs;
    
    if (searchLabType) {
      filtered = filtered.filter((lab) =>
        lab.lab_type.toLowerCase().includes(searchLabType.toLowerCase())
      );
    }
    
    return filtered;
  }, [labs, searchLabType]);

  // Sort labs
  const sortedLabs = useMemo(() => {
    const sorted = [...filteredLabs].sort((a, b) => {
      let aValue: any;
      let bValue: any;

      if (sortField === 'timestamp') {
        aValue = new Date(a.timestamp).getTime();
        bValue = new Date(b.timestamp).getTime();
      } else if (sortField === 'lab_type') {
        aValue = a.lab_type.toLowerCase();
        bValue = b.lab_type.toLowerCase();
      } else if (sortField === 'value') {
        aValue = a.value ?? 0;
        bValue = b.value ?? 0;
      } else {
        return 0;
      }

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return sorted;
  }, [filteredLabs, sortField, sortDirection]);

  // Handle sorting
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Check if value is abnormal
  const isAbnormal = (lab: Lab): boolean => {
    if (lab.value === null || lab.value === undefined || !lab.normal_range) {
      return false;
    }

    // Parse normal range (e.g., "70-100 mg/dL" or "3.5-5.0")
    const rangeMatch = lab.normal_range.match(/(\d+\.?\d*)\s*-\s*(\d+\.?\d*)/);
    if (!rangeMatch) {
      return false;
    }

    const min = parseFloat(rangeMatch[1]);
    const max = parseFloat(rangeMatch[2]);
    
    return lab.value < min || lab.value > max;
  };

  // Get trend indicator (simplified - compares with previous value of same lab type)
  const getTrend = (lab: Lab, index: number): 'up' | 'down' | 'stable' | null => {
    if (index === 0) return null;
    
    // Find previous lab of same type
    const previousLab = sortedLabs
      .slice(0, index)
      .reverse()
      .find((l) => l.lab_type === lab.lab_type);
    
    if (!previousLab || previousLab.value === null || lab.value === null) {
      return null;
    }

    const diff = lab.value - previousLab.value;
    const percentDiff = (diff / previousLab.value) * 100;

    if (Math.abs(percentDiff) < 5) return 'stable';
    return diff > 0 ? 'up' : 'down';
  };

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

  // Trend icon
  const TrendIcon = ({ trend }: { trend: 'up' | 'down' | 'stable' | null }) => {
    if (trend === null) return null;
    
    if (trend === 'up') {
      return (
        <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      );
    } else if (trend === 'down') {
      return (
        <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
        </svg>
      );
    } else {
      return (
        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
        </svg>
      );
    }
  };

  if (loading && labs.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading lab results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
        <button
          onClick={fetchLabs}
          className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
        >
          Retry
        </button>
      </div>
    );
  }

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="bg-white shadow rounded-xl border border-gray-200 p-6">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-indigo-100">
            <svg className="h-5 w-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900">Lab Results</h2>
        </div>
        
        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="filter-lab-type" className="block text-sm font-medium text-gray-700 mb-1">
              Filter by Lab Type
            </label>
            <select
              id="filter-lab-type"
              value={filterLabType}
              onChange={(e) => {
                setFilterLabType(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">All Lab Types</option>
              {uniqueLabTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="search-lab-type" className="block text-sm font-medium text-gray-700 mb-1">
              Search Lab Type
            </label>
            <input
              id="search-lab-type"
              type="text"
              value={searchLabType}
              onChange={(e) => setSearchLabType(e.target.value)}
              placeholder="Search by lab type..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('timestamp')}
              >
                <div className="flex items-center gap-2">
                  Date/Time
                  <SortIcon field="timestamp" />
                </div>
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('lab_type')}
              >
                <div className="flex items-center gap-2">
                  Lab Type
                  <SortIcon field="lab_type" />
                </div>
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('value')}
              >
                <div className="flex items-center gap-2">
                  Value
                  <SortIcon field="value" />
                </div>
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Normal Range
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Status
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Trend
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedLabs.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                  No lab results found
                </td>
              </tr>
            ) : (
              sortedLabs.map((lab, index) => {
                const abnormal = isAbnormal(lab);
                const trend = getTrend(lab, index);

                return (
                  <tr
                    key={lab.id}
                    className={abnormal ? 'bg-red-50 hover:bg-red-100' : 'hover:bg-gray-50'}
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(lab.timestamp)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{lab.lab_type}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div
                        className={`text-sm font-medium ${
                          abnormal ? 'text-red-600' : 'text-gray-900'
                        }`}
                      >
                        {lab.value !== null ? lab.value.toFixed(2) : 'N/A'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {lab.normal_range || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {abnormal ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          Abnormal
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Normal
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <TrendIcon trend={trend} />
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
        <div className="mt-6 flex items-center justify-between border-t border-gray-200 pt-4">
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
  );
}

