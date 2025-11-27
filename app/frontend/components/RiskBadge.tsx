/**
 * Risk badge component for patient risk levels
 */
'use client';

export type RiskLevel = 'routine' | 'needs_attention' | 'high_concern';

interface RiskBadgeProps {
  level: RiskLevel;
  className?: string;
}

export function RiskBadge({ level, className = '' }: RiskBadgeProps) {
  const styles = {
    routine: 'bg-green-100 text-green-800 border-green-300',
    needs_attention: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    high_concern: 'bg-red-100 text-red-800 border-red-300',
  };

  const labels = {
    routine: 'Routine',
    needs_attention: 'Needs Attention',
    high_concern: 'High Concern',
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles[level]} ${className}`}
    >
      {labels[level]}
    </span>
  );
}

