/**
 * XAI (Explainable AI) Service
 * Frontend service for fetching AI explanations
 */

import { apiClient } from './apiClient';

export interface FeatureImportance {
  feature: string;
  value: any;
  unit: string;
  importance: number;
  direction: 'positive' | 'negative' | 'neutral';
  normal_range: string;
  explanation: string;
  adjusted_importance?: number;
}

export interface LocalExplanationFactor {
  condition: string;
  rule: string;
  weight: number;
  met: boolean;
}

export interface LocalExplanation {
  model_type: string;
  local_accuracy: number;
  key_factors: LocalExplanationFactor[];
  interpretation: string;
  simplification_note: string;
}

export interface CounterfactualChange {
  feature: string;
  current_value: any;
  target_value: any;
  unit: string;
  change_needed: number;
  intervention: string;
  timeline: string;
}

export interface CounterfactualExplanation {
  scenario: string;
  changes_needed: CounterfactualChange[];
  minimum_changes: number;
  feasibility: string;
  clinical_note: string;
}

export interface ContrastiveAlternative {
  alternative: string;
  why_not_chosen: string;
  key_difference: string;
}

export interface ContrastiveExplanation {
  question: string;
  alternatives_considered: ContrastiveAlternative[];
  distinguishing_factors: Array<{ factor: string; explanation: string }>;
}

export interface DecisionStep {
  step: number;
  action: string;
  description: string;
  outcome: string;
  data_used?: string[];
  features_extracted?: number;
  risk_factors_found?: string[];
  top_contributors?: string[];
  thresholds_exceeded?: number;
  suggestion?: string;
}

export interface ConfidenceComponent {
  feature: string;
  contribution: number;
  percentage: number;
}

export interface ConfidenceBreakdown {
  base_confidence: number;
  total_confidence: number;
  components: ConfidenceComponent[];
  calculation_method: string;
  formula: string;
}

export interface XAIExplanation {
  suggestion_id: string;
  patient_id: string;
  generated_at: string;
  feature_importance: FeatureImportance[];
  local_explanation: LocalExplanation;
  counterfactual: CounterfactualExplanation;
  contrastive: ContrastiveExplanation;
  decision_path: DecisionStep[];
  confidence_breakdown: ConfidenceBreakdown;
  summary: string;
}

export interface QuickXAIResponse {
  suggestion_id: string;
  top_features: Array<{
    feature: string;
    value: any;
    unit: string;
    importance: number;
    direction: string;
  }>;
  key_insight: string;
  confidence_explanation: string;
  action_rationale: string;
}

export interface DecisionFactors {
  suggestion_id: string;
  suggestion_text: string;
  confidence: number;
  decision_factors: Array<{
    factor: string;
    value: string;
    impact: 'High' | 'Moderate' | 'Low';
    direction: string;
    explanation: string;
  }>;
  total_factors_analyzed: number;
  key_insight: string;
}

class XAIService {
  /**
   * Get comprehensive XAI explanation for a suggestion
   */
  async getExplanation(suggestionId: string): Promise<XAIExplanation> {
    const response = await apiClient.get(`/xai/explain/${suggestionId}`);
    return response.data;
  }

  /**
   * Get quick XAI summary for inline display
   */
  async getQuickExplanation(suggestionId: string): Promise<QuickXAIResponse> {
    const response = await apiClient.get(`/xai/quick/${suggestionId}`);
    return response.data;
  }

  /**
   * Get decision factors for a suggestion
   */
  async getDecisionFactors(suggestionId: string): Promise<DecisionFactors> {
    const response = await apiClient.get(`/xai/decision-factors/${suggestionId}`);
    return response.data;
  }

  /**
   * Get feature importance for a patient
   */
  async getPatientFeatureImportance(
    patientId: string,
    suggestionType?: string
  ): Promise<{
    patient_id: string;
    generated_at: string;
    feature_importance: FeatureImportance[];
    patient_summary: {
      age: number | null;
      risk_factors: string[];
      vitals_available: boolean;
      labs_available: boolean;
    };
  }> {
    const params = suggestionType ? `?suggestion_type=${suggestionType}` : '';
    const response = await apiClient.get(`/xai/feature-importance/${patientId}${params}`);
    return response.data;
  }

  /**
   * Get comparison view for a suggestion
   */
  async getSuggestionComparison(suggestionId: string): Promise<{
    suggestion_id: string;
    current_suggestion: {
      text: string;
      confidence: number;
      source: string;
    };
    contrastive_analysis: ContrastiveExplanation;
    counterfactual_analysis: CounterfactualExplanation;
    why_this_suggestion: string;
  }> {
    const response = await apiClient.get(`/xai/comparison/${suggestionId}`);
    return response.data;
  }
}

export const xaiService = new XAIService();

