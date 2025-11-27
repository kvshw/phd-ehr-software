/**
 * Imaging service for API calls
 */
import { apiClient } from './apiClient';

export interface Imaging {
  id: string;
  patient_id: string;
  type: string;
  file_path: string;
  created_at: string;
}

export interface ImagingListResponse {
  items: Imaging[];
  total: number;
  patient_id: string;
}

export const imagingService = {
  /**
   * Get images for a patient
   */
  getPatientImages: async (patientId: string): Promise<ImagingListResponse> => {
    const response = await apiClient.get<ImagingListResponse>(`/imaging/${patientId}`);
    return response.data;
  },
};

