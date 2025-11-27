/**
 * Allergy service for API calls
 */
import { apiClient } from './apiClient';

export interface Allergy {
  id: string;
  patient_id: string;
  allergen: string;
  allergen_type: string | null;
  severity: string | null;
  reaction: string | null;
  onset_date: string | null;
  notes: string | null;
  status: 'active' | 'resolved' | 'unconfirmed';
  created_at: string;
  updated_at: string;
}

export interface AllergyCreate {
  patient_id: string;
  allergen: string;
  allergen_type?: string | null;
  severity?: string | null;
  reaction?: string | null;
  onset_date?: string | null;
  notes?: string | null;
  status?: 'active' | 'resolved' | 'unconfirmed';
}

export interface AllergyUpdate {
  allergen?: string;
  allergen_type?: string | null;
  severity?: string | null;
  reaction?: string | null;
  onset_date?: string | null;
  notes?: string | null;
  status?: 'active' | 'resolved' | 'unconfirmed';
}

export const allergyService = {
  /**
   * Get allergies for a patient
   */
  getPatientAllergies: async (patientId: string, status?: string): Promise<Allergy[]> => {
    const params = status ? `?status=${status}` : '';
    const response = await apiClient.get<Allergy[]>(`/allergies/patient/${patientId}${params}`);
    return response.data;
  },

  /**
   * Get allergy by ID
   */
  getAllergy: async (allergyId: string): Promise<Allergy> => {
    const response = await apiClient.get<Allergy>(`/allergies/${allergyId}`);
    return response.data;
  },

  /**
   * Create a new allergy
   */
  createAllergy: async (allergyData: AllergyCreate): Promise<Allergy> => {
    const response = await apiClient.post<Allergy>('/allergies', allergyData);
    return response.data;
  },

  /**
   * Update an allergy
   */
  updateAllergy: async (allergyId: string, allergyData: AllergyUpdate): Promise<Allergy> => {
    const response = await apiClient.put<Allergy>(`/allergies/${allergyId}`, allergyData);
    return response.data;
  },

  /**
   * Delete an allergy
   */
  deleteAllergy: async (allergyId: string): Promise<void> => {
    await apiClient.delete(`/allergies/${allergyId}`);
  },
};

