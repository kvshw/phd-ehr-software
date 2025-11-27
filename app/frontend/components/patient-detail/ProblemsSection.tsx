/**
 * Problem List section component
 * Displays and manages patient problems
 */
'use client';

import { useState, useEffect } from 'react';
import { problemService, Problem, ProblemCreate } from '@/lib/problemService';

interface ProblemsSectionProps {
  patientId: string;
}

export function ProblemsSection({ patientId }: ProblemsSectionProps) {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [filter, setFilter] = useState<'all' | 'active' | 'resolved' | 'chronic' | 'inactive'>('all');
  const [formData, setFormData] = useState<ProblemCreate>({
    patient_id: patientId,
    problem_name: '',
    icd_code: '',
    status: 'active',
    notes: '',
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchProblems();
  }, [patientId, filter]);

  const fetchProblems = async () => {
    setLoading(true);
    setError(null);
    try {
      const statusFilter = filter === 'all' ? undefined : filter;
      const data = await problemService.getPatientProblems(patientId, statusFilter);
      setProblems(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load problems');
      console.error('Error fetching problems:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      await problemService.createProblem(formData);
      setShowAddForm(false);
      setFormData({
        patient_id: patientId,
        problem_name: '',
        icd_code: '',
        status: 'active',
        notes: '',
      });
      fetchProblems();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create problem');
      console.error('Error creating problem:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleResolve = async (problemId: string) => {
    try {
      await problemService.updateProblem(problemId, {
        status: 'resolved',
        resolved_date: new Date().toISOString(),
      });
      fetchProblems();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to resolve problem');
      console.error('Error resolving problem:', err);
    }
  };

  const handleDelete = async (problemId: string) => {
    if (!confirm('Are you sure you want to delete this problem?')) {
      return;
    }

    try {
      await problemService.deleteProblem(problemId);
      fetchProblems();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete problem');
      console.error('Error deleting problem:', err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-red-100 text-red-800';
      case 'resolved':
        return 'bg-green-100 text-green-800';
      case 'chronic':
        return 'bg-yellow-100 text-yellow-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredProblems = filter === 'all' 
    ? problems 
    : problems.filter(p => p.status === filter);

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-xl border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-indigo-100">
            <svg className="h-5 w-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900">Problem List</h2>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="all">All</option>
            <option value="active">Active</option>
            <option value="resolved">Resolved</option>
            <option value="chronic">Chronic</option>
            <option value="inactive">Inactive</option>
          </select>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors text-sm"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Problem
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}

      {/* Add Form */}
      {showAddForm && (
        <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Add New Problem</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Problem Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.problem_name}
                onChange={(e) => setFormData({ ...formData, problem_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="e.g., Type 2 Diabetes, Hypertension"
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ICD-10 Code</label>
                <input
                  type="text"
                  value={formData.icd_code || ''}
                  onChange={(e) => setFormData({ ...formData, icd_code: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="e.g., E11.9"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="active">Active</option>
                  <option value="chronic">Chronic</option>
                  <option value="inactive">Inactive</option>
                  <option value="resolved">Resolved</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
              <textarea
                value={formData.notes || ''}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Additional notes about the problem"
              />
            </div>
            <div className="flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
              >
                {submitting ? 'Adding...' : 'Add Problem'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Problems List */}
      {filteredProblems.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">
            {problems.length === 0
              ? 'No problems recorded'
              : `No ${filter} problems`}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredProblems.map((problem) => (
            <div
              key={problem.id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {problem.problem_name}
                    </h3>
                    <span
                      className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getStatusColor(
                        problem.status
                      )}`}
                    >
                      {problem.status}
                    </span>
                    {problem.icd_code && (
                      <span className="text-xs text-gray-500">
                        ICD-10: {problem.icd_code}
                      </span>
                    )}
                  </div>
                  {problem.notes && (
                    <p className="text-sm text-gray-600 mb-2">{problem.notes}</p>
                  )}
                  <div className="text-xs text-gray-500">
                    {problem.onset_date && (
                      <span>Onset: {new Date(problem.onset_date).toLocaleDateString()}</span>
                    )}
                    {problem.resolved_date && (
                      <span className="ml-4">
                        Resolved: {new Date(problem.resolved_date).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  {problem.status === 'active' && (
                    <button
                      onClick={() => handleResolve(problem.id)}
                      className="px-3 py-1 text-sm text-green-700 bg-green-50 rounded hover:bg-green-100"
                    >
                      Mark Resolved
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(problem.id)}
                    className="px-3 py-1 text-sm text-gray-700 bg-gray-100 rounded hover:bg-gray-200"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

