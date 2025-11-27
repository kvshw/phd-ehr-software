/**
 * Lab results service for API calls
 */
import { apiClient } from './apiClient';

export interface Lab {
  id: string;
  patient_id: string;
  timestamp: string;
  lab_type: string;
  value: number | null;
  normal_range: string | null;
  created_at: string;
}

export interface LabListResponse {
  items: Lab[];
  total: number;
  patient_id: string;
  page?: number;
  page_size?: number;
  total_pages?: number;
}

export interface LabFilters {
  lab_type?: string;
  start_time?: string;
  end_time?: string;
  page?: number;
  page_size?: number;
}

export const labService = {
  /**
   * Get labs for a patient with optional filtering and pagination
   */
  getPatientLabs: async (
    patientId: string,
    filters?: LabFilters
  ): Promise<LabListResponse> => {
    const params = new URLSearchParams();
    
    if (filters) {
      if (filters.lab_type) params.append('lab_type', filters.lab_type);
      if (filters.start_time) params.append('start_time', filters.start_time);
      if (filters.end_time) params.append('end_time', filters.end_time);
      if (filters.page) params.append('page', filters.page.toString());
      if (filters.page_size) params.append('page_size', filters.page_size.toString());
    }

    const queryString = params.toString();
    const url = queryString ? `/labs/${patientId}?${queryString}` : `/labs/${patientId}`;
    const response = await apiClient.get<LabListResponse>(url);
    return response.data;
  },
};

