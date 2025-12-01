/**
 * Specialty-Specific Dashboard Widgets
 * Different widgets shown based on medical specialty
 * All widgets are available - shown/hidden/reordered by MAPE-K based on usage
 */
'use client';

import React from 'react';
import { monitorService } from '@/lib/monitorService';

// Cardiology-specific widgets
export function CardiologyWidgets() {
  return (
    <>
      {/* ECG Review Widget - Top Priority for Cardiology */}
      <div className="bg-white rounded-2xl shadow border border-rose-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-rose-100 flex items-center justify-center">
              <span className="text-xl">📈</span>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">ECG Review</h3>
              <p className="text-sm text-gray-500">Recent electrocardiograms</p>
            </div>
          </div>
          <span className="px-2 py-1 text-xs font-medium bg-rose-100 text-rose-800 rounded-full">
            Priority
          </span>
        </div>
        <div className="space-y-2">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <p className="text-sm font-medium text-gray-900">Patient 6c0f319d</p>
              <p className="text-xs text-gray-500">ECG from 11/24/2025</p>
            </div>
            <button 
              onClick={() => monitorService.logDashboardAction({
                actionType: 'feature_access',
                featureId: 'ecg_review',
                metadata: { patient_id: '6c0f319d' },
              })}
              className="px-3 py-1.5 bg-rose-600 text-white text-sm rounded-lg hover:bg-rose-700"
            >
              Review
            </button>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <p className="text-sm font-medium text-gray-900">Patient 13fd6e6c</p>
              <p className="text-xs text-gray-500">ECG from 11/23/2025</p>
            </div>
            <button 
              onClick={() => monitorService.logDashboardAction({
                actionType: 'feature_access',
                featureId: 'ecg_review',
                metadata: { patient_id: '13fd6e6c' },
              })}
              className="px-3 py-1.5 bg-rose-600 text-white text-sm rounded-lg hover:bg-rose-700"
            >
              Review
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

// Neurology-specific widgets
export function NeurologyWidgets() {
  return (
    <>
      {/* Neuro Exam Widget */}
      <div className="bg-white rounded-2xl shadow border border-purple-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center">
              <span className="text-xl">🧠</span>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Neurological Exam</h3>
              <p className="text-sm text-gray-500">Quick assessment tools</p>
            </div>
          </div>
          <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded-full">
            Priority
          </span>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <button 
            onClick={() => monitorService.logDashboardAction({
              actionType: 'quick_action_click',
              featureId: 'mmse',
            })}
            className="p-3 bg-purple-50 rounded-lg text-left hover:bg-purple-100 transition-colors cursor-pointer"
          >
            <p className="text-sm font-medium text-gray-900">MMSE</p>
            <p className="text-xs text-gray-500">Cognitive screening</p>
          </button>
          <button 
            onClick={() => monitorService.logDashboardAction({
              actionType: 'quick_action_click',
              featureId: 'moca',
            })}
            className="p-3 bg-purple-50 rounded-lg text-left hover:bg-purple-100 transition-colors cursor-pointer"
          >
            <p className="text-sm font-medium text-gray-900">MoCA</p>
            <p className="text-xs text-gray-500">Cognitive assessment</p>
          </button>
        </div>
      </div>

      {/* Imaging Review Widget */}
      <div className="bg-white rounded-2xl shadow border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Imaging</h3>
        <div className="space-y-2">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <p className="text-sm font-medium text-gray-900">MRI Brain</p>
              <p className="text-xs text-gray-500">Patient 6c0f319d • 11/24/2025</p>
            </div>
            <button 
              onClick={() => monitorService.logDashboardAction({
                actionType: 'feature_access',
                featureId: 'mri_review',
                metadata: { patient_id: '6c0f319d', imaging_type: 'mri_brain' },
              })}
              className="px-3 py-1.5 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700"
            >
              View
            </button>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <p className="text-sm font-medium text-gray-900">CT Head</p>
              <p className="text-xs text-gray-500">Patient 13fd6e6c • 11/23/2025</p>
            </div>
            <button 
              onClick={() => monitorService.logDashboardAction({
                actionType: 'feature_access',
                featureId: 'ct_review',
                metadata: { patient_id: '13fd6e6c', imaging_type: 'ct_head' },
              })}
              className="px-3 py-1.5 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700"
            >
              View
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

// Emergency-specific widgets
export function EmergencyWidgets() {
  return (
    <>
      {/* Triage Widget */}
      <div className="bg-white rounded-2xl shadow border border-red-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-red-100 flex items-center justify-center">
              <span className="text-xl">🚨</span>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Active Triage</h3>
              <p className="text-sm text-gray-500">Patients awaiting assessment</p>
            </div>
          </div>
          <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">
            Critical
          </span>
        </div>
        <div className="space-y-2">
          <div className="p-3 bg-red-50 border-l-4 border-red-500 rounded">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">Chest Pain</p>
                <p className="text-xs text-gray-500">Room 3 • 5 min ago</p>
              </div>
              <span className="px-2 py-1 text-xs font-bold bg-red-600 text-white rounded">
                P1
              </span>
            </div>
          </div>
          <div className="p-3 bg-orange-50 border-l-4 border-orange-500 rounded">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">Head Injury</p>
                <p className="text-xs text-gray-500">Room 5 • 8 min ago</p>
              </div>
              <span className="px-2 py-1 text-xs font-bold bg-orange-600 text-white rounded">
                P2
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Rapid Assessment Tools */}
      <div className="bg-white rounded-2xl shadow border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Rapid Assessment</h3>
        <div className="grid grid-cols-2 gap-3">
          <button className="p-3 bg-red-50 rounded-lg text-left hover:bg-red-100 transition-colors">
            <p className="text-sm font-medium text-gray-900">GCS Score</p>
            <p className="text-xs text-gray-500">Glasgow Coma Scale</p>
          </button>
          <button className="p-3 bg-orange-50 rounded-lg text-left hover:bg-orange-100 transition-colors">
            <p className="text-sm font-medium text-gray-900">Resus Calc</p>
            <p className="text-xs text-gray-500">Resuscitation tools</p>
          </button>
        </div>
      </div>
    </>
  );
}

// General/Default widgets (for specialties without specific widgets)
export function GeneralWidgets() {
  return (
    <>
      {/* No default widgets - patient vitals/labs should be in patient files */}
    </>
  );
}

/**
 * Get ALL available widgets (not specialty-filtered)
 * MAPE-K will show/hide/reorder based on actual usage
 */
export function getAllAvailableWidgets(specialty: string | null | undefined): Array<{
  id: string;
  label: string;
  component: React.ReactNode;
  specialtyRelevance: Record<string, number>; // Specialty -> relevance (0-10)
}> {
  return [
    {
      id: 'ecg_review',
      label: 'ECG Review',
      component: <CardiologyWidgets />,
      specialtyRelevance: {
        cardiology: 10,
        emergency: 8,
        internal: 6,
        general: 4,
        neurology: 2,
        psychiatry: 1,
      },
    },
    {
      id: 'neuro_exam',
      label: 'Neurological Exam',
      component: <NeurologyWidgets />,
      specialtyRelevance: {
        neurology: 10,
        emergency: 7,
        general: 3,
        cardiology: 1,
      },
    },
    {
      id: 'triage',
      label: 'Triage & Rapid Assessment',
      component: <EmergencyWidgets />,
      specialtyRelevance: {
        emergency: 10,
        general: 4,
        internal: 3,
      },
    },
  ];
}

/**
 * Get specialty-specific widgets (legacy - for initial display)
 * @deprecated Use getAllAvailableWidgets with MAPE-K adaptation instead
 */
export function getSpecialtyWidgets(specialty: string | null | undefined): React.ReactNode {
  switch (specialty) {
    case 'cardiology':
      return <CardiologyWidgets />;
    case 'neurology':
      return <NeurologyWidgets />;
    case 'emergency':
      return <EmergencyWidgets />;
    default:
      return <GeneralWidgets />;
  }
}

