/**
 * Conversation service for API calls
 */
import { apiClient } from './apiClient';

export interface ConversationSession {
  id: string;
  patient_id: string;
  clinician_id: string;
  session_date: string;
  duration_seconds?: number;
  status: string;
  created_at: string;
}

export interface ConversationTranscript {
  id: string;
  session_id: string;
  speaker: 'doctor' | 'patient';
  text: string;
  timestamp_seconds?: number;
  confidence?: number;
  created_at: string;
}

export interface ConversationAnalysis {
  id: string;
  session_id: string;
  full_transcript: string;
  key_points?: string[];
  summary?: string;
  medical_terms?: string[];
  concerns_identified?: string[];
  recommendations?: string;
  created_at: string;
}

export interface ConversationSessionWithAnalysis extends ConversationSession {
  analysis?: ConversationAnalysis;
  transcripts?: ConversationTranscript[];
}

export const conversationService = {
  /**
   * Create a new conversation session
   */
  createSession: async (patientId: string): Promise<ConversationSession> => {
    const response = await apiClient.post<ConversationSession>('/conversations/sessions', {
      patient_id: patientId,
    });
    return response.data;
  },

  /**
   * Get a conversation session with transcripts and analysis
   */
  getSession: async (sessionId: string): Promise<ConversationSessionWithAnalysis> => {
    const response = await apiClient.get<ConversationSessionWithAnalysis>(`/conversations/sessions/${sessionId}`);
    return response.data;
  },

  /**
   * Get all sessions for a patient
   */
  getPatientSessions: async (patientId: string, limit: number = 10): Promise<ConversationSession[]> => {
    const response = await apiClient.get<ConversationSession[]>(`/conversations/patients/${patientId}/sessions`, {
      params: { limit },
    });
    return response.data;
  },

  /**
   * Add a transcript entry
   */
  addTranscript: async (data: {
    session_id: string;
    speaker: 'doctor' | 'patient';
    text: string;
    timestamp_seconds?: number;
    confidence?: number;
  }): Promise<ConversationTranscript> => {
    const response = await apiClient.post<ConversationTranscript>('/conversations/transcripts', data);
    return response.data;
  },

  /**
   * Complete a session
   */
  completeSession: async (sessionId: string, durationSeconds?: number): Promise<ConversationSession> => {
    const response = await apiClient.post<ConversationSession>(
      `/conversations/sessions/${sessionId}/complete`,
      { duration_seconds: durationSeconds }
    );
    return response.data;
  },

  /**
   * Analyze a conversation session
   */
  analyzeSession: async (sessionId: string, useAI: boolean = true): Promise<ConversationAnalysis> => {
    const response = await apiClient.post<ConversationAnalysis>(
      `/conversations/sessions/${sessionId}/analyze?use_ai=${useAI}`,
      {}
    );
    return response.data;
  },
};

