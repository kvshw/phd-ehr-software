/**
 * Adaptation service for fetching and applying MAPE-K adaptation plans
 */
import { apiClient } from './apiClient';

export interface AdaptationPlan {
  order: string[];
  suggestion_density: 'low' | 'medium' | 'high';
  flags?: {
    prioritized_section?: string;
    high_ignore_rate?: boolean;
    risk_escalated?: boolean;
    escalation_count?: number;
    [key: string]: any;
  };
  explanation?: string;
}

export interface AdaptationResponse {
  id: string;
  user_id: string;
  patient_id: string | null;
  plan_json: AdaptationPlan;
  timestamp: string;
}

export const adaptationService = {
  /**
   * Get the latest adaptation plan for the current user
   */
  getLatestAdaptation: async (patientId?: string): Promise<AdaptationResponse | null> => {
    try {
      const params = patientId ? `?patient_id=${patientId}` : '';
      const response = await apiClient.get<AdaptationResponse>(`/mape-k/adaptation/latest${params}`, {
        // Suppress error logging for 404s (expected when no plan exists yet)
        validateStatus: (status) => status < 500,
      });
      
      // Return null for 404 (no plan exists yet) - this is expected behavior
      if (response.status === 404 || !response.data) {
        return null;
      }
      
      return response.data;
    } catch (err: any) {
      // Only log unexpected errors (not 404s)
      // The interceptor should handle 404s, but catch any other errors
      if (err.response?.status !== 404) {
        console.error('Failed to fetch adaptation plan:', err);
      }
      return null;
    }
  },

  /**
   * Trigger analysis and plan generation for the current user
   */
  generatePlan: async (patientId?: string): Promise<AdaptationResponse> => {
    const params = patientId ? `?patient_id=${patientId}` : '';
    const response = await apiClient.post<AdaptationResponse>(`/mape-k/plan${params}`);
    return response.data;
  },
};

