/**
 * Hydration Level Card Component
 */
'use client';

import { HealthMetricsCard } from './HealthMetricsCard';

interface HydrationCardProps {
  percentage?: number;
  currentIntake?: number;
  dailyGoal?: number;
}

export function HydrationCard({
  percentage = 86,
  currentIntake = 1320,
  dailyGoal = 2000,
}: HydrationCardProps) {
  const circumference = 2 * Math.PI * 45; // radius = 45
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <HealthMetricsCard
      title="Hydration level"
      value={percentage}
      unit="%"
      gradient="from-cyan-50 to-blue-50"
    >
      <div className="mt-4 relative">
        <svg className="w-32 h-32 mx-auto transform -rotate-90">
          <circle
            cx="64"
            cy="64"
            r="45"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            className="text-gray-200"
          />
          <circle
            cx="64"
            cy="64"
            r="45"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="text-cyan-500 transition-all duration-1000"
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{percentage}%</div>
          </div>
        </div>
      </div>
      <div className="mt-4 text-center">
        <p className="text-sm text-gray-700">
          <span className="font-semibold">{currentIntake} ml</span> mineral water today
        </p>
        <p className="text-xs text-gray-500 mt-1">Daily goal: {dailyGoal} L per day</p>
      </div>
    </HealthMetricsCard>
  );
}

