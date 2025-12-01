/**
 * Patient service for API calls
 */
import { apiClient } from './apiClient';

export interface Patient {
  id: string;
  name: string;
  age: number;
  sex: string;
  primary_diagnosis: string | null;
  past_medical_history?: string | null;
  past_surgical_history?: string | null;
  family_history?: string | null;
  social_history?: string | null;
  // Finnish identification
  henkilotunnus?: string | null;
  kela_card_number?: string | null;
  date_of_birth?: string | null;
  // Finnish healthcare eligibility
  kela_eligible?: boolean | null;
  municipality_code?: string | null;
  municipality_name?: string | null;
  primary_care_center?: string | null;
  // International patients (EU/EEA)
  ehic_number?: string | null;
  ehic_country_code?: string | null;
  ehic_expiry_date?: string | null;
  is_temporary_visitor?: boolean | null;
  // Contact information
  phone?: string | null;
  email?: string | null;
  address?: string | null;
  postal_code?: string | null;
  city?: string | null;
  // Emergency contact
  emergency_contact_name?: string | null;
  emergency_contact_phone?: string | null;
  emergency_contact_relation?: string | null;
  // Registration status
  registration_status?: string | null;
  // Insurance (for compatibility)
  insurance_provider?: string | null;
  insurance_id?: string | null;
  created_at: string;
  updated_at: string;
  // Anonymization metadata (present when data is anonymized)
  is_anonymized?: boolean;
  anonymization_note?: string;
}

export interface PatientListResponse {
  items: Patient[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PatientFilters {
  name?: string;
  age_min?: number;
  age_max?: number;
  sex?: string;
  diagnosis?: string;
  page?: number;
  page_size?: number;
}

export interface PatientCreate {
  name: string;
  age: number;
  sex: 'M' | 'F' | 'Other';
  primary_diagnosis?: string | null;
  // Finnish identification (optional)
  henkilotunnus?: string | null;
  kela_card_number?: string | null;
  date_of_birth?: string | null;
  // Finnish healthcare eligibility
  kela_eligible?: boolean | null;
  municipality_code?: string | null;
  municipality_name?: string | null;
  primary_care_center?: string | null;
  // International patients (EU/EEA)
  ehic_number?: string | null;
  ehic_country_code?: string | null;
  ehic_expiry_date?: string | null;
  is_temporary_visitor?: boolean | null;
  // Contact information
  phone?: string | null;
  email?: string | null;
  address?: string | null;
  postal_code?: string | null;
  city?: string | null;
  // Emergency contact
  emergency_contact_name?: string | null;
  emergency_contact_phone?: string | null;
  emergency_contact_relation?: string | null;
  // Registration status
  registration_status?: string | null;
  // Insurance (for compatibility)
  insurance_provider?: string | null;
  insurance_id?: string | null;
}

export const patientService = {
  /**
   * Get list of patients with pagination and filtering
   */
  getPatients: async (filters?: PatientFilters): Promise<PatientListResponse> => {
    const params = new URLSearchParams();
    
    if (filters) {
      if (filters.page) params.append('page', filters.page.toString());
      if (filters.page_size) params.append('page_size', filters.page_size.toString());
      if (filters.name) params.append('name', filters.name);
      if (filters.age_min !== undefined) params.append('age_min', filters.age_min.toString());
      if (filters.age_max !== undefined) params.append('age_max', filters.age_max.toString());
      if (filters.sex) params.append('sex', filters.sex);
      if (filters.diagnosis) params.append('diagnosis', filters.diagnosis);
    }

    const queryString = params.toString();
    const url = queryString ? `/patients?${queryString}` : '/patients';
    const response = await apiClient.get<PatientListResponse>(url);
    return response.data;
  },

  /**
   * Get patient by ID
   */
  getPatient: async (patientId: string): Promise<Patient> => {
    const response = await apiClient.get<Patient>(`/patients/${patientId}`);
    return response.data;
  },

  /**
   * Create a new patient
   */
  createPatient: async (patientData: PatientCreate): Promise<Patient> => {
    const response = await apiClient.post<Patient>('/patients', patientData);
    return response.data;
  },

  /**
   * Update a patient
   */
  updatePatient: async (patientId: string, patientData: Partial<Patient>): Promise<Patient> => {
    const response = await apiClient.put<Patient>(`/patients/${patientId}`, patientData);
    return response.data;
  },

  /**
   * Get metadata for multiple patients in bulk (optimizes dashboard loading)
   * Uses POST to avoid URL length limits with many patient IDs
   */
  getPatientsMetadata: async (patientIds: string[]): Promise<Record<string, {
    has_vitals: boolean;
    has_images: boolean;
    risk_level: 'routine' | 'needs_attention' | 'high_concern';
    image_count: number;
  }>> => {
    const response = await apiClient.post<Record<string, any>>(`/patients/metadata`, patientIds);
    return response.data;
  },
};

