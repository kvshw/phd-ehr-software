/**
 * Medication service for API calls
 */
import { apiClient } from './apiClient';

export interface Medication {
  id: string;
  patient_id: string;
  prescriber_id: string | null;
  medication_name: string;
  generic_name: string | null;
  dosage: string | null;
  frequency: string | null;
  route: string | null;
  quantity: string | null;
  start_date: string | null;
  end_date: string | null;
  status: 'active' | 'discontinued' | 'completed';
  indication: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  // Anonymization metadata (present when data is anonymized)
  is_anonymized?: boolean;
  anonymization_note?: string;
}

export interface MedicationCreate {
  patient_id: string;
  prescriber_id?: string | null;
  medication_name: string;
  generic_name?: string | null;
  dosage?: string | null;
  frequency?: string | null;
  route?: string | null;
  quantity?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  status?: 'active' | 'discontinued' | 'completed';
  indication?: string | null;
  notes?: string | null;
}

export interface MedicationUpdate {
  medication_name?: string;
  generic_name?: string | null;
  dosage?: string | null;
  frequency?: string | null;
  route?: string | null;
  quantity?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  status?: 'active' | 'discontinued' | 'completed';
  indication?: string | null;
  notes?: string | null;
}

export const medicationService = {
  /**
   * Get medications for a patient
   */
  getPatientMedications: async (patientId: string, status?: string): Promise<Medication[]> => {
    const params = status ? `?status=${status}` : '';
    const response = await apiClient.get<Medication[]>(`/medications/patient/${patientId}${params}`);
    return response.data;
  },

  /**
   * Get medication by ID
   */
  getMedication: async (medicationId: string): Promise<Medication> => {
    const response = await apiClient.get<Medication>(`/medications/${medicationId}`);
    return response.data;
  },

  /**
   * Create a new medication
   */
  createMedication: async (medicationData: MedicationCreate): Promise<Medication> => {
    const response = await apiClient.post<Medication>('/medications', medicationData);
    return response.data;
  },

  /**
   * Update a medication
   */
  updateMedication: async (medicationId: string, medicationData: MedicationUpdate): Promise<Medication> => {
    const response = await apiClient.put<Medication>(`/medications/${medicationId}`, medicationData);
    return response.data;
  },

  /**
   * Delete a medication
   */
  deleteMedication: async (medicationId: string): Promise<void> => {
    await apiClient.delete(`/medications/${medicationId}`);
  },
};

