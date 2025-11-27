/**
 * Suggestion service for API calls
 */
import { apiClient } from './apiClient';

export interface Citation {
  authors: string;
  title: string;
  journal: string;
  year: number;
  pmid?: string;
  doi?: string;
  url?: string;
}

export interface ClinicalGuideline {
  organization: string;
  title: string;
  year: number;
  url?: string;
}

export interface Suggestion {
  id: string;
  patient_id: string;
  type: string;
  text: string;
  source: string;
  explanation: string;
  confidence: number | null;
  created_at: string;
  
  // Evidence-based fields (PhD-level)
  evidence_level?: string;
  recommendation_strength?: string;
  guidelines?: ClinicalGuideline[];
  citations?: Citation[];
  mechanism?: string;
  clinical_pearl?: string;
  limitations?: string[];
}

export interface SuggestionListResponse {
  items: Suggestion[];
  total: number;
  patient_id: string;
}

export interface SuggestionFeedback {
  suggestion_id: string;
  action: 'accept' | 'ignore' | 'not_relevant';
  patient_id?: string; // Optional but recommended for proper tracking
}

export const suggestionService = {
  /**
   * Get suggestions for a patient
   */
  getPatientSuggestions: async (patientId: string): Promise<SuggestionListResponse> => {
    const response = await apiClient.get<SuggestionListResponse>(`/ai/suggestions/${patientId}`);
    return response.data;
  },

  /**
   * Submit feedback for a suggestion
   * Now stores in database and triggers self-adaptive learning
   */
  submitFeedback: async (feedback: SuggestionFeedback): Promise<void> => {
    try {
      const payload: any = {
        suggestion_id: feedback.suggestion_id,
        action: feedback.action,
      };
      
      // Include patient_id if provided (recommended for proper tracking)
      if (feedback.patient_id) {
        payload.patient_id = feedback.patient_id;
      }
      
      await apiClient.post('/feedback', payload);
    } catch (error) {
      console.error('Error submitting feedback:', error);
      throw error;
    }
  },

  /**
   * Submit detailed feedback with ratings and comments
   */
  submitDetailedFeedback: async (feedback: {
    suggestion_id: string;
    action: string;
    clinical_relevance?: number;
    agreement_rating?: number;
    explanation_quality?: number;
    would_act_on?: number;
    comment?: string;
    improvement_suggestion?: string;
  }): Promise<void> => {
    try {
      await apiClient.post('/feedback', feedback);
    } catch (error) {
      console.error('Error submitting detailed feedback:', error);
      throw error;
    }
  },

  /**
   * Generate AI suggestions for a patient
   * Triggers diagnosis helper service to generate suggestions
   */
  generateSuggestions: async (patientId: string): Promise<void> => {
    // The endpoint expects patient_id as a query parameter, not in body
    await apiClient.post(`/ai/diagnosis-helper?patient_id=${patientId}`);
  },
};

