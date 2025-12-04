/**
 * Admin System Controls Dashboard
 * System management, user administration, and configuration
 * Enhanced with Phase 7 Assurance Dashboard (shadow tests, rollouts, bias/drift)
 */
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { UserManagement } from '@/components/admin/UserManagement';
import { SystemStatusPanel } from '@/components/admin/SystemStatus';
import { SyntheticDataGenerator } from '@/components/admin/SyntheticDataGenerator';
import { AdaptationConfigPanel } from '@/components/admin/AdaptationConfig';
import { AssuranceDashboard } from '@/components/admin/AssuranceDashboard';
import { AnonymizedReferralOverview } from '@/components/admin/AnonymizedReferralOverview';
import { LogViewer } from '@/components/researcher/LogViewer';
import { TopHeader } from '@/components/layout/TopHeader';

export default function AdminControlsPage() {
  const router = useRouter();
  const { isAuthenticated, user, checkAuth, isLoading: authLoading } = useAuthStore();
  const [activeTab, setActiveTab] = useState<'system' | 'assurance' | 'referrals'>('system');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    checkAuth();
  }, []);

  // Don't render anything on server
  if (!mounted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    );
  }

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // If not authenticated after loading, show login message
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center p-8 bg-yellow-50 rounded-lg border border-yellow-200">
          <h2 className="text-xl font-bold text-yellow-700 mb-4">Session Expired</h2>
          <p className="text-gray-600 mb-4">Please login to continue</p>
          <button
            onClick={() => router.push('/login')}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <TopHeader currentPage="Settings" />
      <div className="max-w-[1600px] mx-auto px-6 py-8">
        <div>
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Admin System Controls</h1>
            <p className="mt-2 text-gray-600">
              System management, user administration, and configuration
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="mb-6 flex gap-2 border-b border-gray-200 pb-2">
            <button
              onClick={() => setActiveTab('system')}
              className={`px-4 py-2 rounded-t-lg font-medium transition-colors ${
                activeTab === 'system'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              System Management
            </button>
            <button
              onClick={() => setActiveTab('assurance')}
              className={`px-4 py-2 rounded-t-lg font-medium transition-colors ${
                activeTab === 'assurance'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Assurance & Governance
            </button>
            <button
              onClick={() => setActiveTab('referrals')}
              className={`px-4 py-2 rounded-t-lg font-medium transition-colors ${
                activeTab === 'referrals'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Referral Analytics
            </button>
          </div>

          {activeTab === 'system' ? (
            <>
              {/* System Status */}
              <div className="mb-8">
                <SystemStatusPanel />
              </div>

              {/* Main Content Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* User Management */}
                <div>
                  <UserManagement />
                </div>

                {/* Adaptation Configuration */}
                <div>
                  <AdaptationConfigPanel />
                </div>
              </div>

              {/* Synthetic Data Generator */}
              <div className="mb-8">
                <SyntheticDataGenerator />
              </div>

              {/* System Logs */}
              <div>
                <LogViewer />
              </div>
            </>
          ) : activeTab === 'assurance' ? (
            <>
              {/* Assurance Dashboard - Shadow Tests, Rollouts, Bias/Drift */}
              <div className="mb-6 bg-gradient-to-r from-purple-500 to-indigo-600 rounded-xl p-4 text-white">
                <h2 className="text-lg font-semibold">Runtime Assurance Layer</h2>
                <p className="text-sm text-purple-100">
                  Monitor shadow tests, gradual rollouts, and detect bias/drift in adaptations
                </p>
              </div>
              <AssuranceDashboard />
            </>
          ) : (
            <>
              {/* Anonymized Referral Analytics */}
              <AnonymizedReferralOverview />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
