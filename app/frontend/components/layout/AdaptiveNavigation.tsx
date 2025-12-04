/**
 * Adaptive Navigation Component
 * Navigation items adapt based on MAPE-K analysis of actual usage
 * Frequently used sections appear first, rarely used are hidden
 */
'use client';

import { useEffect, useState, useMemo } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { adaptiveDashboardService, DashboardPlan } from '@/lib/adaptiveDashboardService';
import { monitorService } from '@/lib/monitorService';

export interface NavItem {
  id: string;
  label: string;
  icon: string;
  featureId: string; // Maps to MAPE-K feature tracking
  href?: string; // Optional direct href
  defaultVisible: boolean;
  defaultPriority: number; // For fallback when no plan
  roleRestrictions?: string[]; // Which roles can see this
}

// All available navigation items
const ALL_NAV_ITEMS: NavItem[] = [
  {
    id: 'overview',
    label: 'Overview',
    icon: '',
    featureId: 'dashboard_overview',
    href: '/dashboard',
    defaultVisible: true,
    defaultPriority: 10,
  },
  {
    id: 'notes',
    label: 'Notes',
    icon: '',
    featureId: 'clinical_notes',
    defaultVisible: true,
    defaultPriority: 9,
  },
  {
    id: 'document',
    label: 'Document',
    icon: '📄',
    featureId: 'imaging_documents',
    defaultVisible: true,
    defaultPriority: 8,
  },
  {
    id: 'labs',
    label: 'Labs',
    icon: '',
    featureId: 'lab_results',
    defaultVisible: true,
    defaultPriority: 8,
  },
  {
    id: 'schedule',
    label: 'Schedule',
    icon: '📅',
    featureId: 'appointments_schedule',
    defaultVisible: true,
    defaultPriority: 7,
  },
  {
    id: 'doctor',
    label: 'Doctor',
    icon: '',
    featureId: 'doctor_consultation',
    defaultVisible: true,
    defaultPriority: 6,
  },
  {
    id: 'medicine',
    label: 'Medicine',
    icon: '',
    featureId: 'medications',
    defaultVisible: true,
    defaultPriority: 8,
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: '',
    featureId: 'research_analytics',
    href: '/research',
    defaultVisible: false,
    defaultPriority: 5,
    roleRestrictions: ['researcher', 'admin'],
  },
];

interface AdaptiveNavigationProps {
  currentPage?: string;
  onNavClick?: (itemId: string) => void;
}

