/**
 * Top Header Component
 * Modern header with navigation, search, notifications, and user profile
 */
'use client';

import { useAuthStore } from '@/store/authStore';
import { useRouter } from 'next/navigation';
import { useState, useRef, useEffect } from 'react';
import { RoleBadge } from '@/components/auth/RoleBadge';
import { useDemoMode } from '@/components/demo/DemoMode';
import { monitorService } from '@/lib/monitorService';

interface TopHeaderProps {
  currentPage?: string;
}

export function TopHeader({ currentPage = 'Overview' }: TopHeaderProps) {
  const { user, logout, isLoading } = useAuthStore();
  const router = useRouter();
  const [notifications, setNotifications] = useState(3);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  // Get demo mode controls from context
  const demoControls = useDemoMode();

  // Navigation items with tracking
  const navItems = [
    { id: 'overview', label: 'Overview', icon: '', href: '/dashboard' },
    { id: 'notes', label: 'Notes', icon: '' },
    { id: 'document', label: 'Document', icon: '📄' },
    { id: 'labs', label: 'Labs', icon: '' },
    { id: 'schedule', label: 'Schedule', icon: '📅' },
    { id: 'doctor', label: 'Doctor', icon: '' },
    { id: 'medicine', label: 'Medicine', icon: '' },
    { id: 'analytics', label: 'Analytics', icon: '', href: '/research' },
  ];

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
    };

    if (showUserMenu) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showUserMenu]);

  const handleNavClick = (itemId: string) => {
    console.log('Nav clicked:', itemId);
    
    // Track for MAPE-K (non-blocking)
    monitorService.logDashboardAction({
      actionType: 'navigation',
      featureId: `nav_${itemId}`,
      metadata: { specialty: user?.specialty },
    }).catch(() => {});

    switch (itemId) {
      case 'overview':
        router.push('/dashboard');
        break;
      case 'notes':
        if (window.location.pathname.startsWith('/patients/')) {
          const patientId = window.location.pathname.split('/patients/')[1]?.split('/')[0];
          if (patientId) {
            router.push(`/patients/${patientId}?section=notes`);
            setTimeout(() => window.location.reload(), 100);
          }
        } else {
          router.push('/dashboard');
        }
        break;
      case 'labs':
        if (window.location.pathname.startsWith('/patients/')) {
          const patientId = window.location.pathname.split('/patients/')[1]?.split('/')[0];
          if (patientId) {
            router.push(`/patients/${patientId}?section=labs`);
            setTimeout(() => window.location.reload(), 100);
          }
        } else {
          router.push('/dashboard');
        }
        break;
      case 'medicine':
        if (window.location.pathname.startsWith('/patients/')) {
          const patientId = window.location.pathname.split('/patients/')[1]?.split('/')[0];
          if (patientId) {
            router.push(`/patients/${patientId}?section=medications`);
            setTimeout(() => window.location.reload(), 100);
          }
        } else {
          router.push('/dashboard');
        }
        break;
      case 'document':
        if (window.location.pathname.startsWith('/patients/')) {
          const patientId = window.location.pathname.split('/patients/')[1]?.split('/')[0];
          if (patientId) {
            router.push(`/patients/${patientId}?section=imaging`);
            setTimeout(() => window.location.reload(), 100);
          }
        } else {
          router.push('/dashboard');
        }
        break;
      case 'schedule':
        router.push('/dashboard');
        break;
      case 'analytics':
        router.push('/research');
        break;
      default:
        router.push('/dashboard');
        break;
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      // Redirect is handled in the auth store
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <header className="bg-white border-b border-gray-200/80 backdrop-blur-sm sticky top-0 z-50 shadow">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Left: Logo and Navigation */}
          <div className="flex items-center space-x-8">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center h-10 w-10 rounded-xl bg-gradient-to-br from-blue-400 to-indigo-500 shadow">
                <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                EHR Platform
              </span>
            </div>

            {/* Navigation */}
            <nav className="flex items-center space-x-1">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => handleNavClick(item.id)}
                  className={`relative px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer ${
                    currentPage.toLowerCase() === item.id.toLowerCase()
                      ? 'text-blue-600 bg-blue-50'
                      : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50'
                  }`}
                >
                  <span className="mr-1">{item.icon}</span>
                  {item.label}
                  {currentPage.toLowerCase() === item.id.toLowerCase() && (
                    <span className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-blue-600 rounded-full"></span>
                  )}
                </button>
              ))}
            </nav>
          </div>

          {/* Right: Demo, Search, Notifications, Alerts, User */}
          <div className="flex items-center space-x-4">
            {/* Demo Mode Button */}
            {!demoControls.isActive && (
              <button
                onClick={demoControls.startDemo}
                className="px-3 py-1.5 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-lg hover:from-indigo-600 hover:to-purple-600 shadow hover:shadow-lg transition-all flex items-center gap-1.5 text-xs font-medium"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Demo
              </button>
            )}

            {/* Search */}
            <button className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>

            {/* Notifications */}
            <button className="relative p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              {notifications > 0 && (
                <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full border-2 border-white"></span>
              )}
            </button>

            {/* Alerts */}
            <button className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </button>

            {/* User Profile */}
            <div className="relative pl-4 border-l border-gray-200" ref={userMenuRef}>
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-3 hover:opacity-80 transition-opacity focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-lg p-1"
                aria-label="User menu"
              >
                <div className="text-right hidden sm:block">
                  <p className="text-sm font-semibold text-gray-900">
                    Hi, {user?.first_name || user?.email?.split('@')[0] || 'User'}
                  </p>
                  {user?.role && (
                    <div className="mt-1 flex justify-end">
                      <RoleBadge role={user.role} size="sm" />
                    </div>
                  )}
                </div>
                <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white font-semibold shadow ring-2 ring-white">
                  {(user?.first_name?.charAt(0) || user?.email?.charAt(0) || 'U').toUpperCase()}
                </div>
                <svg
                  className={`w-4 h-4 text-gray-500 transition-transform ${showUserMenu ? 'rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* Dropdown Menu */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                  <div className="px-4 py-3 border-b border-gray-100">
                    <p className="text-sm font-semibold text-gray-900">
                      {user?.first_name && user?.last_name 
                        ? `${user.first_name} ${user.last_name}`
                        : user?.first_name 
                        ? user.first_name
                        : user?.email || 'User'}
                    </p>
                    {user?.email && (
                      <p className="text-xs text-gray-500 mt-0.5">{user.email}</p>
                    )}
                    {user?.role && (
                      <div className="mt-1 flex items-center gap-2">
                        <RoleBadge role={user.role} size="sm" />
                        {user?.specialty && (
                          <span className="text-xs text-gray-500 capitalize">{user.specialty}</span>
                        )}
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => { setShowUserMenu(false); router.push('/settings'); }}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors flex items-center space-x-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <span>Profile & Specialty</span>
                  </button>
                  <button
                    onClick={() => { setShowUserMenu(false); router.push('/research'); }}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors flex items-center space-x-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <span>Research Analytics</span>
                  </button>
                  <div className="border-t border-gray-100 mt-1">
                    <button
                      onClick={handleLogout}
                      disabled={isLoading}
                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      <span>{isLoading ? 'Logging out...' : 'Logout'}</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

