/**
 * Blood Tracking Card Component
 */
'use client';

import { HealthMetricsCard } from './HealthMetricsCard';
import { useState } from 'react';

interface BloodTrackingCardProps {
  subtitle?: string;
}

export function BloodTrackingCard({
  subtitle = 'Orthopedic Doctors',
}: BloodTrackingCardProps) {
  const [selectedDay, setSelectedDay] = useState('Today');
  const hours = ['06.00', '09.00', '12.00', '15.00', '18.00', '21.00'];
  
  // Sample data for different metrics
  const metrics = [
    { name: 'Cholesterol Levels', color: 'bg-blue-600', data: [160, 170, 165, 175, 168, 172] },
    { name: 'Iron Levels', color: 'bg-cyan-400', data: [76, 80, 78, 82, 79, 81] },
    { name: 'Sugar level', color: 'bg-indigo-500', data: [97, 95, 98, 96, 99, 97] },
    { name: 'Heart Rate', color: 'bg-purple-600', data: [72, 75, 73, 76, 74, 75] },
  ];

  return (
    <HealthMetricsCard
      title="Blood tracking"
      subtitle={subtitle}
      gradient="from-blue-50 to-indigo-50"
      className="col-span-2"
    >
      <div className="mt-4">
        {/* Time Selector */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            {['Today', 'Week', 'Month'].map((day) => (
              <button
                key={day}
                onClick={() => setSelectedDay(day)}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                  selectedDay === day
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {day}
              </button>
            ))}
          </div>
        </div>

        {/* Grid Chart */}
        <div className="grid grid-cols-6 gap-2 mb-4">
          {hours.map((hour, hourIndex) => (
            <div key={hour} className="flex flex-col items-center">
              <span className="text-xs text-gray-600 mb-2">{hour}</span>
              <div className="flex flex-col gap-1 w-full">
                {metrics.map((metric, metricIndex) => {
                  const value = metric.data[hourIndex];
                  const maxValue = 200;
                  const height = (value / maxValue) * 100;
                  return (
                    <div
                      key={metricIndex}
                      className={`${metric.color} rounded opacity-80 hover:opacity-100 transition-opacity cursor-pointer group relative`}
                      style={{ height: `${Math.max(20, height)}%`, minHeight: '8px' }}
                      title={`${metric.name}: ${value}`}
                    >
                      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-1 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                        {value}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Legend */}
        <div className="flex flex-wrap gap-4 text-xs">
          {metrics.map((metric, index) => (
            <div key={index} className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded ${metric.color}`}></div>
              <span className="text-gray-600">{metric.name}</span>
            </div>
          ))}
        </div>
      </div>
    </HealthMetricsCard>
  );
}

