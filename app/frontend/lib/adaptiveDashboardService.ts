/**
 * Adaptive Dashboard Service
 * Fetches MAPE-K adaptation plans and applies them to the dashboard
 * Enables self-adaptive UI based on actual user behavior
 */
import { apiClient } from './apiClient';

export interface DashboardPlan {
  plan_type: string;
  version: string;
  feature_priority: Array<{
    id: string;
    position: number;
    size: 'large' | 'medium' | 'small';
    usage_count: number;
    daily_average: number;
    source?: string; // 'usage' or 'specialty_default'
  }>;
  hidden_features: string[];
  quick_stats: Record<string, any>;
  patient_list: {
    sort_by: string;
    default_filters: Record<string, any>;
    items_per_page: number;
  };
  explanation: string;
}

export interface DashboardAnalysis {
  feature_frequencies: Record<string, number>;
  feature_daily_averages: Record<string, number>;
  most_used_features: string[];
  least_used_features: string[];
  workflow_patterns: {
    common_sequences: Array<{
      sequence: string[];
      frequency: number;
    }>;
  };
  time_of_day_patterns: Record<string, Record<string, number>>;
}

export const adaptiveDashboardService = {
  /**
   * Get dashboard usage analysis
   * Shows what features the user actually uses
   */
  getAnalysis: async (): Promise<DashboardAnalysis> => {
    try {
      const response = await apiClient.get<DashboardAnalysis>('/mape-k/dashboard/analyze');
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch dashboard analysis:', err);
      // Return empty analysis on error
      return {
        feature_frequencies: {},
        feature_daily_averages: {},
        most_used_features: [],
        least_used_features: [],
        workflow_patterns: { common_sequences: [] },
        time_of_day_patterns: {},
      };
    }
  },

  /**
   * Get adaptive dashboard plan
   * Returns how the dashboard should be laid out based on usage
   */
  getPlan: async (): Promise<DashboardPlan | null> => {
    try {
      const response = await apiClient.get<DashboardPlan>('/mape-k/dashboard/plan');
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch dashboard plan:', err);
      return null;
    }
  },

  /**
   * Get both analysis and plan in one call
   */
  getAnalysisAndPlan: async (): Promise<{ analysis: DashboardAnalysis; plan: DashboardPlan | null }> => {
    const [analysis, plan] = await Promise.all([
      adaptiveDashboardService.getAnalysis(),
      adaptiveDashboardService.getPlan(),
    ]);
    return { analysis, plan };
  },
};

