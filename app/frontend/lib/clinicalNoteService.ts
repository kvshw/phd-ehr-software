/**
 * Clinical Note service for API calls
 */
import { apiClient } from './apiClient';

export interface ClinicalNote {
  id: string;
  patient_id: string;
  user_id: string;
  note_type: string;
  encounter_date: string;
  chief_complaint: string | null;
  history_of_present_illness: string | null;
  review_of_systems: string | null;
  physical_exam: string | null;
  assessment: string | null;
  plan: string | null;
  note_text: string | null;
  created_at: string;
  updated_at: string;
}

export interface ClinicalNoteCreate {
  patient_id: string;
  note_type?: string;
  encounter_date?: string;
  chief_complaint?: string | null;
  history_of_present_illness?: string | null;
  review_of_systems?: string | null;
  physical_exam?: string | null;
  assessment?: string | null;
  plan?: string | null;
  note_text?: string | null;
}

export interface ClinicalNoteUpdate {
  note_type?: string;
  encounter_date?: string;
  chief_complaint?: string | null;
  history_of_present_illness?: string | null;
  review_of_systems?: string | null;
  physical_exam?: string | null;
  assessment?: string | null;
  plan?: string | null;
  note_text?: string | null;
}

export const clinicalNoteService = {
  /**
   * Get clinical notes for a patient
   */
  getPatientNotes: async (patientId: string, limit?: number, offset?: number): Promise<ClinicalNote[]> => {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    if (offset) params.append('offset', offset.toString());
    const queryString = params.toString();
    const url = queryString ? `/clinical-notes/patient/${patientId}?${queryString}` : `/clinical-notes/patient/${patientId}`;
    const response = await apiClient.get<ClinicalNote[]>(url);
    return response.data;
  },

  /**
   * Get note by ID
   */
  getNote: async (noteId: string): Promise<ClinicalNote> => {
    const response = await apiClient.get<ClinicalNote>(`/clinical-notes/${noteId}`);
    return response.data;
  },

  /**
   * Create a new clinical note
   */
  createNote: async (noteData: ClinicalNoteCreate): Promise<ClinicalNote> => {
    const response = await apiClient.post<ClinicalNote>('/clinical-notes', noteData);
    return response.data;
  },

  /**
   * Update a clinical note
   */
  updateNote: async (noteId: string, noteData: ClinicalNoteUpdate): Promise<ClinicalNote> => {
    const response = await apiClient.put<ClinicalNote>(`/clinical-notes/${noteId}`, noteData);
    return response.data;
  },

  /**
   * Delete a clinical note
   */
  deleteNote: async (noteId: string): Promise<void> => {
    await apiClient.delete(`/clinical-notes/${noteId}`);
  },
};

