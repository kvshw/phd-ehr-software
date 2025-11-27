/**
 * Weight Balance Card Component
 */
'use client';

import { HealthMetricsCard } from './HealthMetricsCard';
import { useEffect, useState } from 'react';

interface WeightBalanceCardProps {
  currentWeight?: number;
  maxWeight?: number;
  minWeight?: number;
  idealMin?: number;
  idealMax?: number;
  height?: number;
}

export function WeightBalanceCard({
  currentWeight = 73,
  maxWeight = 78,
  minWeight = 60,
  idealMin = 60,
  idealMax = 78,
  height = 178,
}: WeightBalanceCardProps) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Calculate progress percentage
    const range = maxWeight - minWeight;
    const current = currentWeight - minWeight;
    const percentage = (current / range) * 100;
    setProgress(Math.min(100, Math.max(0, percentage)));
  }, [currentWeight, maxWeight, minWeight]);

  return (
    <HealthMetricsCard
      title="Weight balance"
      value={currentWeight}
      unit="Kg"
      gradient="from-blue-50 to-cyan-50"
      normalRange={`${idealMin} kg - ${idealMax} kg ideal weight • ${height} cm height`}
    >
      <div className="mt-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-gray-600">Min {minWeight}kg</span>
          <span className="text-xs font-semibold text-blue-600">Max {maxWeight}kg</span>
        </div>
        <div className="relative h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-400 to-indigo-500 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          >
            <div className="absolute right-0 top-1/2 transform -translate-y-1/2 translate-x-1/2 w-4 h-4 bg-white rounded-full border-2 border-blue-500 shadow"></div>
          </div>
        </div>
      </div>
    </HealthMetricsCard>
  );
}

