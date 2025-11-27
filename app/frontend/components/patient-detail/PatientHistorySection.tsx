/**
 * Patient History section component
 * Displays and edits PMH, PSH, Family History, Social History
 */
'use client';

import { useState } from 'react';
import { Patient, patientService } from '@/lib/patientService';

interface PatientHistorySectionProps {
  patient: Patient;
}

export function PatientHistorySection({ patient }: PatientHistorySectionProps) {
  const [editing, setEditing] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    past_medical_history: patient.past_medical_history || '',
    past_surgical_history: patient.past_surgical_history || '',
    family_history: patient.family_history || '',
    social_history: patient.social_history || '',
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSave = async (field: string) => {
    setSaving(true);
    setError(null);
    setSuccess(false);

    try {
      await patientService.updatePatient(patient.id, {
        [field]: formData[field as keyof typeof formData] || null,
      });
      setEditing(null);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      // Refresh patient data would be handled by parent component
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update history');
      console.error('Error updating history:', err);
    } finally {
      setSaving(false);
    }
  };

  const historyFields = [
    {
      key: 'past_medical_history',
      label: 'Past Medical History (PMH)',
      placeholder: 'Previous medical conditions, chronic diseases, etc.',
    },
    {
      key: 'past_surgical_history',
      label: 'Past Surgical History (PSH)',
      placeholder: 'Previous surgeries, procedures, dates, etc.',
    },
    {
      key: 'family_history',
      label: 'Family History',
      placeholder: 'Family medical history, hereditary conditions, etc.',
    },
    {
      key: 'social_history',
      label: 'Social History',
      placeholder: 'Smoking, alcohol use, occupation, lifestyle factors, etc.',
    },
  ];

  return (
    <div className="bg-white shadow rounded-xl border border-gray-200 p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-indigo-100">
          <svg className="h-5 w-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-gray-900">Patient History</h2>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-green-800 text-sm">History updated successfully</p>
        </div>
      )}

      <div className="space-y-6">
        {historyFields.map((field) => (
          <div key={field.key} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-medium text-gray-900">{field.label}</h3>
              {editing !== field.key && (
                <button
                  onClick={() => setEditing(field.key)}
                  className="px-3 py-1 text-sm text-indigo-600 bg-indigo-50 rounded hover:bg-indigo-100"
                >
                  {formData[field.key as keyof typeof formData] ? 'Edit' : 'Add'}
                </button>
              )}
            </div>

            {editing === field.key ? (
              <div className="space-y-3">
                <textarea
                  value={formData[field.key as keyof typeof formData]}
                  onChange={(e) =>
                    setFormData({ ...formData, [field.key]: e.target.value })
                  }
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder={field.placeholder}
                />
                <div className="flex items-center justify-end gap-3">
                  <button
                    onClick={() => {
                      setEditing(null);
                      setFormData({
                        past_medical_history: patient.past_medical_history || '',
                        past_surgical_history: patient.past_surgical_history || '',
                        family_history: patient.family_history || '',
                        social_history: patient.social_history || '',
                      });
                    }}
                    className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => handleSave(field.key)}
                    disabled={saving}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
                  >
                    {saving ? 'Saving...' : 'Save'}
                  </button>
                </div>
              </div>
            ) : (
              <div>
                {formData[field.key as keyof typeof formData] ? (
                  <p className="text-gray-900 whitespace-pre-wrap">
                    {formData[field.key as keyof typeof formData]}
                  </p>
                ) : (
                  <p className="text-gray-400 italic">No {field.label.toLowerCase()} recorded</p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