export function AdaptiveNavigation({ currentPage = 'Overview', onNavClick }: AdaptiveNavigationProps) {
  const { user } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();
  const [plan, setPlan] = useState<DashboardPlan | null>(null);
  const [loading, setLoading] = useState(true);

  // Fetch adaptation plan
  useEffect(() => {
    const fetchPlan = async () => {
      if (!user || user.role !== 'clinician') {
        setLoading(false);
        return; // Only adapt for clinicians
      }

      try {
        const dashboardPlan = await adaptiveDashboardService.getPlan();
        setPlan(dashboardPlan);
      } catch (error) {
        console.error('Failed to fetch navigation plan:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPlan();
    
    // Refresh plan every 5 minutes
    const interval = setInterval(fetchPlan, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [user]);

  // Apply adaptive ordering and filtering
  const adaptedNavItems = useMemo(() => {
    // Filter by role restrictions
    let items = ALL_NAV_ITEMS.filter(item => {
      if (item.roleRestrictions && user?.role) {
        return item.roleRestrictions.includes(user.role);
      }
      return true;
    });

    if (!plan || plan.feature_priority.length === 0) {
      // No plan - use defaults
      return items
        .filter(item => item.defaultVisible)
        .sort((a, b) => b.defaultPriority - a.defaultPriority);
    }

    // Create priority map from plan
    const priorityMap = new Map<string, { position: number; usage_count: number }>();
    plan.feature_priority.forEach(f => {
      priorityMap.set(f.id, {
        position: f.position,
        usage_count: f.usage_count,
      });
    });

    // Get hidden features
    const hiddenSet = new Set(plan.hidden_features);

    // Sort by plan priority
    const visibleItems = items
      .filter(item => {
        // Hide if in hidden list
        if (hiddenSet.has(item.featureId)) {
          return false;
        }
        // Show if in plan or default visible
        return priorityMap.has(item.featureId) || item.defaultVisible;
      })
      .sort((a, b) => {
        const aPriority = priorityMap.get(a.featureId);
        const bPriority = priorityMap.get(b.featureId);
        
        if (aPriority && bPriority) {
          return aPriority.position - bPriority.position;
        }
        if (aPriority) return -1;
        if (bPriority) return 1;
        return b.defaultPriority - a.defaultPriority;
      });

    return visibleItems;
  }, [plan, user]);

  const handleNavClick = async (item: NavItem, e?: React.MouseEvent) => {
    e?.preventDefault();
    e?.stopPropagation();

    console.log('Navigation clicked:', item.id, item);

    // Track navigation for adaptation (non-blocking)
    monitorService.logDashboardAction({
      actionType: 'navigation',
      featureId: item.featureId,
      metadata: {
        nav_item_id: item.id,
        specialty: user?.specialty,
        time_of_day: new Date().getHours(),
      },
    }).catch(err => {
      console.error('Failed to log navigation:', err);
      // Don't block navigation on tracking failure
    });

    // Call custom handler if provided (with item.id for backward compatibility)
    if (onNavClick) {
      onNavClick(item.id);
      return;
    }

    // Default navigation logic
    try {
      if (item.href) {
        console.log('Navigating to:', item.href);
        router.push(item.href);
        return;
      }

      // Handle patient page navigation
      if (pathname?.startsWith('/patients/')) {
        const patientId = pathname.split('/patients/')[1]?.split('/')[0];
        if (patientId) {
          const sectionMap: Record<string, string> = {
            notes: 'notes',
            labs: 'labs',
            medicine: 'medications',
            document: 'imaging',
          };
          const section = sectionMap[item.id];
          if (section) {
            const targetUrl = `/patients/${patientId}?section=${section}`;
            console.log('Navigating to patient section:', targetUrl);
            router.push(targetUrl);
            // Small delay before reload to let router update
            setTimeout(() => {
              window.location.reload();
            }, 150);
            return;
          }
        }
      }

      // For items without href and not on patient page, navigate based on item type
      const defaultRoutes: Record<string, string> = {
        notes: '/dashboard',
        labs: '/dashboard',
        medicine: '/dashboard',
        document: '/dashboard',
        schedule: '/dashboard',
        doctor: '/dashboard',
      };

      const targetRoute = defaultRoutes[item.id] || '/dashboard';
      console.log('Navigating to default route:', targetRoute);
      router.push(targetRoute);
    } catch (error) {
      console.error('Navigation error:', error);
      // Fallback to dashboard on error
      router.push('/dashboard');
    }
  };

  if (loading) {
    // Show default navigation while loading
    return (
      <nav className="hidden md:flex items-center space-x-1">
        {ALL_NAV_ITEMS
          .filter(item => item.defaultVisible && (!item.roleRestrictions || item.roleRestrictions.includes(user?.role || '')))
          .map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={(e) => handleNavClick(item, e)}
              className={`relative px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                currentPage.toLowerCase() === item.id.toLowerCase()
                  ? 'text-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50'
              }`}
            >
              {item.label}
              {currentPage.toLowerCase() === item.id.toLowerCase() && (
                <span className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-blue-600 rounded-full"></span>
              )}
            </button>
          ))}
      </nav>
    );
  }

  // Fallback to default items if adaptedNavItems is empty
  const displayItems = adaptedNavItems.length > 0 
    ? adaptedNavItems 
    : ALL_NAV_ITEMS.filter(item => 
        item.defaultVisible && 
        (!item.roleRestrictions || item.roleRestrictions.includes(user?.role || ''))
      ).sort((a, b) => b.defaultPriority - a.defaultPriority);

  return (
    <nav className="hidden md:flex items-center space-x-1">
      {displayItems.map((item) => {
        const featureInfo = plan?.feature_priority.find(f => f.id === item.featureId);
        const isActive = currentPage.toLowerCase() === item.id.toLowerCase() || 
                        pathname === item.href;

        return (
          <button
            key={item.id}
            type="button"
            onClick={(e) => handleNavClick(item, e)}
            className={`relative px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
              isActive
                ? 'text-blue-600 bg-blue-50'
                : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50'
            }`}
            title={featureInfo ? `Used ${featureInfo.usage_count} times` : undefined}
          >
            <span className="mr-1">{item.icon}</span>
            {item.label}
            {isActive && (
              <span className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-blue-600 rounded-full"></span>
            )}
            {/* Show usage indicator for frequently used items */}
            {featureInfo && featureInfo.usage_count > 10 && (
              <span className="ml-1 text-xs text-blue-500">●</span>
            )}
          </button>
        );
      })}
      
      {/* Show "More" dropdown for hidden items if plan exists */}
      {plan && plan.hidden_features.length > 0 && (
        <div className="relative group">
          <button className="px-4 py-2 rounded-lg text-sm font-medium text-gray-600 hover:text-blue-600 hover:bg-gray-50 transition-all">
            More ▼
          </button>
          <div className="absolute top-full left-0 mt-1 bg-white rounded-lg shadow-lg border border-gray-200 py-1 min-w-[150px] opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
            {ALL_NAV_ITEMS
              .filter(item => plan.hidden_features.includes(item.featureId))
              .map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={(e) => handleNavClick(item, e)}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  <span className="mr-2">{item.icon}</span>
                  {item.label}
                </button>
              ))}
          </div>
        </div>
      )}
    </nav>
  );
}

