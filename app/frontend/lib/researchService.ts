/**
 * Research service for fetching analytics and metrics
 */
import { apiClient } from './apiClient';

export interface MetricsSummary {
  period_days: number;
  start_date: string;
  end_date: string;
  total_events: number;
  by_category: Record<string, number>;
  by_type: Record<string, number>;
  by_action_type: Record<string, number>;
}

export interface SuggestionMetrics {
  total: number;
  accepted: number;
  ignored: number;
  not_relevant: number;
  accept_rate: number;
  ignore_rate: number;
  not_relevant_rate: number;
}

export interface NavigationMetrics {
  section_visits: Record<string, number>;
  visit_percentages: Record<string, number>;
  total_navigations: number;
}

export interface AdaptationMetrics {
  total_adaptations: number;
  adaptations_by_user: Record<string, number>;
  adaptations_by_type: Record<string, number>;
}

export interface ModelPerformanceMetrics {
  total_outputs: number;
  outputs_by_model: Record<string, number>;
  average_confidence: Record<string, number>;
}

export const researchService = {
  /**
   * Get audit log summary statistics
   */
  getAuditSummary: async (days: number = 7): Promise<MetricsSummary> => {
    const response = await apiClient.get('/audit/summary', {
      params: { days },
    });
    const summary = response.data;
    
    // Calculate period-based metrics
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    
    return {
      period_days: days,
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString(),
      total_events: summary.total_logs || 0,
      by_category: {
        user_activity: summary.user_actions_count || 0,
        ai_suggestion: summary.ai_suggestions_count || 0,
        system_adaptation: summary.adaptation_events_count || 0,
      },
      by_type: {},
      by_action_type: {},
    };
  },

  /**
   * Get suggestion metrics
   */
  getSuggestionMetrics: async (days: number = 30): Promise<SuggestionMetrics> => {
    // Get suggestion actions from monitor endpoint
    const response = await apiClient.get('/monitor/suggestion-actions', {
      params: { days },
    });
    const actions = response.data.actions || [];
    
    const total = actions.length;
    const accepted = actions.filter((a: any) => a.action === 'accept').length;
    const ignored = actions.filter((a: any) => a.action === 'ignore').length;
    const not_relevant = actions.filter((a: any) => a.action === 'not_relevant').length;
    
    return {
      total,
      accepted,
      ignored,
      not_relevant,
      accept_rate: total > 0 ? (accepted / total) * 100 : 0,
      ignore_rate: total > 0 ? (ignored / total) * 100 : 0,
      not_relevant_rate: total > 0 ? (not_relevant / total) * 100 : 0,
    };
  },

  /**
   * Get navigation patterns/metrics
   */
  getNavigationMetrics: async (days: number = 30): Promise<NavigationMetrics> => {
    const response = await apiClient.get('/monitor/navigation-patterns', {
      params: { days },
    });
    const patterns = response.data.patterns || [];
    
    const section_visits: Record<string, number> = {};
    patterns.forEach((p: any) => {
      const section = p.to_section;
      if (section) {
        section_visits[section] = (section_visits[section] || 0) + 1;
      }
    });
    
    const total = Object.values(section_visits).reduce((sum, count) => sum + count, 0);
    const visit_percentages: Record<string, number> = {};
    Object.keys(section_visits).forEach((section) => {
      visit_percentages[section] = total > 0 ? (section_visits[section] / total) * 100 : 0;
    });
    
    return {
      section_visits,
      visit_percentages,
      total_navigations: total,
    };
  },

  /**
   * Get adaptation metrics
   */
  getAdaptationMetrics: async (days: number = 30): Promise<AdaptationMetrics> => {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    
    const response = await apiClient.get('/audit/adaptations', {
      params: {
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
        page: 1,
        page_size: 1000,
      },
    });
    
    const adaptations = response.data.items || [];
    const adaptations_by_user: Record<string, number> = {};
    const adaptations_by_type: Record<string, number> = {};
    
    adaptations.forEach((adaptation: any) => {
      const userId = adaptation.user_id;
      if (userId) {
        adaptations_by_user[userId] = (adaptations_by_user[userId] || 0) + 1;
      }
      
      const density = adaptation.metadata?.suggestion_density || 'medium';
      adaptations_by_type[density] = (adaptations_by_type[density] || 0) + 1;
    });
    
    return {
      total_adaptations: adaptations.length,
      adaptations_by_user,
      adaptations_by_type,
    };
  },

  /**
   * Get model performance metrics
   */
  getModelPerformanceMetrics: async (days: number = 30): Promise<ModelPerformanceMetrics> => {
    const response = await apiClient.get('/monitor/model-outputs', {
      params: { days },
    });
    const outputs = response.data.outputs || [];
    
    const outputs_by_model: Record<string, number> = {};
    const confidence_sum: Record<string, number> = {};
    const confidence_count: Record<string, number> = {};
    
    outputs.forEach((output: any) => {
      const modelType = output.model_type || 'unknown';
      outputs_by_model[modelType] = (outputs_by_model[modelType] || 0) + 1;
      
      // Try to extract confidence from output_data
      const outputData = output.output_data || {};
      if (outputData.score !== undefined || outputData.confidence !== undefined) {
        const confidence = outputData.score || outputData.confidence || 0;
        confidence_sum[modelType] = (confidence_sum[modelType] || 0) + confidence;
        confidence_count[modelType] = (confidence_count[modelType] || 0) + 1;
      }
    });
    
    const average_confidence: Record<string, number> = {};
    Object.keys(outputs_by_model).forEach((modelType) => {
      if (confidence_count[modelType] > 0) {
        average_confidence[modelType] = confidence_sum[modelType] / confidence_count[modelType];
      }
    });
    
    return {
      total_outputs: outputs.length,
      outputs_by_model,
      average_confidence,
    };
  },

  /**
   * Export research data as JSON
   */
  exportResearchData: async (days: number = 30): Promise<any> => {
    const [summary, suggestions, navigation, adaptations, modelPerformance] = await Promise.all([
      researchService.getAuditSummary(days),
      researchService.getSuggestionMetrics(days),
      researchService.getNavigationMetrics(days),
      researchService.getAdaptationMetrics(days),
      researchService.getModelPerformanceMetrics(days),
    ]);
    
    return {
      export_date: new Date().toISOString(),
      period_days: days,
      summary,
      suggestion_metrics: suggestions,
      navigation_metrics: navigation,
      adaptation_metrics: adaptations,
      model_performance: modelPerformance,
    };
  },
};

