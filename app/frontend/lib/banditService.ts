/**
 * Bandit Learning Service
 * Handles Thompson Sampling feedback and status for MAPE-K adaptation
 */
import { apiClient } from './apiClient';

export interface FeatureBelief {
  feature_key: string;
  context_hash: string;
  alpha: number;
  beta: number;
  expected_value: number;
  confidence_interval: [number, number];
  total_interactions: number;
  is_critical: boolean;
}

export interface RecentAdaptation {
  feature_key: string;
  action: 'promoted' | 'demoted' | 'maintained';
  sampled_value: number;
  constraint_applied: string | null;
  created_at: string;
}

export interface BanditStatus {
  user_id: string;
  using_bandit: boolean;
  feature_beliefs: FeatureBelief[];
  recent_adaptations: RecentAdaptation[];
}

export interface BanditPlanResult {
  plan: {
    order: string[];
    suggestion_density: string;
    flags: Record<string, any>;
  };
  adaptation_id: string;
  explanation: string;
  algorithm: string;
  bandit_details?: {
    sampled_values: Record<string, number>;
    actions: Record<string, string>;
    constraints_applied: string[];
  };
  ab_test?: {
    group: 'bandit' | 'rule_based';
    user_id: string;
  };
}

export const banditService = {
  /**
   * Record user feedback for bandit learning
   * Call this when user interacts with a feature
   */
  recordFeedback: async (
    featureKey: string,
    success: boolean,
    specialty?: string,
    weight: number = 1.0
  ): Promise<void> => {
    await apiClient.post('/mape-k/bandit/feedback', null, {
      params: {
        feature_key: featureKey,
        success,
        specialty,
        weight,
      },
    });
  },

  /**
   * Record quick access to a feature (positive feedback)
   */
  recordQuickAccess: async (featureKey: string, specialty?: string): Promise<void> => {
    await banditService.recordFeedback(featureKey, true, specialty, 1.0);
  },

  /**
   * Record prolonged use of a feature (positive feedback)
   */
  recordProlongedUse: async (featureKey: string, specialty?: string): Promise<void> => {
    await banditService.recordFeedback(featureKey, true, specialty, 1.5);
  },

  /**
   * Record ignored feature (negative feedback)
   */
  recordIgnored: async (featureKey: string, specialty?: string): Promise<void> => {
    await banditService.recordFeedback(featureKey, false, specialty, 0.5);
  },

  /**
   * Record AI suggestion acceptance (positive feedback for suggestions)
   */
  recordSuggestionAccepted: async (specialty?: string): Promise<void> => {
    await banditService.recordFeedback('suggestions', true, specialty, 1.5);
  },

  /**
   * Record AI suggestion ignored (negative feedback for suggestions)
   */
  recordSuggestionIgnored: async (specialty?: string): Promise<void> => {
    await banditService.recordFeedback('suggestions', false, specialty, 0.5);
  },

  /**
   * Get smart plan using best available algorithm (A/B tested)
   */
  getSmartPlan: async (
    patientId?: string,
    specialty?: string
  ): Promise<BanditPlanResult> => {
    const params: Record<string, string> = {};
    if (patientId) params.patient_id = patientId;
    if (specialty) params.specialty = specialty;

    const response = await apiClient.post<BanditPlanResult>(
      '/mape-k/plan/smart',
      null,
      { params }
    );
    return response.data;
  },

  /**
   * Get bandit-based plan explicitly
   */
  getBanditPlan: async (
    patientId?: string,
    specialty?: string
  ): Promise<BanditPlanResult> => {
    const params: Record<string, string> = {};
    if (patientId) params.patient_id = patientId;
    if (specialty) params.specialty = specialty;

    const response = await apiClient.post<BanditPlanResult>(
      '/mape-k/plan/bandit',
      null,
      { params }
    );
    return response.data;
  },

  /**
   * Get current bandit status for user
   */
  getStatus: async (): Promise<BanditStatus> => {
    const response = await apiClient.get<BanditStatus>('/mape-k/bandit/status');
    return response.data;
  },
};

/**
 * Hook for tracking feature interactions
 * Use this to automatically record bandit feedback
 */
export class FeatureInteractionTracker {
  private viewStartTime: Map<string, number> = new Map();
  private specialty?: string;

  constructor(specialty?: string) {
    this.specialty = specialty;
  }

  /**
   * Call when user starts viewing a feature/section
   */
  startViewing(featureKey: string): void {
    this.viewStartTime.set(featureKey, Date.now());
  }

  /**
   * Call when user stops viewing a feature/section
   * Automatically determines if it was quick access or prolonged use
   */
  async stopViewing(featureKey: string): Promise<void> {
    const startTime = this.viewStartTime.get(featureKey);
    if (!startTime) return;

    const duration = Date.now() - startTime;
    this.viewStartTime.delete(featureKey);

    // Quick access: < 5 seconds
    // Prolonged use: > 30 seconds
    // Ignore: 5-30 seconds (neutral, don't record)
    try {
      if (duration < 5000) {
        await banditService.recordQuickAccess(featureKey, this.specialty);
      } else if (duration > 30000) {
        await banditService.recordProlongedUse(featureKey, this.specialty);
      }
      // Between 5-30 seconds: no feedback (neutral)
    } catch (error) {
      console.warn('Failed to record bandit feedback:', error);
    }
  }

  /**
   * Record that user scrolled past a feature without interacting
   */
  async recordScrolledPast(featureKey: string): Promise<void> {
    try {
      await banditService.recordIgnored(featureKey, this.specialty);
    } catch (error) {
      console.warn('Failed to record scrolled past feedback:', error);
    }
  }

  /**
   * Update specialty (e.g., when user profile changes)
   */
  setSpecialty(specialty: string): void {
    this.specialty = specialty;
  }
}

export default banditService;

