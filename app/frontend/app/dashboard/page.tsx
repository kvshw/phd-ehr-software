'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { useRouter } from 'next/navigation';
import { TopHeader } from '@/components/layout/TopHeader';
import { AppointmentSidebar } from '@/components/dashboard/AppointmentSidebar';
import { PatientCardGrid } from '@/components/dashboard/PatientCardGrid';
import { SpecialtyBanner } from '@/components/dashboard/SpecialtyBanner';
import { SpecialtyQuickActions } from '@/components/dashboard/SpecialtyQuickActions';
import { AdaptiveDashboard, DashboardSection } from '@/components/dashboard/AdaptiveDashboard';
import { getAllAvailableWidgets } from '@/components/dashboard/SpecialtyWidgets';
import { BanditIndicatorCompact } from '@/components/adaptation/BanditIndicator';
import { ChangeLogDrawer } from '@/components/dashboard/ChangeLogDrawer';
import { IncomingReferrals } from '@/components/dashboard/IncomingReferrals';
import { monitorService } from '@/lib/monitorService';
import { patientService } from '@/lib/patientService';

export default function DashboardPage() {
  const { user, isAuthenticated, checkAuth, isLoading } = useAuthStore();
  const router = useRouter();
  const [todayPatients, setTodayPatients] = useState<Array<{
    id: string;
    name: string;
    age: number;
    time: string;
  }>>([]);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [totalPatients, setTotalPatients] = useState(0);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    } else if (!isLoading && user) {
      // Role-based redirects
      if (user.role === 'admin') {
        router.push('/admin/controls');
      } else if (user.role === 'researcher') {
        router.push('/research');
      } else if (user.role === 'nurse') {
        router.push('/nurse/dashboard');
      }
      // Clinicians stay on /dashboard
    }
  }, [isAuthenticated, isLoading, user, router]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchTodayPatients();
    }
  }, [isAuthenticated]);

  const fetchTodayPatients = async () => {
    try {
      const response = await patientService.getPatients({ page: 1, page_size: 5 });
      setTotalPatients(response.total);
      // Transform to today's patients format with sample times
      const times = ['11.00 AM', '13.00 PM', '14.00 PM', '15.00 PM', '16.00 PM'];
      const patients = response.items.slice(0, 5).map((patient, index) => ({
        id: patient.id,
        name: patient.name,
        age: patient.age,
        time: times[index] || 'TBD',
      }));
      setTodayPatients(patients);
    } catch (error) {
      console.error('Error fetching today patients:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  const formattedDate = currentDate.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
  const formattedTime = currentDate.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="min-h-screen bg-white">
      {/* Top Header */}
      <TopHeader currentPage="Overview" />

      {/* Main Content */}
      <div className="max-w-[1600px] mx-auto px-6 py-8">
        <div className="flex gap-6">
          {/* Left Sidebar - Appointments */}
          <div className="flex-shrink-0">
            <AppointmentSidebar todayPatients={todayPatients} />
          </div>

          {/* Main Content Area */}
          <div className="flex-1 space-y-6">
            {/* Role-based content */}
            {user.role === 'clinician' && (
              <>
                {/* Specialty Banner - Shows if clinician has selected a specialty */}
                {user.specialty && (
                  <div className="flex items-start gap-3">
                    <div className="flex-1">
                      <SpecialtyBanner specialty={user.specialty} userName={user.first_name || user.email?.split('@')[0]} />
                    </div>
                    <BanditIndicatorCompact />
                  </div>
                )}

                {/* Prompt to set specialty if not set (only for clinicians) */}
                {!user.specialty && (
                  <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-2xl shadow border border-amber-200 p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="h-12 w-12 rounded-xl bg-amber-100 flex items-center justify-center">
                      <span className="text-2xl">🩺</span>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-amber-900">Set Your Medical Specialty</h3>
                      <p className="text-sm text-amber-700">Personalize your dashboard based on your specialty for better workflow.</p>
                    </div>
                  </div>
                  <a
                    href="/settings"
                    className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors font-medium text-sm"
                  >
                    Set Specialty →
                  </a>
                </div>
              </div>
            )}

            {/* Daily Healthy Overview Header */}
            <div className="bg-white rounded-2xl shadow border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Daily healthy overview</h1>
                  <p className="text-sm text-gray-600 mt-1">
                    {formattedDate} • {formattedTime}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  {/* Change Log - shows adaptation history */}
                  <ChangeLogDrawer />
                  
                  {(user.role === 'clinician' || user.role === 'admin') && (
                    <a
                      href="/patients/new"
                      className="inline-flex items-center px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-sm font-semibold rounded-xl hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 shadow hover:shadow-md transition-all transform hover:scale-105 active:scale-95"
                    >
                      <svg
                        className="w-5 h-5 mr-2"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 4v16m8-8H4"
                        />
                      </svg>
                      New Patient
                    </a>
                  )}
                </div>
              </div>
            </div>

            {/* Self-Adaptive Dashboard - All features available, ordered by usage */}
            {user.role === 'clinician' && (
              <AdaptiveDashboard
                sections={[
                  // Quick Actions - adapts based on specialty and usage
                  {
                    id: 'quick_actions',
                    label: 'Quick Actions',
                    component: user.specialty ? (
                      <SpecialtyQuickActions specialty={user.specialty} />
                    ) : (
                      <div className="bg-white rounded-2xl shadow border border-gray-200 p-6">
                        <p className="text-gray-500">Select a specialty to see quick actions</p>
                      </div>
                    ),
                    defaultVisible: true,
                    defaultPriority: 8,
                  },
                  // Incoming Referrals - Patients referred by nurses
                  {
                    id: 'incoming_referrals',
                    label: 'Incoming Referrals',
                    component: <IncomingReferrals specialty={user.specialty || undefined} />,
                    defaultVisible: true,
                    defaultPriority: 9,
                  },
                  // All specialty widgets - available but shown/hidden based on usage
                  ...getAllAvailableWidgets(user.specialty || undefined).map(widget => ({
                    id: widget.id,
                    label: widget.label,
                    component: widget.component,
                    defaultVisible: (widget.specialtyRelevance[user.specialty || 'general'] || 0) >= 5,
                    defaultPriority: widget.specialtyRelevance[user.specialty || 'general'] || 5,
                  })),
                  // Health Metrics - adapts based on usage
                  {
                    id: 'health_metrics',
                    label: 'Health Metrics',
                    component: (
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div 
                          className="bg-white rounded-2xl shadow border border-gray-200 p-6 cursor-pointer hover:shadow-md transition-shadow"
                          onClick={() => monitorService.logDashboardAction({ actionType: 'feature_access', featureId: 'total_patients' })}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm text-gray-600 mb-1">Total Patients</p>
                              <p className="text-3xl font-bold text-gray-900">{totalPatients}</p>
                            </div>
                            <div className="h-12 w-12 rounded-lg bg-blue-100 flex items-center justify-center">
                              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                              </svg>
                            </div>
                          </div>
                        </div>
                        <div 
                          className="bg-white rounded-2xl shadow border border-gray-200 p-6 cursor-pointer hover:shadow-md transition-shadow"
                          onClick={() => monitorService.logDashboardAction({ actionType: 'feature_access', featureId: 'appointments' })}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm text-gray-600 mb-1">Today's Appointments</p>
                              <p className="text-3xl font-bold text-gray-900">{todayPatients.length}</p>
                            </div>
                            <div className="h-12 w-12 rounded-lg bg-indigo-100 flex items-center justify-center">
                              <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                              </svg>
                            </div>
                          </div>
                        </div>
                        <div 
                          className="bg-white rounded-2xl shadow border border-gray-200 p-6 cursor-pointer hover:shadow-md transition-shadow"
                          onClick={() => monitorService.logDashboardAction({ actionType: 'feature_access', featureId: 'active_sessions' })}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm text-gray-600 mb-1">Active Sessions</p>
                              <p className="text-3xl font-bold text-gray-900">1</p>
                            </div>
                            <div className="h-12 w-12 rounded-lg bg-green-100 flex items-center justify-center">
                              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                            </div>
                          </div>
                        </div>
                      </div>
                    ),
                    defaultVisible: true,
                    defaultPriority: 6,
                  },
                  // Patient List - always visible but order adapts
                  {
                    id: 'patient_list',
                    label: 'Patient Management',
                    component: (
                      <div className="bg-white rounded-2xl shadow border border-gray-200 p-6">
                        <div className="flex items-center justify-between mb-6">
                          <div>
                            <h2 className="text-xl font-bold text-gray-900">Patient Management</h2>
                            <p className="text-sm text-gray-600 mt-1">View and manage all patients</p>
                          </div>
                        </div>
                        <PatientCardGrid />
                      </div>
                    ),
                    defaultVisible: true,
                    defaultPriority: 7,
                  },
                ]}
                onFeatureClick={(featureId) => {
                  // Plan will refresh automatically after interaction
                  console.log(`Feature clicked: ${featureId}`);
                }}
              />
            )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
