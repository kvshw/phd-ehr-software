/**
 * Adaptive Dashboard Component
 * Dynamically reorders and shows/hides features based on MAPE-K analysis
 * All features are available, but displayed based on actual usage patterns
 */
'use client';

import React, { useEffect, useState, useMemo } from 'react';
import { useAuthStore } from '@/store/authStore';
import { adaptiveDashboardService, DashboardPlan } from '@/lib/adaptiveDashboardService';
import { monitorService } from '@/lib/monitorService';

export interface DashboardSection {
  id: string;
  label: string;
  component: React.ReactNode;
  defaultVisible: boolean;
  defaultPriority: number; // For fallback when no plan available
}

interface AdaptiveDashboardProps {
  sections: DashboardSection[];
  onFeatureClick?: (featureId: string) => void;
}

export function AdaptiveDashboard({ sections, onFeatureClick }: AdaptiveDashboardProps) {
  const { user } = useAuthStore();
  const [plan, setPlan] = useState<DashboardPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Fetch adaptation plan on mount and periodically
  useEffect(() => {
    const fetchPlan = async () => {
      try {
        const dashboardPlan = await adaptiveDashboardService.getPlan();
        setPlan(dashboardPlan);
        setLastUpdate(new Date());
      } catch (error) {
        console.error('Failed to fetch adaptive plan:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPlan();
    
    // Refresh plan every 5 minutes to adapt to new usage
    const interval = setInterval(fetchPlan, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  // Track when user interacts with features
  const handleFeatureInteraction = (featureId: string, actionType: 'quick_action_click' | 'feature_access' = 'feature_access') => {
    monitorService.logDashboardAction({
      actionType,
      featureId,
      metadata: {
        specialty: user?.specialty,
        time_of_day: new Date().getHours(),
      },
    });
    
    // Trigger plan refresh after significant interaction
    if (onFeatureClick) {
      onFeatureClick(featureId);
    }
  };

  // Apply adaptive plan to sections
  const adaptedSections = useMemo(() => {
    // Always return same structure: { visible: [], hidden: [] }
    if (!plan || plan.feature_priority.length === 0) {
      // No plan yet - use default order with specialty-based priority
      const visible = sections.filter(s => s.defaultVisible).sort((a, b) => b.defaultPriority - a.defaultPriority);
      const hidden = sections.filter(s => !s.defaultVisible);
      return { visible, hidden };
    }

    // Create a map of feature priorities from plan
    const priorityMap = new Map<string, { position: number; size: string; usage_count: number }>();
    plan.feature_priority.forEach(f => {
      priorityMap.set(f.id, {
        position: f.position,
        size: f.size,
        usage_count: f.usage_count,
      });
    });

    // Get hidden features
    const hiddenSet = new Set(plan.hidden_features);

    // Sort sections by plan priority
    const visibleSections = sections
      .filter(section => {
        // Show if not in hidden list and either in plan or defaultVisible
        if (hiddenSet.has(section.id)) {
          return false;
        }
        return priorityMap.has(section.id) || section.defaultVisible;
      })
      .sort((a, b) => {
        const aPriority = priorityMap.get(a.id);
        const bPriority = priorityMap.get(b.id);
        
        if (aPriority && bPriority) {
          return aPriority.position - bPriority.position;
        }
        if (aPriority) return -1; // Planned features first
        if (bPriority) return 1;
        return b.defaultPriority - a.defaultPriority; // Then by default priority
      });

    // Add hidden sections to a "More" section
    const hiddenSections = sections.filter(s => hiddenSet.has(s.id));

    return { visible: visibleSections, hidden: hiddenSections };
  }, [plan, sections]);

  if (loading) {
    return (
      <div className="space-y-6">
        {sections.filter(s => s.defaultVisible).map(section => (
          <div key={section.id}>{section.component}</div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Show adaptation indicator if plan exists */}
      {plan && plan.explanation && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span className="font-medium">Adaptive Layout Active</span>
            <span className="text-blue-600">•</span>
            <span className="text-xs">{plan.explanation}</span>
          </div>
        </div>
      )}

      {/* Render visible sections in adaptive order */}
      {adaptedSections?.visible?.map((section) => {
        const featureInfo = plan?.feature_priority.find(f => f.id === section.id);
        const size = featureInfo?.size || 'medium';
        
        return (
          <div
            key={section.id}
            data-feature-id={section.id}
            data-usage-count={featureInfo?.usage_count || 0}
            className={`
              ${size === 'large' ? 'col-span-2' : ''}
              transition-all duration-300
            `}
          >
            {/* Wrap component to track interactions */}
            <div
              onClick={() => handleFeatureInteraction(section.id, 'feature_access')}
              className="cursor-pointer"
            >
              {section.component}
            </div>
          </div>
        );
      })}

      {/* Hidden sections in collapsible "More" section */}
      {adaptedSections?.hidden && adaptedSections.hidden.length > 0 && (
        <details className="bg-gray-50 rounded-lg border border-gray-200">
          <summary className="cursor-pointer p-4 text-sm font-medium text-gray-700 hover:text-gray-900 flex items-center justify-between">
            <span>More Features ({adaptedSections.hidden.length})</span>
            <span className="text-xs text-gray-500">Rarely used - click to expand</span>
          </summary>
          <div className="p-4 pt-0 space-y-4">
            {adaptedSections.hidden.map((section) => (
              <div
                key={section.id}
                onClick={() => handleFeatureInteraction(section.id, 'feature_access')}
                className="opacity-75 hover:opacity-100 transition-opacity"
              >
                {section.component}
              </div>
            ))}
          </div>
        </details>
      )}

      {/* Debug info (remove in production) */}
      {process.env.NODE_ENV === 'development' && plan && (
        <div className="fixed bottom-4 left-4 bg-black text-green-400 text-xs p-2 rounded font-mono z-50 max-w-xs">
          <div>Adaptive Plan Active</div>
          <div>Features: {plan.feature_priority.length}</div>
          <div>Hidden: {plan.hidden_features.length}</div>
          <div>Updated: {lastUpdate.toLocaleTimeString()}</div>
        </div>
      )}
    </div>
  );
}

/**
 * Hook to get adaptive dashboard state
 */
export function useAdaptiveDashboard() {
  const [plan, setPlan] = useState<DashboardPlan | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adaptiveDashboardService.getPlan().then(setPlan).finally(() => setLoading(false));
  }, []);

  return { plan, loading };
}

