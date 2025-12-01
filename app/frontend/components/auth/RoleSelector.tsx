/**
 * Role Selector Component
 * Visual role selection cards for login page
 */
'use client';

export type UserRole = 'clinician' | 'researcher' | 'admin' | 'nurse' | 'doctor';

interface RoleOption {
  id: UserRole;
  label: string;
  icon: string;
  description: string;
  color: {
    bg: string;
    border: string;
    selectedBg: string;
    selectedBorder: string;
    text: string;
  };
}

interface RoleSelectorProps {
  selectedRole: UserRole | null;
  onRoleSelect: (role: UserRole) => void;
  disabled?: boolean;
}

const roles: RoleOption[] = [
  {
    id: 'clinician',
    label: 'Doctor',
    icon: '👨‍⚕️',
    description: 'Access patient records, vitals, and AI suggestions',
    color: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      selectedBg: 'bg-blue-100',
      selectedBorder: 'border-blue-400',
      text: 'text-blue-700',
    },
  },
  {
    id: 'nurse',
    label: 'Nurse',
    icon: '👩‍⚕️',
    description: 'Patient triage, routing, and care coordination',
    color: {
      bg: 'bg-teal-50',
      border: 'border-teal-200',
      selectedBg: 'bg-teal-100',
      selectedBorder: 'border-teal-400',
      text: 'text-teal-700',
    },
  },
  {
    id: 'researcher',
    label: 'Researcher',
    icon: '📊',
    description: 'View analytics, metrics, and research data',
    color: {
      bg: 'bg-purple-50',
      border: 'border-purple-200',
      selectedBg: 'bg-purple-100',
      selectedBorder: 'border-purple-400',
      text: 'text-purple-700',
    },
  },
  {
    id: 'admin',
    label: 'Administrator',
    icon: '⚙️',
    description: 'System controls and user management',
    color: {
      bg: 'bg-indigo-50',
      border: 'border-indigo-200',
      selectedBg: 'bg-indigo-100',
      selectedBorder: 'border-indigo-400',
      text: 'text-indigo-700',
    },
  },
];

export function RoleSelector({ selectedRole, onRoleSelect, disabled = false }: RoleSelectorProps) {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700 mb-3">
        Select Your Role
      </label>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {roles.map((role) => {
          const isSelected = selectedRole === role.id;
          return (
            <button
              key={role.id}
              type="button"
              onClick={() => !disabled && onRoleSelect(role.id)}
              disabled={disabled}
              className={`
                relative p-4 rounded-xl border-2 transition-all duration-200
                ${isSelected 
                  ? `${role.color.selectedBg} ${role.color.selectedBorder} shadow-md scale-[1.02]` 
                  : `${role.color.bg} ${role.color.border} hover:shadow-sm hover:scale-[1.01]`
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                focus:outline-none focus:ring-2 focus:ring-offset-2 ${role.color.selectedBorder.replace('border-', 'focus:ring-')}
              `}
            >
              {/* Selection Indicator */}
              {isSelected && (
                <div className="absolute top-2 right-2">
                  <div className={`h-5 w-5 rounded-full ${role.color.selectedBorder.replace('border-', 'bg-').replace('-400', '-600')} flex items-center justify-center`}>
                    <svg className="h-3 w-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              )}

              {/* Role Icon */}
              <div className="text-center mb-2">
                <div className="text-4xl mb-2">{role.icon}</div>
                <h3 className={`font-semibold ${role.color.text}`}>{role.label}</h3>
              </div>

              {/* Role Description */}
              <p className="text-xs text-gray-600 text-center leading-tight">
                {role.description}
              </p>
            </button>
          );
        })}
      </div>
      
      {selectedRole && (
        <p className="text-xs text-gray-500 text-center mt-2">
          Selected: <span className="font-medium">{roles.find(r => r.id === selectedRole)?.label}</span>
        </p>
      )}
    </div>
  );
}

