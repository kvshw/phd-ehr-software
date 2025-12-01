"use client";

import { useState, useEffect } from "react";

interface TimeToTargetMetrics {
  feature_key: string;
  measurements: number;
  mean_seconds: number | null;
  median_seconds: number | null;
  min_seconds: number | null;
  max_seconds: number | null;
}

interface ClickReductionMetrics {
  click_reduction_percent: number;
  improvement: boolean;
  baseline_period: {
    clicks_per_day: number;
    total_clicks: number;
  };
  adaptive_period: {
    clicks_per_day: number;
    total_clicks: number;
  };
}

interface SuggestionRates {
  total_suggestions: number;
  acceptance_rate: number;
  ignore_rate: number;
  rejection_rate: number;
}

interface AdaptationAccuracy {
  precision: number;
  recall: number;
  f1_score: number;
  top_n: number;
}

interface StudySummary {
  study_id: string;
  name: string;
  status: string;
  unique_users: number;
  sequential_analysis: {
    can_stop: boolean;
    recommendation: string;
    effect_size: number;
  };
}

/**
 * MetricsDashboard Component
 * 
 * Research dashboard for viewing comprehensive metrics
 * on adaptation effectiveness and user behavior.
 */
export function MetricsDashboard() {
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"efficiency" | "effectiveness" | "studies">("efficiency");
  
  // Metrics state
  const [clickReduction, setClickReduction] = useState<ClickReductionMetrics | null>(null);
  const [suggestionRates, setSuggestionRates] = useState<SuggestionRates | null>(null);
  const [adaptationAccuracy, setAdaptationAccuracy] = useState<AdaptationAccuracy | null>(null);
  const [studies, setStudies] = useState<StudySummary[]>([]);
  const [timeToTarget, setTimeToTarget] = useState<Record<string, TimeToTargetMetrics>>({});
  
  useEffect(() => {
    fetchMetrics();
  }, []);
  
  const fetchMetrics = async () => {
    setLoading(true);
    const token = localStorage.getItem("token");
    const headers = { Authorization: `Bearer ${token}` };
    const baseUrl = process.env.NEXT_PUBLIC_API_URL;
    
    try {
      // Fetch all metrics in parallel
      const [
        clickRes,
        suggestRes,
        accuracyRes,
        studiesRes,
      ] = await Promise.all([
        fetch(`${baseUrl}/api/v1/research/metrics/click-reduction`, { headers }).catch(() => null),
        fetch(`${baseUrl}/api/v1/research/metrics/suggestion-rates`, { headers }).catch(() => null),
        fetch(`${baseUrl}/api/v1/research/metrics/adaptation-accuracy`, { headers }).catch(() => null),
        fetch(`${baseUrl}/api/v1/research/studies`, { headers }).catch(() => null),
      ]);
      
      if (clickRes?.ok) setClickReduction(await clickRes.json());
      if (suggestRes?.ok) setSuggestionRates(await suggestRes.json());
      if (accuracyRes?.ok) setAdaptationAccuracy(await accuracyRes.json());
      if (studiesRes?.ok) {
        const data = await studiesRes.json();
        setStudies(data.studies || []);
      }
      
      // Fetch time-to-target for common features
      const features = ["vitals", "medications", "labs", "notes", "problems"];
      for (const feature of features) {
        try {
          const res = await fetch(
            `${baseUrl}/api/v1/research/metrics/time-to-target/${feature}`,
            { headers }
          );
          if (res.ok) {
            const data = await res.json();
            setTimeToTarget(prev => ({ ...prev, [feature]: data }));
          }
        } catch (e) {
          // Ignore individual feature errors
        }
      }
    } catch (error) {
      console.error("Error fetching metrics:", error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }
  
  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">📊 Research Metrics Dashboard</h1>
          <p className="text-gray-500">
            Comprehensive metrics for adaptation effectiveness evaluation
          </p>
        </div>
        <button
          onClick={fetchMetrics}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>
      
      {/* Tabs */}
      <div className="border-b">
        <div className="flex gap-4">
          <TabButton
            active={activeTab === "efficiency"}
            onClick={() => setActiveTab("efficiency")}
          >
            ⚡ Efficiency
          </TabButton>
          <TabButton
            active={activeTab === "effectiveness"}
            onClick={() => setActiveTab("effectiveness")}
          >
            🎯 Effectiveness
          </TabButton>
          <TabButton
            active={activeTab === "studies"}
            onClick={() => setActiveTab("studies")}
          >
            🧪 Studies
          </TabButton>
        </div>
      </div>
      
      {/* Tab Content */}
      {activeTab === "efficiency" && (
        <div className="space-y-6">
          {/* Click Reduction */}
          <div className="bg-white rounded-lg border p-6">
            <h2 className="text-lg font-semibold mb-4">📉 Click Reduction</h2>
            {clickReduction ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <MetricCard
                  label="Reduction"
                  value={`${clickReduction.click_reduction_percent?.toFixed(1) || 0}%`}
                  status={clickReduction.improvement ? "positive" : "negative"}
                  description={clickReduction.improvement ? "Fewer clicks needed" : "More clicks needed"}
                />
                <MetricCard
                  label="Baseline Period"
                  value={`${clickReduction.baseline_period?.clicks_per_day?.toFixed(1) || 0}`}
                  description="Clicks per day (before)"
                />
                <MetricCard
                  label="Adaptive Period"
                  value={`${clickReduction.adaptive_period?.clicks_per_day?.toFixed(1) || 0}`}
                  description="Clicks per day (after)"
                />
              </div>
            ) : (
              <p className="text-gray-500">No click reduction data available</p>
            )}
          </div>
          
          {/* Time to Target */}
          <div className="bg-white rounded-lg border p-6">
            <h2 className="text-lg font-semibold mb-4">⏱️ Time to Target (seconds)</h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {Object.entries(timeToTarget).map(([feature, data]) => (
                <div key={feature} className="bg-gray-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {data.mean_seconds?.toFixed(1) || "—"}
                  </div>
                  <div className="text-sm text-gray-500 capitalize">{feature}</div>
                  <div className="text-xs text-gray-400">
                    {data.measurements} samples
                  </div>
                </div>
              ))}
              {Object.keys(timeToTarget).length === 0 && (
                <p className="text-gray-500 col-span-5">No time-to-target data available</p>
              )}
            </div>
          </div>
        </div>
      )}
      
      {activeTab === "effectiveness" && (
        <div className="space-y-6">
          {/* Suggestion Rates */}
          <div className="bg-white rounded-lg border p-6">
            <h2 className="text-lg font-semibold mb-4">💡 Suggestion Response Rates</h2>
            {suggestionRates ? (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <MetricCard
                    label="Total Suggestions"
                    value={suggestionRates.total_suggestions.toString()}
                  />
                  <MetricCard
                    label="Acceptance Rate"
                    value={`${(suggestionRates.acceptance_rate * 100).toFixed(1)}%`}
                    status={suggestionRates.acceptance_rate > 0.5 ? "positive" : "neutral"}
                  />
                  <MetricCard
                    label="Ignore Rate"
                    value={`${(suggestionRates.ignore_rate * 100).toFixed(1)}%`}
                    status="neutral"
                  />
                  <MetricCard
                    label="Rejection Rate"
                    value={`${(suggestionRates.rejection_rate * 100).toFixed(1)}%`}
                    status={suggestionRates.rejection_rate > 0.3 ? "negative" : "neutral"}
                  />
                </div>
                
                {/* Bar visualization */}
                <div className="h-8 flex rounded-lg overflow-hidden">
                  <div
                    className="bg-green-500"
                    style={{ width: `${suggestionRates.acceptance_rate * 100}%` }}
                    title="Accepted"
                  />
                  <div
                    className="bg-yellow-500"
                    style={{ width: `${suggestionRates.ignore_rate * 100}%` }}
                    title="Ignored"
                  />
                  <div
                    className="bg-red-500"
                    style={{ width: `${suggestionRates.rejection_rate * 100}%` }}
                    title="Rejected"
                  />
                </div>
                <div className="flex justify-between text-sm text-gray-500">
                  <span>🟢 Accepted</span>
                  <span>🟡 Ignored</span>
                  <span>🔴 Rejected</span>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">No suggestion data available</p>
            )}
          </div>
          
          {/* Adaptation Accuracy */}
          <div className="bg-white rounded-lg border p-6">
            <h2 className="text-lg font-semibold mb-4">🎯 Adaptation Accuracy (Top-{adaptationAccuracy?.top_n || 5} Features)</h2>
            {adaptationAccuracy ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <MetricCard
                  label="Precision"
                  value={`${(adaptationAccuracy.precision * 100).toFixed(1)}%`}
                  description="Promoted features that were used"
                  status={adaptationAccuracy.precision > 0.6 ? "positive" : "neutral"}
                />
                <MetricCard
                  label="Recall"
                  value={`${(adaptationAccuracy.recall * 100).toFixed(1)}%`}
                  description="Used features that were promoted"
                  status={adaptationAccuracy.recall > 0.6 ? "positive" : "neutral"}
                />
                <MetricCard
                  label="F1 Score"
                  value={`${(adaptationAccuracy.f1_score * 100).toFixed(1)}%`}
                  description="Balanced accuracy measure"
                  status={adaptationAccuracy.f1_score > 0.6 ? "positive" : "neutral"}
                />
              </div>
            ) : (
              <p className="text-gray-500">No adaptation accuracy data available</p>
            )}
          </div>
        </div>
      )}
      
      {activeTab === "studies" && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg border p-6">
            <h2 className="text-lg font-semibold mb-4">🧪 Research Studies</h2>
            {studies.length > 0 ? (
              <div className="space-y-4">
                {studies.map((study) => (
                  <StudyCard key={study.study_id} study={study} />
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <span className="text-4xl">📋</span>
                <p className="text-lg font-medium mt-3">No Studies Yet</p>
                <p className="text-gray-500">Create a study to start A/B testing</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Sub-components

function TabButton({
  children,
  active,
  onClick,
}: {
  children: React.ReactNode;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 font-medium border-b-2 transition-colors ${
        active
          ? "border-blue-600 text-blue-600"
          : "border-transparent text-gray-500 hover:text-gray-700"
      }`}
    >
      {children}
    </button>
  );
}

function MetricCard({
  label,
  value,
  description,
  status = "neutral",
}: {
  label: string;
  value: string;
  description?: string;
  status?: "positive" | "negative" | "neutral";
}) {
  const statusColors = {
    positive: "text-green-600",
    negative: "text-red-600",
    neutral: "text-gray-900",
  };
  
  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="text-sm text-gray-500">{label}</div>
      <div className={`text-2xl font-bold ${statusColors[status]}`}>{value}</div>
      {description && (
        <div className="text-xs text-gray-400 mt-1">{description}</div>
      )}
    </div>
  );
}

function StudyCard({ study }: { study: StudySummary }) {
  const statusColors: Record<string, string> = {
    draft: "bg-gray-100 text-gray-700",
    active: "bg-green-100 text-green-700",
    paused: "bg-yellow-100 text-yellow-700",
    completed: "bg-blue-100 text-blue-700",
  };
  
  return (
    <div className="border rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold">{study.name}</h3>
        <span className={`px-2 py-1 rounded text-sm ${statusColors[study.status] || "bg-gray-100"}`}>
          {study.status}
        </span>
      </div>
      <div className="grid grid-cols-3 gap-4 text-sm">
        <div>
          <span className="text-gray-500">Participants:</span>
          <span className="ml-2 font-medium">{study.unique_users}</span>
        </div>
        {study.sequential_analysis && (
          <>
            <div>
              <span className="text-gray-500">Effect Size:</span>
              <span className="ml-2 font-medium">
                {study.sequential_analysis.effect_size?.toFixed(3) || "—"}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Can Stop:</span>
              <span className={`ml-2 font-medium ${
                study.sequential_analysis.can_stop ? "text-green-600" : "text-gray-600"
              }`}>
                {study.sequential_analysis.can_stop ? "Yes" : "No"}
              </span>
            </div>
          </>
        )}
      </div>
      {study.sequential_analysis?.recommendation && (
        <div className="mt-2 text-sm text-gray-600 bg-gray-50 rounded p-2">
          {study.sequential_analysis.recommendation}
        </div>
      )}
    </div>
  );
}

export default MetricsDashboard;

