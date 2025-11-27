/**
 * Admin System Controls Dashboard
 * System management, user administration, and configuration
 */
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { UserManagement } from '@/components/admin/UserManagement';
import { SystemStatusPanel } from '@/components/admin/SystemStatus';
import { SyntheticDataGenerator } from '@/components/admin/SyntheticDataGenerator';
import { AdaptationConfigPanel } from '@/components/admin/AdaptationConfig';
import { LogViewer } from '@/components/researcher/LogViewer';
import { TopHeader } from '@/components/layout/TopHeader';

export default function AdminControlsPage() {
  const router = useRouter();
  const { isAuthenticated, user, checkAuth, isLoading: authLoading } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    } else if (!authLoading && user && user.role !== 'admin') {
      router.push('/dashboard');
    }
  }, [isAuthenticated, authLoading, user, router]);

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || user?.role !== 'admin') {
    return null;
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
        </div>
      </div>
    </div>
  );
}
