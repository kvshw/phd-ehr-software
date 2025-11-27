/**
 * Problem service for API calls
 */
import { apiClient } from './apiClient';

export interface Problem {
  id: string;
  patient_id: string;
  problem_name: string;
  icd_code: string | null;
  status: 'active' | 'resolved' | 'chronic' | 'inactive';
  onset_date: string | null;
  resolved_date: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProblemCreate {
  patient_id: string;
  problem_name: string;
  icd_code?: string | null;
  status?: 'active' | 'resolved' | 'chronic' | 'inactive';
  onset_date?: string | null;
  resolved_date?: string | null;
  notes?: string | null;
}

export interface ProblemUpdate {
  problem_name?: string;
  icd_code?: string | null;
  status?: 'active' | 'resolved' | 'chronic' | 'inactive';
  onset_date?: string | null;
  resolved_date?: string | null;
  notes?: string | null;
}

export const problemService = {
  /**
   * Get problems for a patient
   */
  getPatientProblems: async (patientId: string, status?: string): Promise<Problem[]> => {
    const params = status ? `?status=${status}` : '';
    const response = await apiClient.get<Problem[]>(`/problems/patient/${patientId}${params}`);
    return response.data;
  },

  /**
   * Get problem by ID
   */
  getProblem: async (problemId: string): Promise<Problem> => {
    const response = await apiClient.get<Problem>(`/problems/${problemId}`);
    return response.data;
  },

  /**
   * Create a new problem
   */
  createProblem: async (problemData: ProblemCreate): Promise<Problem> => {
    const response = await apiClient.post<Problem>('/problems', problemData);
    return response.data;
  },

  /**
   * Update a problem
   */
  updateProblem: async (problemId: string, problemData: ProblemUpdate): Promise<Problem> => {
    const response = await apiClient.put<Problem>(`/problems/${problemId}`, problemData);
    return response.data;
  },

  /**
   * Delete a problem
   */
  deleteProblem: async (problemId: string): Promise<void> => {
    await apiClient.delete(`/problems/${problemId}`);
  },
};

