"use client";

import { useState, useEffect } from "react";
import { apiClient } from "@/lib/apiClient";

interface RegretData {
  summary: {
    total_rounds: number;
    cumulative_regret: number;
    average_regret_per_round: number;
    optimal_arm_selection_rate: string;
  };
  theoretical_analysis: {
    theoretical_bound: number;
    empirical_vs_theoretical_ratio: number;
    bound_interpretation: string;
  };
  convergence_analysis: {
    converged: boolean;
    convergence_round: number | null;
    interpretation: string;
  };
  arm_performance: {
    selection_frequency: Record<string, number>;
    regret_per_arm: Record<string, number>;
  };
  regret_curve: {
    data_points: number;
    curve: [number, number][];
  };
}

export default function RegretAnalysisChart() {
  const [data, setData] = useState<RegretData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(30);

  useEffect(() => {
    fetchRegretData();
  }, [days]);

  const fetchRegretData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get(`/research-analytics/regret/report?days=${days}`);
      setData(response.data);
    } catch (err: any) {
      console.error("Error fetching regret data:", err);
      setError(err.response?.data?.detail || "Failed to fetch regret data");
    } finally {
      setLoading(false);
    }
  };

  // Calculate chart dimensions
  const chartWidth = 600;
  const chartHeight = 300;
  const padding = { top: 20, right: 20, bottom: 40, left: 60 };
  const innerWidth = chartWidth - padding.left - padding.right;
  const innerHeight = chartHeight - padding.top - padding.bottom;

  // Generate SVG path for regret curve
  const generatePath = (curve: [number, number][]) => {
    if (!curve || curve.length === 0) return "";
    
    const maxRound = Math.max(...curve.map(d => d[0]));
    const maxRegret = Math.max(...curve.map(d => d[1]), 1);
    
    const xScale = (val: number) => padding.left + (val / maxRound) * innerWidth;
    const yScale = (val: number) => padding.top + innerHeight - (val / maxRegret) * innerHeight;
    
    return curve.map((point, i) => {
      const x = xScale(point[0]);
      const y = yScale(point[1]);
      return i === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;
    }).join(" ");
  };

  // Generate theoretical bound line (sqrt(K*T*log(T)))
  const generateTheoreticalPath = (curve: [number, number][], numArms: number = 10) => {
    if (!curve || curve.length === 0) return "";
    
    const maxRound = Math.max(...curve.map(d => d[0]));
    const theoreticalPoints: [number, number][] = [];
    
    for (let t = 1; t <= maxRound; t += Math.max(1, maxRound / 50)) {
      const bound = 1.5 * Math.sqrt(numArms * t * Math.log(Math.max(t, 2)));
      theoreticalPoints.push([t, bound]);
    }
    
    const maxRegret = Math.max(...curve.map(d => d[1]), ...theoreticalPoints.map(d => d[1]), 1);
    
    const xScale = (val: number) => padding.left + (val / maxRound) * innerWidth;
    const yScale = (val: number) => padding.top + innerHeight - (val / maxRegret) * innerHeight;
    
    return theoreticalPoints.map((point, i) => {
      const x = xScale(point[0]);
      const y = yScale(point[1]);
      return i === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;
    }).join(" ");
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="animate-pulse flex flex-col gap-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Cumulative Regret Analysis</h3>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800 font-medium">No regret data available yet</p>
          <p className="text-yellow-600 text-sm mt-2">
            Regret data is collected as users interact with the dashboard. Keep using the system 
            and data will accumulate automatically.
          </p>
          <div className="mt-4 p-3 bg-yellow-100 rounded text-sm text-yellow-700">
            <p className="font-medium">How to generate data:</p>
            <ol className="list-decimal ml-4 mt-2 space-y-1">
              <li>Use the doctor dashboard to view patients</li>
              <li>Click on different sections (vitals, medications, labs)</li>
              <li>Accept or ignore AI suggestions</li>
              <li>Each interaction updates the bandit and logs regret</li>
            </ol>
          </div>
        </div>
      </div>
    );
  }

  if (!data || !data.regret_curve?.curve?.length) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Cumulative Regret Analysis</h3>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
          <p className="text-blue-800">No regret observations recorded yet</p>
          <p className="text-blue-600 text-sm mt-2">
            Use the system and regret will be tracked automatically.
          </p>
        </div>
      </div>
    );
  }

  const curve = data.regret_curve.curve;
  const maxRound = curve.length > 0 ? Math.max(...curve.map(d => d[0])) : 0;
  const maxRegret = curve.length > 0 ? Math.max(...curve.map(d => d[1]), 1) : 1;

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">📊 Cumulative Regret Over Time</h3>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm text-gray-900 bg-white"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
          <option value={365}>Last year</option>
        </select>
      </div>

      {/* Chart */}
      <div className="overflow-x-auto">
        <svg width={chartWidth} height={chartHeight} className="mx-auto">
          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((tick) => (
            <g key={tick}>
              <line
                x1={padding.left}
                x2={chartWidth - padding.right}
                y1={padding.top + innerHeight * (1 - tick)}
                y2={padding.top + innerHeight * (1 - tick)}
                stroke="#e5e7eb"
                strokeDasharray="4,4"
              />
              <text
                x={padding.left - 10}
                y={padding.top + innerHeight * (1 - tick) + 4}
                textAnchor="end"
                className="text-xs fill-gray-500"
              >
                {(maxRegret * tick).toFixed(1)}
              </text>
            </g>
          ))}

          {/* Theoretical bound line */}
          <path
            d={generateTheoreticalPath(curve)}
            fill="none"
            stroke="#9ca3af"
            strokeWidth={2}
            strokeDasharray="6,4"
            opacity={0.7}
          />

          {/* Empirical regret curve */}
          <path
            d={generatePath(curve)}
            fill="none"
            stroke="#3b82f6"
            strokeWidth={2.5}
          />

          {/* Data points */}
          {curve.map((point, i) => {
            const x = padding.left + (point[0] / maxRound) * innerWidth;
            const y = padding.top + innerHeight - (point[1] / maxRegret) * innerHeight;
            return (
              <circle
                key={i}
                cx={x}
                cy={y}
                r={3}
                fill="#3b82f6"
                className="hover:r-5 transition-all"
              />
            );
          })}

          {/* Convergence marker */}
          {data.convergence_analysis.converged && data.convergence_analysis.convergence_round && (
            <g>
              <line
                x1={padding.left + (data.convergence_analysis.convergence_round / maxRound) * innerWidth}
                x2={padding.left + (data.convergence_analysis.convergence_round / maxRound) * innerWidth}
                y1={padding.top}
                y2={padding.top + innerHeight}
                stroke="#10b981"
                strokeWidth={2}
                strokeDasharray="4,4"
              />
              <text
                x={padding.left + (data.convergence_analysis.convergence_round / maxRound) * innerWidth}
                y={padding.top - 5}
                textAnchor="middle"
                className="text-xs fill-green-600 font-medium"
              >
                Converged
              </text>
            </g>
          )}

          {/* X-axis label */}
          <text
            x={chartWidth / 2}
            y={chartHeight - 5}
            textAnchor="middle"
            className="text-sm fill-gray-600"
          >
            Rounds (Interactions)
          </text>

          {/* Y-axis label */}
          <text
            x={15}
            y={chartHeight / 2}
            textAnchor="middle"
            transform={`rotate(-90, 15, ${chartHeight / 2})`}
            className="text-sm fill-gray-600"
          >
            Cumulative Regret
          </text>
        </svg>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-blue-500"></div>
          <span className="text-gray-600">Empirical Regret</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-gray-400 border-dashed border-t-2 border-gray-400"></div>
          <span className="text-gray-600">Theoretical Bound O(√KT log T)</span>
        </div>
        {data.convergence_analysis.converged && (
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-green-500 border-dashed border-t-2 border-green-500"></div>
            <span className="text-gray-600">Convergence Point</span>
          </div>
        )}
      </div>

      {/* Metrics Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">{data.summary.total_rounds}</div>
          <div className="text-sm text-gray-500">Total Rounds</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-orange-600">{data.summary.cumulative_regret.toFixed(2)}</div>
          <div className="text-sm text-gray-500">Cumulative Regret</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">{data.summary.optimal_arm_selection_rate}</div>
          <div className="text-sm text-gray-500">Optimal Selection</div>
        </div>
        <div className="text-center">
          <div className={`text-2xl font-bold ${data.theoretical_analysis.empirical_vs_theoretical_ratio <= 1 ? 'text-green-600' : 'text-orange-600'}`}>
            {(data.theoretical_analysis.empirical_vs_theoretical_ratio * 100).toFixed(0)}%
          </div>
          <div className="text-sm text-gray-500">vs Theoretical Bound</div>
        </div>
      </div>

      {/* Convergence Status */}
      <div className={`mt-4 p-3 rounded-lg ${data.convergence_analysis.converged ? 'bg-green-50 text-green-800' : 'bg-blue-50 text-blue-800'}`}>
        <div className="flex items-center gap-2">
          {data.convergence_analysis.converged ? (
            <>
              <span className="text-lg">✅</span>
              <span className="font-medium">Algorithm Converged</span>
              <span className="text-sm">at round {data.convergence_analysis.convergence_round}</span>
            </>
          ) : (
            <>
              <span className="text-lg">🔄</span>
              <span className="font-medium">Still Learning</span>
              <span className="text-sm">- {data.convergence_analysis.interpretation}</span>
            </>
          )}
        </div>
      </div>

      {/* Arm Performance */}
      {Object.keys(data.arm_performance.selection_frequency).length > 0 && (
        <div className="mt-6 pt-6 border-t">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Feature Selection Frequency</h4>
          <div className="flex flex-wrap gap-2">
            {Object.entries(data.arm_performance.selection_frequency)
              .sort((a, b) => b[1] - a[1])
              .map(([arm, count]) => (
                <div key={arm} className="px-3 py-1 bg-gray-100 rounded-full text-sm">
                  <span className="font-medium text-gray-700">{arm}</span>
                  <span className="text-gray-500 ml-1">({count})</span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}

