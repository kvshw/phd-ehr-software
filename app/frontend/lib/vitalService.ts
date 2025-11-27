/**
 * Vital signs service for API calls
 */
import { apiClient } from './apiClient';

export interface Vital {
  id: string;
  patient_id: string;
  timestamp: string;
  hr: number | null;
  bp_sys: number | null;
  bp_dia: number | null;
  spo2: number | null;
  rr: number | null;
  temp: number | null;
  pain: number | null;
  created_at: string;
}

export interface VitalListResponse {
  items: Vital[];
  total: number;
  patient_id: string;
}

export interface VitalTimeRangeParams {
  start_time?: string;
  end_time?: string;
  limit?: number;
}

export const vitalService = {
  /**
   * Get vitals for a patient with optional time range filtering
   */
  getPatientVitals: async (
    patientId: string,
    timeRange?: VitalTimeRangeParams
  ): Promise<VitalListResponse> => {
    const params = new URLSearchParams();
    if (timeRange?.start_time) {
      params.append('start_time', timeRange.start_time);
    }
    if (timeRange?.end_time) {
      params.append('end_time', timeRange.end_time);
    }
    if (timeRange?.limit) {
      params.append('limit', timeRange.limit.toString());
    }
    
    const queryString = params.toString();
    const url = `/vitals/${patientId}${queryString ? `?${queryString}` : ''}`;
    const response = await apiClient.get<VitalListResponse>(url);
    return response.data;
  },
};

