"use client";

import { useState, useEffect } from "react";

interface ShadowTest {
  id: string;
  name: string;
  policy_type: string;
  is_shadow_mode: boolean;
  test_group_percentage: number;
  started_at: string;
  scheduled_end_at: string;
  status: string;
}

interface RolloutInfo {
  id: string;
  name: string;
  policy_type: string;
  status: string;
  stage_number?: number;
  rollout_percentage?: number;
  regression_detected?: boolean;
}

interface BiasAlert {
  group_type: string;
  group_value: string;
  deviation_from_overall: number;
  created_at: string;
}

interface DriftAlert {
  metric_name: string;
  drift_score: number;
  drift_direction: string;
  created_at: string;
}

interface Summary {
  active_tests: number;
  successful_deployments: number;
  rollbacks: number;
  total_tests: number;
  success_rate: number;
}

interface DashboardData {
  active_tests: ShadowTest[];
  recent_rollouts: RolloutInfo[];
  bias_alerts: BiasAlert[];
  drift_alerts: DriftAlert[];
  summary: Summary;
}

/**
 * AssuranceDashboard Component
 * 
 * Admin dashboard for monitoring MAPE-K runtime assurance
 */
export function AssuranceDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"tests" | "bias" | "drift">("tests");

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/assurance/dashboard`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const dashboardData = await response.json();
        setData(dashboardData);
      } else {
        // Use demo data if API not available
        setData(getDemoData());
      }
    } catch (error) {
      console.error("Error fetching assurance data:", error);
      // Use demo data on error
      setData(getDemoData());
    } finally {
      setLoading(false);
    }
  };

  const getDemoData = (): DashboardData => ({
    active_tests: [
      {
        id: "st-001",
        name: "Enhanced Risk Prediction v2",
        policy_type: "risk_display",
        is_shadow_mode: true,
        test_group_percentage: 25,
        started_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        scheduled_end_at: new Date(Date.now() + 9 * 24 * 60 * 60 * 1000).toISOString(),
        status: "running"
      },
      {
        id: "st-002",
        name: "Adaptive Layout Algorithm",
        policy_type: "ui_layout",
        is_shadow_mode: false,
        test_group_percentage: 10,
        started_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        scheduled_end_at: new Date(Date.now() + 12 * 24 * 60 * 60 * 1000).toISOString(),
        status: "running"
      }
    ],
    recent_rollouts: [
      {
        id: "ro-001",
        name: "Smart Suggestion Ranking",
        policy_type: "suggestion_priority",
        status: "completed",
        stage_number: 4,
        rollout_percentage: 100,
        regression_detected: false
      },
      {
        id: "ro-002",
        name: "Contextual Dashboard",
        policy_type: "ui_layout",
        status: "in_progress",
        stage_number: 2,
        rollout_percentage: 50,
        regression_detected: false
      }
    ],
    bias_alerts: [
      {
        group_type: "specialty",
        group_value: "Neurology",
        deviation_from_overall: 0.18,
        created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        group_type: "experience_level",
        group_value: "Junior (<2 years)",
        deviation_from_overall: -0.12,
        created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
      }
    ],
    drift_alerts: [
      {
        metric_name: "suggestion_acceptance_rate",
        drift_score: 0.15,
        drift_direction: "decreasing",
        created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        metric_name: "avg_time_to_decision",
        drift_score: 0.22,
        drift_direction: "increasing",
        created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString()
      }
    ],
    summary: {
      active_tests: 2,
      successful_deployments: 8,
      rollbacks: 1,
      total_tests: 12,
      success_rate: 0.92
    }
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            Runtime Assurance
          </h2>
          <p className="text-gray-500">
            Monitor ethics, safety, and transparency of MAPE-K adaptations
          </p>
        </div>
        <button
          onClick={fetchDashboardData}
          className="px-3 py-2 text-sm bg-white border rounded-lg hover:bg-gray-50"
        >
          Refresh
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <SummaryCard
          title="Active Tests"
          value={data?.summary.active_tests || 0}
          icon="🧪"
          color="blue"
        />
        <SummaryCard
          title="Successful Deploys"
          value={data?.summary.successful_deployments || 0}
          icon="✅"
          color="green"
        />
        <SummaryCard
          title="Rollbacks"
          value={data?.summary.rollbacks || 0}
          icon="↩️"
          color="red"
        />
        <SummaryCard
          title="Success Rate"
          value={`${Math.round((data?.summary.success_rate || 0) * 100)}%`}
          icon="📈"
          color="purple"
        />
      </div>

      {/* Alerts Banner */}
      {((data?.bias_alerts?.length || 0) > 0 || (data?.drift_alerts?.length || 0) > 0) && (
        <div className="rounded-lg bg-yellow-50 border border-yellow-200 p-4">
          <div className="flex items-center gap-2 text-yellow-800">
            <span>⚠️</span>
            <span className="font-medium">
              {(data?.bias_alerts?.length || 0) + (data?.drift_alerts?.length || 0)} alert(s) require attention
            </span>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b">
        <div className="flex gap-4">
          <TabButton
            active={activeTab === "tests"}
            onClick={() => setActiveTab("tests")}
            badge={data?.active_tests?.length}
          >
            🧪 Tests & Rollouts
          </TabButton>
          <TabButton
            active={activeTab === "bias"}
            onClick={() => setActiveTab("bias")}
            badge={data?.bias_alerts?.length}
            badgeColor="red"
          >
            👥 Bias Detection
          </TabButton>
          <TabButton
            active={activeTab === "drift"}
            onClick={() => setActiveTab("drift")}
            badge={data?.drift_alerts?.length}
            badgeColor="red"
          >
            📊 Drift Monitoring
          </TabButton>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === "tests" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Active Tests */}
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4">🧪 Active Shadow/A/B Tests</h3>
            {data?.active_tests?.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No active tests</p>
            ) : (
              <div className="space-y-3">
                {data?.active_tests?.map((test) => (
                  <TestCard key={test.id} test={test} />
                ))}
              </div>
            )}
          </div>

          {/* Recent Rollouts */}
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4">🚀 Recent Rollouts</h3>
            {data?.recent_rollouts?.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No recent rollouts</p>
            ) : (
              <div className="space-y-3">
                {data?.recent_rollouts?.map((rollout) => (
                  <RolloutCard key={rollout.id} rollout={rollout} />
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === "bias" && (
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold mb-4">👥 Bias Detection</h3>
          {data?.bias_alerts?.length === 0 ? (
            <div className="text-center py-12">
              <span className="text-4xl">✅</span>
              <p className="text-lg font-medium mt-3">No Bias Detected</p>
              <p className="text-gray-500">Adaptations benefit all user groups equally</p>
            </div>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 text-gray-700 font-semibold">Group Type</th>
                  <th className="text-left py-2 text-gray-700 font-semibold">Group</th>
                  <th className="text-left py-2 text-gray-700 font-semibold">Deviation</th>
                  <th className="text-left py-2 text-gray-700 font-semibold">Direction</th>
                </tr>
              </thead>
              <tbody>
                {data?.bias_alerts?.map((alert, idx) => (
                  <tr key={idx} className="border-b">
                    <td className="py-2 font-medium text-gray-900">{alert.group_type}</td>
                    <td className="py-2 text-gray-700">{alert.group_value}</td>
                    <td className="py-2">
                      <span className={`px-2 py-1 rounded text-sm font-semibold ${
                        Math.abs(alert.deviation_from_overall) > 0.2
                          ? "bg-red-100 text-red-800"
                          : "bg-gray-100 text-gray-800"
                      }`}>
                        {(alert.deviation_from_overall * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="py-2">
                      {alert.deviation_from_overall > 0 ? (
                        <span className="text-green-700 font-medium">↑ Advantaged</span>
                      ) : (
                        <span className="text-red-700 font-medium">↓ Disadvantaged</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {activeTab === "drift" && (
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold mb-4">📊 Drift Monitoring</h3>
          {data?.drift_alerts?.length === 0 ? (
            <div className="text-center py-12">
              <span className="text-4xl">✅</span>
              <p className="text-lg font-medium mt-3">No Drift Detected</p>
              <p className="text-gray-500">All metrics within expected ranges</p>
            </div>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 text-gray-700 font-semibold">Metric</th>
                  <th className="text-left py-2 text-gray-700 font-semibold">Drift Score</th>
                  <th className="text-left py-2 text-gray-700 font-semibold">Direction</th>
                  <th className="text-left py-2 text-gray-700 font-semibold">Severity</th>
                </tr>
              </thead>
              <tbody>
                {data?.drift_alerts?.map((alert, idx) => (
                  <tr key={idx} className="border-b">
                    <td className="py-2 font-medium text-gray-900">{alert.metric_name.replace(/_/g, " ")}</td>
                    <td className="py-2">
                      <span className="px-2 py-1 rounded border border-gray-300 text-sm font-semibold text-gray-800 bg-gray-50">
                        {alert.drift_score.toFixed(2)}σ
                      </span>
                    </td>
                    <td className="py-2">
                      {alert.drift_direction === "improving" ? (
                        <span className="text-green-700 font-medium">↑ Improving</span>
                      ) : alert.drift_direction === "degrading" ? (
                        <span className="text-red-700 font-medium">↓ Degrading</span>
                      ) : (
                        <span className="text-gray-700 font-medium">→ Shift</span>
                      )}
                    </td>
                    <td className="py-2">
                      <DriftSeverity score={alert.drift_score} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}

// Sub-components

function SummaryCard({
  title,
  value,
  icon,
  color,
}: {
  title: string;
  value: number | string;
  icon: string;
  color: "blue" | "green" | "red" | "purple";
}) {
  const colorClasses = {
    blue: "bg-blue-100 text-blue-600",
    green: "bg-green-100 text-green-600",
    red: "bg-red-100 text-red-600",
    purple: "bg-purple-100 text-purple-600",
  };

  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
        <div className={`rounded-full p-3 text-2xl ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

