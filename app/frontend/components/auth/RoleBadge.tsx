/**
 * Role Badge Component
 * Displays user role with icon and color coding
 */
'use client';

import { UserRole } from './RoleSelector';

interface RoleBadgeProps {
  role: UserRole;
  size?: 'sm' | 'md' | 'lg';
  showDescription?: boolean;
  className?: string;
}

const roleConfig: Record<UserRole, {
  label: string;
  icon: string;
  color: {
    bg: string;
    text: string;
    border: string;
  };
  description: string;
}> = {
  clinician: {
    label: 'Doctor',
    icon: 'DR',
    color: {
      bg: 'bg-blue-100',
      text: 'text-blue-800',
      border: 'border-blue-200',
    },
    description: 'Patient care and AI suggestions',
  },
  doctor: {
    label: 'Doctor',
    icon: 'DR',
    color: {
      bg: 'bg-blue-100',
      text: 'text-blue-800',
      border: 'border-blue-200',
    },
    description: 'Patient care and AI suggestions',
  },
  nurse: {
    label: 'Nurse',
    icon: 'RN',
    color: {
      bg: 'bg-teal-100',
      text: 'text-teal-800',
      border: 'border-teal-200',
    },
    description: 'Patient triage and care coordination',
  },
  researcher: {
    label: 'Researcher',
    icon: 'RS',
    color: {
      bg: 'bg-purple-100',
      text: 'text-purple-800',
      border: 'border-purple-200',
    },
    description: 'Analytics and research data',
  },
  admin: {
    label: 'Administrator',
    icon: 'AD',
    color: {
      bg: 'bg-indigo-100',
      text: 'text-indigo-800',
      border: 'border-indigo-200',
    },
    description: 'System controls and management',
  },
};

export function RoleBadge({ role, size = 'md', showDescription = false, className = '' }: RoleBadgeProps) {
  const config = roleConfig[role];
  
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  return (
    <div className={`inline-flex items-center gap-2 rounded-full border ${config.color.bg} ${config.color.text} ${config.color.border} ${sizeClasses[size]} ${className}`}>
      <span className="text-xs font-bold leading-none">{config.icon}</span>
      <span className="font-medium">{config.label}</span>
      {showDescription && size === 'lg' && (
        <span className="text-xs opacity-75 ml-1">- {config.description}</span>
      )}
    </div>
  );
}

