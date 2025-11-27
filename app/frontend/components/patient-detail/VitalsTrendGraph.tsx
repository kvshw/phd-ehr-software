/**
 * Vitals Trend Graph Component
 * Displays interactive line charts for vital signs with abnormal value highlighting
 */
'use client';

import { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { vitalService, Vital } from '@/lib/vitalService';

interface VitalsTrendGraphProps {
  patientId: string;
}

// Normal ranges for vital signs
const NORMAL_RANGES = {
  hr: { min: 60, max: 100 },
  bp_sys: { min: 90, max: 140 },
  bp_dia: { min: 60, max: 90 },
  spo2: { min: 95, max: 100 },
  rr: { min: 12, max: 20 },
  temp: { min: 36.1, max: 37.2 },
  pain: { min: 0, max: 3 },
};

// Chart colors
const CHART_COLORS = {
  hr: '#ef4444', // red
  bp_sys: '#3b82f6', // blue
  bp_dia: '#60a5fa', // light blue
  spo2: '#10b981', // green
  rr: '#f59e0b', // amber
  temp: '#ec4899', // pink
  pain: '#8b5cf6', // purple
};

export function VitalsTrendGraph({ patientId }: VitalsTrendGraphProps) {
  const [vitals, setVitals] = useState<Vital[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedVital, setSelectedVital] = useState<string>('all');
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d' | 'all'>('7d');

  useEffect(() => {
    fetchVitals();
  }, [patientId, timeRange]);

  const fetchVitals = async () => {
    setLoading(true);
    setError(null);
    try {
      // Calculate time range for backend filtering
      let startTime: Date | undefined;
      if (timeRange !== 'all') {
        const now = new Date();
        const cutoffDate = new Date();
        
        switch (timeRange) {
          case '24h':
            cutoffDate.setHours(now.getHours() - 24);
            break;
          case '7d':
            cutoffDate.setDate(now.getDate() - 7);
            break;
          case '30d':
            cutoffDate.setDate(now.getDate() - 30);
            break;
        }
        startTime = cutoffDate;
      }
      
      // Fetch with time range filter from backend (more efficient)
      const response = await vitalService.getPatientVitals(patientId, {
        start_time: startTime?.toISOString(),
        limit: 500, // Reasonable limit for chart display
      });
      // Data is already filtered by backend - no redundant client-side filtering needed
      const filteredVitals = response.items;

      // Sort by timestamp
      filteredVitals.sort((a, b) => 
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      );
      
      setVitals(filteredVitals);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load vitals data');
      console.error('Error fetching vitals:', err);
    } finally {
      setLoading(false);
    }
  };

  // Format data for charts
  const formatChartData = () => {
    return vitals.map((v) => ({
      timestamp: new Date(v.timestamp).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      }),
      fullTimestamp: v.timestamp,
      hr: v.hr,
      bp_sys: v.bp_sys,
      bp_dia: v.bp_dia,
      spo2: v.spo2,
      rr: v.rr,
      temp: v.temp,
      pain: v.pain,
    }));
  };

  // Check if value is abnormal
  const isAbnormal = (vitalType: string, value: number | null): boolean => {
    if (value === null) return false;
    const range = NORMAL_RANGES[vitalType as keyof typeof NORMAL_RANGES];
    return value < range.min || value > range.max;
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow">
          <p className="font-medium text-gray-900 mb-2">{label}</p>
          {payload.map((entry: any, index: number) => {
            if (entry.value === null || entry.value === undefined) return null;
            const isAbnormalValue = isAbnormal(entry.dataKey, entry.value);
            return (
              <p
                key={index}
                className={`text-sm ${isAbnormalValue ? 'text-red-600 font-semibold' : 'text-gray-700'}`}
              >
                <span style={{ color: entry.color }}>●</span> {entry.name}: {entry.value}
                {isAbnormalValue && ' (Abnormal)'}
              </p>
            );
          })}
        </div>
      );
    }
    return null;
  };

  const chartData = formatChartData();

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading vitals data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
        <button
          onClick={fetchVitals}
          className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
        >
          Retry
        </button>
      </div>
    );
  }

  if (vitals.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
        <p className="text-gray-500">No vitals data available for the selected time range.</p>
      </div>
    );
  }

  // Render chart based on selected vital
  const renderChart = (vitalType: string, label: string, unit: string, color: string) => {
    const dataKey = vitalType;
    const range = NORMAL_RANGES[vitalType as keyof typeof NORMAL_RANGES];
    
    return (
      <div key={vitalType} className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            {label} ({unit})
          </h3>
          <div className="text-sm text-gray-600">
            Normal: {range.min} - {range.max} {unit}
          </div>
        </div>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="timestamp"
              stroke="#6b7280"
              fontSize={12}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis stroke="#6b7280" fontSize={12} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <ReferenceLine
              y={range.min}
              stroke="#10b981"
              strokeDasharray="3 3"
              label={{ value: 'Min Normal', position: 'insideTopLeft' }}
            />
            <ReferenceLine
              y={range.max}
              stroke="#10b981"
              strokeDasharray="3 3"
              label={{ value: 'Max Normal', position: 'insideTopLeft' }}
            />
            <Line
              type="monotone"
              dataKey={dataKey}
              stroke={color}
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              name={label}
              connectNulls
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  };

  return (
    <div className="bg-white shadow rounded-xl border border-gray-200 p-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
        <div className="flex items-center gap-3 mb-4 md:mb-0">
          <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-indigo-100">
            <svg className="h-5 w-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900">Vital Signs Trends</h2>
        </div>
        <div className="flex flex-wrap gap-4">
          <div>
            <label htmlFor="time-range" className="block text-sm font-medium text-gray-700 mb-1">
              Time Range
            </label>
            <select
              id="time-range"
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as any)}
              className="px-3 py-2 border border-gray-300 rounded-md shadow focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-sm"
            >
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="all">All Time</option>
            </select>
          </div>
          <div>
            <label htmlFor="vital-select" className="block text-sm font-medium text-gray-700 mb-1">
              View
            </label>
            <select
              id="vital-select"
              value={selectedVital}
              onChange={(e) => setSelectedVital(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md shadow focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-sm"
            >
              <option value="all">All Vitals</option>
              <option value="hr">Heart Rate</option>
              <option value="bp">Blood Pressure</option>
              <option value="spo2">Oxygen Saturation</option>
              <option value="rr">Respiratory Rate</option>
              <option value="temp">Temperature</option>
              <option value="pain">Pain Scale</option>
            </select>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {selectedVital === 'all' || selectedVital === 'hr' ? (
          renderChart('hr', 'Heart Rate', 'bpm', CHART_COLORS.hr)
        ) : null}
        
        {selectedVital === 'all' || selectedVital === 'bp' ? (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Blood Pressure (mmHg)</h3>
              <div className="text-sm text-gray-600">
                Systolic: 90-140, Diastolic: 60-90
              </div>
            </div>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  dataKey="timestamp"
                  stroke="#6b7280"
                  fontSize={12}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <ReferenceLine y={90} stroke="#10b981" strokeDasharray="3 3" />
                <ReferenceLine y={140} stroke="#10b981" strokeDasharray="3 3" />
                <ReferenceLine y={60} stroke="#10b981" strokeDasharray="3 3" />
                <ReferenceLine y={90} stroke="#10b981" strokeDasharray="3 3" />
                <Line
                  type="monotone"
                  dataKey="bp_sys"
                  stroke={CHART_COLORS.bp_sys}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                  name="Systolic BP"
                  connectNulls
                />
                <Line
                  type="monotone"
                  dataKey="bp_dia"
                  stroke={CHART_COLORS.bp_dia}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                  name="Diastolic BP"
                  connectNulls
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : null}
        
        {selectedVital === 'all' || selectedVital === 'spo2' ? (
          renderChart('spo2', 'Oxygen Saturation', '%', CHART_COLORS.spo2)
        ) : null}
        
        {selectedVital === 'all' || selectedVital === 'rr' ? (
          renderChart('rr', 'Respiratory Rate', 'breaths/min', CHART_COLORS.rr)
        ) : null}
        
        {selectedVital === 'all' || selectedVital === 'temp' ? (
          renderChart('temp', 'Temperature', '°C', CHART_COLORS.temp)
        ) : null}
        
        {selectedVital === 'all' || selectedVital === 'pain' ? (
          renderChart('pain', 'Pain Scale', '0-10', CHART_COLORS.pain)
        ) : null}
      </div>

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-800">
          <strong>Note:</strong> Green dashed lines indicate normal ranges. Values outside these ranges are highlighted in red in the tooltip.
        </p>
      </div>
    </div>
  );
}