function TabButton({
  children,
  active,
  onClick,
  badge,
  badgeColor = "blue",
}: {
  children: React.ReactNode;
  active: boolean;
  onClick: () => void;
  badge?: number;
  badgeColor?: "blue" | "red";
}) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
        active
          ? "border-blue-600 text-blue-600"
          : "border-transparent text-gray-500 hover:text-gray-700"
      }`}
    >
      {children}
      {badge !== undefined && badge > 0 && (
        <span className={`px-2 py-0.5 rounded-full text-xs text-white ${
          badgeColor === "red" ? "bg-red-500" : "bg-blue-500"
        }`}>
          {badge}
        </span>
      )}
    </button>
  );
}

function TestCard({ test }: { test: ShadowTest }) {
  const daysRemaining = Math.max(
    0,
    Math.ceil(
      (new Date(test.scheduled_end_at).getTime() - Date.now()) /
        (1000 * 60 * 60 * 24)
    )
  );

  return (
    <div className="rounded-lg border p-3">
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-medium truncate">{test.name}</h4>
        <span className={`px-2 py-1 rounded text-xs ${
          test.is_shadow_mode
            ? "bg-gray-100 text-gray-700"
            : "bg-blue-100 text-blue-700"
        }`}>
          {test.is_shadow_mode ? "Shadow" : "A/B"}
        </span>
      </div>
      <div className="space-y-1 text-sm text-gray-500">
        <div className="flex justify-between">
          <span>Type:</span>
          <span>{test.policy_type}</span>
        </div>
        <div className="flex justify-between">
          <span>Remaining:</span>
          <span>{daysRemaining} days</span>
        </div>
      </div>
    </div>
  );
}

function RolloutCard({ rollout }: { rollout: RolloutInfo }) {
  const statusColors: Record<string, string> = {
    rolling_out: "bg-blue-500",
    deployed: "bg-green-500",
    rolled_back: "bg-red-500",
  };

  return (
    <div className="rounded-lg border p-3">
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-medium truncate">{rollout.name}</h4>
        <span className={`px-2 py-1 rounded text-xs text-white ${
          statusColors[rollout.status] || "bg-gray-500"
        }`}>
          {rollout.status.replace("_", " ")}
        </span>
      </div>
      {rollout.rollout_percentage !== undefined && (
        <div className="space-y-1">
          <div className="flex justify-between text-sm text-gray-500">
            <span>Progress</span>
            <span>{(rollout.rollout_percentage * 100).toFixed(0)}%</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 rounded-full"
              style={{ width: `${rollout.rollout_percentage * 100}%` }}
            />
          </div>
        </div>
      )}
      {rollout.regression_detected && (
        <div className="mt-2 flex items-center gap-1 text-red-600 text-sm">
          ⚠️ Regression detected
        </div>
      )}
    </div>
  );
}

function DriftSeverity({ score }: { score: number }) {
  if (score > 3) {
    return (
      <span className="px-2 py-1 rounded text-xs font-semibold bg-red-100 text-red-800 border border-red-200">
        ⚠️ Critical
      </span>
    );
  }
  if (score > 2) {
    return (
      <span className="px-2 py-1 rounded text-xs font-semibold bg-orange-100 text-orange-800 border border-orange-200">
        High
      </span>
    );
  }
  return (
    <span className="px-2 py-1 rounded text-xs font-semibold bg-gray-100 text-gray-800 border border-gray-200">
      Moderate
    </span>
  );
}

export default AssuranceDashboard;
