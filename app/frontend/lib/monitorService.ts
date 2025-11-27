/**
 * Monitor service for logging user actions and system events
 * Part of MAPE-K adaptation engine
 */
import { apiClient } from './apiClient';

export interface LogNavigationParams {
  patientId?: string;
  fromSection?: string;
  toSection: string;
}

export interface LogSuggestionActionParams {
  suggestionId: string;
  action: 'accept' | 'ignore' | 'not_relevant';
  suggestionType?: string;
  suggestionSource?: string;
  patientId?: string;
}

export interface LogRiskChangeParams {
  patientId: string;
  newRiskLevel: string;
  previousRiskLevel?: string;
  riskScore?: number;
}

export const monitorService = {
  /**
   * Log user navigation between sections
   */
  logNavigation: async (params: LogNavigationParams): Promise<void> => {
    try {
      await apiClient.post('/monitor/log-navigation', {
        patient_id: params.patientId || null,
        from_section: params.fromSection || null,
        to_section: params.toSection,
      });
    } catch (err) {
      // Don't throw - monitoring should not break user experience
      console.error('Failed to log navigation:', err);
    }
  },

  /**
   * Log user interaction with a suggestion
   */
  logSuggestionAction: async (params: LogSuggestionActionParams): Promise<void> => {
    try {
      await apiClient.post('/monitor/log-suggestion-action', {
        suggestion_id: params.suggestionId,
        action: params.action,
        suggestion_type: params.suggestionType,
        suggestion_source: params.suggestionSource,
        patient_id: params.patientId || null,
      });
    } catch (err) {
      // Don't throw - monitoring should not break user experience
      console.error('Failed to log suggestion action:', err);
    }
  },

  /**
   * Log patient risk level change
   */
  logRiskChange: async (params: LogRiskChangeParams): Promise<void> => {
    try {
      await apiClient.post('/monitor/log-risk-change', {
        patient_id: params.patientId,
        new_risk_level: params.newRiskLevel,
        previous_risk_level: params.previousRiskLevel,
        risk_score: params.riskScore,
      });
    } catch (err) {
      // Don't throw - monitoring should not break user experience
      console.error('Failed to log risk change:', err);
    }
  },
};

