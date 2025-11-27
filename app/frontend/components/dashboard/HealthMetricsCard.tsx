/**
 * Health Metrics Card Component
 * Reusable card for displaying health metrics with advanced visualizations
 */
'use client';

import { ReactNode } from 'react';

interface HealthMetricsCardProps {
  title: string;
  subtitle?: string;
  value: string | number;
  unit?: string;
  icon?: ReactNode;
  children?: ReactNode;
  className?: string;
  gradient?: string;
  advice?: string;
  normalRange?: string;
}

export function HealthMetricsCard({
  title,
  subtitle,
  value,
  unit,
  icon,
  children,
  className = '',
  gradient = 'from-blue-50 to-indigo-50',
  advice,
  normalRange,
}: HealthMetricsCardProps) {
  return (
    <div className={`bg-white rounded-2xl shadow border border-gray-200 p-6 hover:shadow-md transition-all duration-300 ${className}`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            {icon && <div className="text-blue-600">{icon}</div>}
            <h3 className="text-sm font-semibold text-gray-700">{title}</h3>
          </div>
          {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
        </div>
      </div>

      <div className={`bg-gradient-to-br ${gradient} rounded-xl p-4 mb-4`}>
        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-3xl font-bold text-gray-900">{value}</span>
          {unit && <span className="text-lg text-gray-600">{unit}</span>}
        </div>
        {children}
      </div>

      {advice && (
        <div className="flex items-center gap-2 text-xs text-amber-600 bg-amber-50 rounded-lg px-3 py-2 mb-2">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <span className="font-medium">{advice}</span>
        </div>
      )}

      {normalRange && (
        <p className="text-xs text-gray-500">{normalRange}</p>
      )}
    </div>
  );
}

