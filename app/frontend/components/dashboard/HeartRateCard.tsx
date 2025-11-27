/**
 * Heart Rate Card Component
 */
'use client';

import { HealthMetricsCard } from './HealthMetricsCard';
import { useEffect, useState } from 'react';

interface HeartRateCardProps {
  heartRate?: number;
  advice?: string;
}

export function HeartRateCard({
  heartRate = 90,
  advice = 'Reduce caffeine',
}: HeartRateCardProps) {
  const [beats, setBeats] = useState<number[]>([]);

  useEffect(() => {
    // Generate heartbeat visualization
    const generateBeats = () => {
      const newBeats: number[] = [];
      for (let i = 0; i < 20; i++) {
        newBeats.push(Math.random() * 40 + 20);
      }
      setBeats(newBeats);
    };
    generateBeats();
    const interval = setInterval(generateBeats, 2000);
    return () => clearInterval(interval);
  }, []);

  const getHeartIcon = () => (
    <svg className="w-5 h-5 text-red-500 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
    </svg>
  );

  return (
    <HealthMetricsCard
      title="Heart rate"
      value={heartRate}
      unit="bpm"
      icon={getHeartIcon()}
      gradient="from-red-50 to-pink-50"
      advice={advice}
      normalRange="60 - 100 beats per minute"
    >
      <div className="mt-4 h-16 flex items-end gap-1">
        {beats.map((height, index) => (
          <div
            key={index}
            className="flex-1 bg-gradient-to-t from-red-400 to-pink-400 rounded-t transition-all duration-300"
            style={{ height: `${height}%` }}
          ></div>
        ))}
      </div>
    </HealthMetricsCard>
  );
}

