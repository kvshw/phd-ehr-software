/**
 * Sleep Periodic Card Component
 */
'use client';

import { HealthMetricsCard } from './HealthMetricsCard';

interface SleepPeriodicCardProps {
  avgSleep?: number;
  goalSleep?: number;
  deepSleep?: number;
  totalSleep?: string;
}

export function SleepPeriodicCard({
  avgSleep = 6.2,
  goalSleep = 8,
  deepSleep = 1.6,
  totalSleep = '9 Hours 40 minutes',
}: SleepPeriodicCardProps) {
  const months = ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'];
  const sleepData = [6.5, 7.2, 6.8, 7.5, 6.2, 6.9]; // Sample data
  const maxSleep = Math.max(...sleepData, goalSleep);

  const getMoonIcon = () => (
    <svg className="w-5 h-5 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
      <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
    </svg>
  );

  return (
    <HealthMetricsCard
      title="Sleep periodic"
      subtitle="Control your sleep to create great habit"
      value={avgSleep}
      unit="Hours"
      icon={getMoonIcon()}
      gradient="from-indigo-50 to-purple-50"
    >
      <div className="mt-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <span className="text-2xl font-bold text-gray-900">{avgSleep}</span>
            <span className="text-sm text-gray-600 ml-1">Hours</span>
          </div>
          <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold">
            Goal {goalSleep}h
          </span>
        </div>

        {/* Bar Chart */}
        <div className="space-y-2">
          {months.map((month, index) => {
            const height = (sleepData[index] / maxSleep) * 100;
            const deepHeight = (deepSleep / maxSleep) * 100;
            return (
              <div key={month} className="flex items-center gap-2">
                <span className="text-xs text-gray-600 w-8">{month}</span>
                <div className="flex-1 relative h-6 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-indigo-400 to-indigo-600 rounded-full transition-all duration-500"
                    style={{ height: `${height}%` }}
                  >
                    <div
                      className="absolute bottom-0 left-0 w-full bg-indigo-800 rounded-full"
                      style={{ height: `${deepHeight}%` }}
                    ></div>
                  </div>
                  <span className="absolute inset-0 flex items-center justify-center text-xs font-semibold text-gray-700">
                    {sleepData[index]}H
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-600">Deep Sleep: {deepSleep} Hours</span>
            <span className="text-gray-900 font-semibold">{totalSleep}</span>
          </div>
        </div>
      </div>
    </HealthMetricsCard>
  );
}

