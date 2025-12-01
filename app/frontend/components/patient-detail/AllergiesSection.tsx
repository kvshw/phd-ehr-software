/**
 * Allergies section component
 * Displays and manages patient allergies
 */
'use client';

import { useState, useEffect } from 'react';
import { allergyService, Allergy, AllergyCreate } from '@/lib/allergyService';

interface AllergiesSectionProps {
  patientId: string;
}

export function AllergiesSection({ patientId }: AllergiesSectionProps) {
  const [allergies, setAllergies] = useState<Allergy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState<AllergyCreate>({
    patient_id: patientId,
    allergen: '',
    allergen_type: '',
    severity: '',
    reaction: '',
    notes: '',
    status: 'active',
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchAllergies();
  }, [patientId]);

  const fetchAllergies = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await allergyService.getPatientAllergies(patientId);
      setAllergies(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load allergies');
      console.error('Error fetching allergies:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      await allergyService.createAllergy(formData);
      setShowAddForm(false);
      setFormData({
        patient_id: patientId,
        allergen: '',
        allergen_type: '',
        severity: '',
        reaction: '',
        notes: '',
        status: 'active',
      });
      fetchAllergies();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create allergy');
      console.error('Error creating allergy:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (allergyId: string) => {
    if (!confirm('Are you sure you want to delete this allergy?')) {
      return;
    }

    try {
      await allergyService.deleteAllergy(allergyId);
      fetchAllergies();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete allergy');
      console.error('Error deleting allergy:', err);
    }
  };

  const getSeverityColor = (severity: string | null) => {
    if (!severity) return 'bg-gray-100 text-gray-800';
    switch (severity.toLowerCase()) {
      case 'life-threatening':
        return 'bg-red-200 text-red-900 border-2 border-red-500';
      case 'severe':
        return 'bg-red-100 text-red-800';
      case 'moderate':
        return 'bg-yellow-100 text-yellow-800';
      case 'mild':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const activeAllergies = allergies.filter(a => a.status === 'active');

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
          <h2 className="text-xl font-semibold text-gray-900">Allergies</h2>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors text-sm"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Allergy
        </button>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}

      {/* Warning for Severe Allergies */}
      {activeAllergies.some(a => a.severity === 'severe' || a.severity === 'life-threatening') && (
        <div className="mb-4 bg-red-50 border-2 border-red-300 rounded-lg p-4">
          <div className="flex items-start gap-2">
            <svg className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div>
              <p className="text-sm font-semibold text-red-800">⚠️ Severe Allergies Present</p>
              <p className="text-xs text-red-700 mt-1">
                This patient has severe or life-threatening allergies. Exercise caution.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Add Form */}
      {showAddForm && (
        <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Add New Allergy</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Allergen <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.allergen}
                onChange={(e) => setFormData({ ...formData, allergen: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                placeholder="e.g., Penicillin, Latex, Peanuts"
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Allergen Type</label>
                <select
                  value={formData.allergen_type || ''}
                  onChange={(e) => setFormData({ ...formData, allergen_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                >
                  <option value="">Select type</option>
                  <option value="medication">Medication</option>
                  <option value="food">Food</option>
                  <option value="environmental">Environmental</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Severity</label>
                <select
                  value={formData.severity || ''}
                  onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                >
                  <option value="">Select severity</option>
                  <option value="mild">Mild</option>
                  <option value="moderate">Moderate</option>
                  <option value="severe">Severe</option>
                  <option value="life-threatening">Life-threatening</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Reaction</label>
              <textarea
                value={formData.reaction || ''}
                onChange={(e) => setFormData({ ...formData, reaction: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                placeholder="e.g., Hives, Anaphylaxis, Rash"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
              <textarea
                value={formData.notes || ''}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                placeholder="Additional notes"
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
                {submitting ? 'Adding...' : 'Add Allergy'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Allergies List */}
      {allergies.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No allergies recorded</p>
        </div>
      ) : (
        <div className="space-y-4">
          {allergies.map((allergy) => (
            <div
              key={allergy.id}
              className={`border rounded-lg p-4 hover:shadow-md transition-shadow ${
                allergy.severity === 'severe' || allergy.severity === 'life-threatening'
                  ? 'border-red-300 bg-red-50'
                  : 'border-gray-200'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {allergy.allergen}
                    </h3>
                    {allergy.severity && (
                      <span
                        className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getSeverityColor(
                          allergy.severity
                        )}`}
                      >
                        {allergy.severity}
                      </span>
                    )}
                    {allergy.allergen_type && (
                      <span className="text-xs text-gray-500">
                        ({allergy.allergen_type})
                      </span>
                    )}
                  </div>
                  {allergy.reaction && (
                    <p className="text-sm text-gray-700 mb-2">
                      <span className="font-medium">Reaction:</span> {allergy.reaction}
                    </p>
                  )}
                  {allergy.notes && (
                    <p className="text-sm text-gray-600 mb-2">{allergy.notes}</p>
                  )}
                  {allergy.onset_date && (
                    <p className="text-xs text-gray-500">
                      Identified: {new Date(allergy.onset_date).toLocaleDateString()}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => handleDelete(allergy.id)}
                  className="px-3 py-1 text-sm text-gray-700 bg-gray-100 rounded hover:bg-gray-200 ml-4"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
