/**
 * Admin service for system management
 */
import { apiClient } from './apiClient';

export interface User {
  id: string;
  email: string;
  role: 'clinician' | 'researcher' | 'admin';
  created_at?: string;
}

export interface UserCreate {
  email: string;
  password: string;
  role: 'clinician' | 'researcher' | 'admin';
}

export interface UserUpdate {
  email?: string;
  role?: 'clinician' | 'researcher' | 'admin';
  password?: string;
}

export interface SystemStatus {
  backend: {
    status: 'healthy' | 'unhealthy';
    version: string;
  };
  database: {
    status: 'connected' | 'disconnected';
  };
  model_services: {
    vital_risk: { status: 'active' | 'inactive'; version: string };
    image_analysis: { status: 'active' | 'inactive'; version: string };
    diagnosis_helper: { status: 'active' | 'inactive'; version: string };
  };
}

export interface AdaptationConfig {
  navigation_threshold: number;
  ignore_rate_threshold: number;
  acceptance_rate_threshold: number;
  risk_escalation_threshold: number;
}

export const adminService = {
  /**
   * Get all users
   */
  getUsers: async (): Promise<User[]> => {
    const response = await apiClient.get('/admin/users');
    return response.data;
  },

  /**
   * Create a new user
   */
  createUser: async (userData: UserCreate): Promise<User> => {
    const response = await apiClient.post('/admin/users', userData);
    return response.data;
  },

  /**
   * Update a user
   */
  updateUser: async (userId: string, userData: UserUpdate): Promise<User> => {
    const response = await apiClient.put(`/admin/users/${userId}`, userData);
    return response.data;
  },

  /**
   * Delete a user
   */
  deleteUser: async (userId: string): Promise<void> => {
    await apiClient.delete(`/admin/users/${userId}`);
  },

  /**
   * Get system status
   */
  getSystemStatus: async (): Promise<SystemStatus> => {
    const response = await apiClient.get('/admin/system-status');
    return response.data;
  },

  /**
   * Get adaptation configuration
   */
  getAdaptationConfig: async (): Promise<AdaptationConfig> => {
    const response = await apiClient.get('/admin/adaptation-config');
    return response.data;
  },

  /**
   * Update adaptation configuration
   */
  updateAdaptationConfig: async (config: AdaptationConfig): Promise<AdaptationConfig> => {
    const response = await apiClient.put('/admin/adaptation-config', config);
    return response.data;
  },

  /**
   * Generate synthetic data
   */
  generateSyntheticData: async (options: {
    num_patients?: number;
    num_vitals_per_patient?: number;
    num_labs_per_patient?: number;
    num_images_per_patient?: number;
  }): Promise<{ message: string; generated: any }> => {
    const response = await apiClient.post('/admin/generate-synthetic-data', options);
    return response.data;
  },
};

