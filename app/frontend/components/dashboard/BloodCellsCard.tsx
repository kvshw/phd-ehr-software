/**
 * Blood Cells Card Component
 */
'use client';

import { HealthMetricsCard } from './HealthMetricsCard';
import { useEffect, useState } from 'react';

interface BloodCellsCardProps {
  count?: number;
  advice?: string;
}

export function BloodCellsCard({
  count = 1100,
  advice = 'Need more sleep',
}: BloodCellsCardProps) {
  const [cells, setCells] = useState<Array<{ x: number; y: number; size: number }>>([]);

  useEffect(() => {
    // Generate cell positions for visualization
    const newCells: Array<{ x: number; y: number; size: number }> = [];
    for (let i = 0; i < 15; i++) {
      newCells.push({
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: Math.random() * 8 + 4,
      });
    }
    setCells(newCells);
  }, []);

  return (
    <HealthMetricsCard
      title="Blood cells"
      value={count}
      unit="UL"
      gradient="from-purple-50 to-pink-50"
      advice={advice}
      normalRange="4k - 11k cells in normal"
    >
      <div className="mt-4 h-20 relative">
        <svg className="w-full h-full">
          {cells.map((cell, index) => (
            <g key={index}>
              <circle
                cx={`${cell.x}%`}
                cy={`${cell.y}%`}
                r={cell.size}
                fill="url(#cellGradient)"
                className="opacity-80"
              />
              {index < cells.length - 1 && (
                <line
                  x1={`${cell.x}%`}
                  y1={`${cell.y}%`}
                  x2={`${cells[index + 1].x}%`}
                  y2={`${cells[index + 1].y}%`}
                  stroke="#9333ea"
                  strokeWidth="1"
                  opacity="0.3"
                />
              )}
            </g>
          ))}
          <defs>
            <linearGradient id="cellGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#9333ea" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#ec4899" stopOpacity="0.6" />
            </linearGradient>
          </defs>
        </svg>
      </div>
    </HealthMetricsCard>
  );
}

