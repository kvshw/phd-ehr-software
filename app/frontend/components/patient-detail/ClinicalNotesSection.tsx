/**
 * Clinical Notes section component
 * Displays and manages SOAP notes
 */
'use client';

import { useState, useEffect } from 'react';
import { clinicalNoteService, ClinicalNote, ClinicalNoteCreate } from '@/lib/clinicalNoteService';

interface ClinicalNotesSectionProps {
  patientId: string;
}

export function ClinicalNotesSection({ patientId }: ClinicalNotesSectionProps) {
  const [notes, setNotes] = useState<ClinicalNote[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState<ClinicalNoteCreate>({
    patient_id: patientId,
    note_type: 'progress',
    encounter_date: new Date().toISOString(),
    chief_complaint: '',
    history_of_present_illness: '',
    review_of_systems: '',
    physical_exam: '',
    assessment: '',
    plan: '',
    note_text: '',
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchNotes();
  }, [patientId]);

  const fetchNotes = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await clinicalNoteService.getPatientNotes(patientId, 50, 0);
      setNotes(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load clinical notes');
      console.error('Error fetching notes:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      await clinicalNoteService.createNote(formData);
      setShowAddForm(false);
      setFormData({
        patient_id: patientId,
        note_type: 'progress',
        encounter_date: new Date().toISOString(),
        chief_complaint: '',
        history_of_present_illness: '',
        review_of_systems: '',
        physical_exam: '',
        assessment: '',
        plan: '',
        note_text: '',
      });
      fetchNotes();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create note');
      console.error('Error creating note:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (noteId: string) => {
    if (!confirm('Are you sure you want to delete this note?')) {
      return;
    }

    try {
      await clinicalNoteService.deleteNote(noteId);
      fetchNotes();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete note');
      console.error('Error deleting note:', err);
    }
  };

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
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900">Clinical Notes</h2>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors text-sm"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Note
        </button>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}

      {/* Add Form */}
      {showAddForm && (
        <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Create New Clinical Note</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Note Type</label>
                <select
                  value={formData.note_type}
                  onChange={(e) => setFormData({ ...formData, note_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                >
                  <option value="progress">Progress Note</option>
                  <option value="admission">Admission Note</option>
                  <option value="discharge">Discharge Note</option>
                  <option value="consult">Consultation Note</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Encounter Date</label>
                <input
                  type="datetime-local"
                  value={formData.encounter_date ? new Date(formData.encounter_date).toISOString().slice(0, 16) : ''}
                  onChange={(e) => setFormData({ ...formData, encounter_date: new Date(e.target.value).toISOString() })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                />
              </div>
            </div>

            {/* SOAP Structure */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Chief Complaint (CC)</label>
                <textarea
                  value={formData.chief_complaint || ''}
                  onChange={(e) => setFormData({ ...formData, chief_complaint: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                  placeholder="Patient's main complaint"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">History of Present Illness (HPI)</label>
                <textarea
                  value={formData.history_of_present_illness || ''}
                  onChange={(e) => setFormData({ ...formData, history_of_present_illness: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                  placeholder="Detailed history of the current problem"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Review of Systems (ROS)</label>
                <textarea
                  value={formData.review_of_systems || ''}
                  onChange={(e) => setFormData({ ...formData, review_of_systems: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                  placeholder="Systematic review of body systems"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Physical Examination</label>
                <textarea
                  value={formData.physical_exam || ''}
                  onChange={(e) => setFormData({ ...formData, physical_exam: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                  placeholder="Physical examination findings"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Assessment</label>
                <textarea
                  value={formData.assessment || ''}
                  onChange={(e) => setFormData({ ...formData, assessment: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                  placeholder="Clinical assessment and diagnosis"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Plan</label>
                <textarea
                  value={formData.plan || ''}
                  onChange={(e) => setFormData({ ...formData, plan: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                  placeholder="Treatment plan and follow-up"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Free-form Note (Optional)</label>
                <textarea
                  value={formData.note_text || ''}
                  onChange={(e) => setFormData({ ...formData, note_text: e.target.value })}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                  placeholder="Additional free-form notes"
                />
              </div>
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
                {submitting ? 'Creating...' : 'Create Note'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Notes List */}
      {notes.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No clinical notes recorded</p>
        </div>
      ) : (
        <div className="space-y-4">
          {notes.map((note) => (
            <div
              key={note.id}
              className="border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-indigo-100 text-indigo-800">
                      {note.note_type.replace('_', ' ').toUpperCase()}
                    </span>
                    <span className="text-sm text-gray-500">
                      {new Date(note.encounter_date).toLocaleString()}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(note.id)}
                  className="px-3 py-1 text-sm text-gray-700 bg-gray-100 rounded hover:bg-gray-200"
                >
                  Delete
                </button>
              </div>

              {/* SOAP Display */}
              <div className="space-y-3 text-sm">
                {note.chief_complaint && (
                  <div>
                    <span className="font-semibold text-gray-700">CC:</span>{' '}
                    <span className="text-gray-900">{note.chief_complaint}</span>
                  </div>
                )}
                {note.history_of_present_illness && (
                  <div>
                    <span className="font-semibold text-gray-700">HPI:</span>{' '}
                    <span className="text-gray-900">{note.history_of_present_illness}</span>
                  </div>
                )}
                {note.review_of_systems && (
                  <div>
                    <span className="font-semibold text-gray-700">ROS:</span>{' '}
                    <span className="text-gray-900">{note.review_of_systems}</span>
                  </div>
                )}
                {note.physical_exam && (
                  <div>
                    <span className="font-semibold text-gray-700">Physical Exam:</span>{' '}
                    <span className="text-gray-900">{note.physical_exam}</span>
                  </div>
                )}
                {note.assessment && (
                  <div>
                    <span className="font-semibold text-gray-700">Assessment:</span>{' '}
                    <span className="text-gray-900">{note.assessment}</span>
                  </div>
                )}
                {note.plan && (
                  <div>
                    <span className="font-semibold text-gray-700">Plan:</span>{' '}
                    <span className="text-gray-900">{note.plan}</span>
                  </div>
                )}
                {note.note_text && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-gray-900 whitespace-pre-wrap">{note.note_text}</p>
                  </div>
                )}
              </div>

              <div className="mt-3 text-xs text-gray-500">
                Created: {new Date(note.created_at).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

