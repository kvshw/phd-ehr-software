/**
 * Specialty-based Quick Actions Component
 * Shows relevant quick actions based on the doctor's specialty
 * Tracks usage for MAPE-K self-adaptation
 */
'use client';

import React from 'react';
import { monitorService } from '@/lib/monitorService';

// Quick actions by specialty
const SPECIALTY_ACTIONS: Record<string, Array<{
  id: string;
  label: string;
  icon: string;
  href: string;
  description: string;
  color: string;
}>> = {
  cardiology: [
    { id: 'ecg', label: 'ECG Review', icon: '📈', href: '#', description: 'Review recent ECGs', color: 'rose' },
    { id: 'bp', label: 'BP Trends', icon: '🩸', href: '#', description: 'Blood pressure monitoring', color: 'red' },
    { id: 'echo', label: 'Echo Results', icon: '🫀', href: '#', description: 'Echocardiogram reports', color: 'pink' },
    { id: 'risk', label: 'CV Risk Calc', icon: '⚠️', href: '#', description: 'Calculate cardiovascular risk', color: 'amber' },
  ],
  neurology: [
    { id: 'neuro', label: 'Neuro Exam', icon: '🧠', href: '#', description: 'Neurological examination', color: 'purple' },
    { id: 'mri', label: 'MRI Review', icon: '📷', href: '#', description: 'Brain imaging results', color: 'violet' },
    { id: 'cognitive', label: 'Cognitive Test', icon: '📝', href: '#', description: 'MMSE / MoCA scoring', color: 'indigo' },
    { id: 'headache', label: 'Headache Diary', icon: '🤕', href: '#', description: 'Track headache patterns', color: 'fuchsia' },
  ],
  psychiatry: [
    { id: 'mse', label: 'Mental Status', icon: '🧘', href: '#', description: 'Mental status examination', color: 'teal' },
    { id: 'phq9', label: 'PHQ-9 Score', icon: '📋', href: '#', description: 'Depression screening', color: 'emerald' },
    { id: 'gad7', label: 'GAD-7 Score', icon: '😰', href: '#', description: 'Anxiety screening', color: 'cyan' },
    { id: 'meds', label: 'Psych Meds', icon: '💊', href: '#', description: 'Medication management', color: 'green' },
  ],
  pediatrics: [
    { id: 'growth', label: 'Growth Chart', icon: '📊', href: '#', description: 'Height/weight percentiles', color: 'sky' },
    { id: 'vaccines', label: 'Vaccines', icon: '💉', href: '#', description: 'Immunization schedule', color: 'blue' },
    { id: 'develop', label: 'Development', icon: '👶', href: '#', description: 'Developmental milestones', color: 'cyan' },
    { id: 'feeding', label: 'Nutrition', icon: '🍼', href: '#', description: 'Feeding and nutrition', color: 'lime' },
  ],
  geriatrics: [
    { id: 'falls', label: 'Fall Risk', icon: '⚠️', href: '#', description: 'Fall risk assessment', color: 'amber' },
    { id: 'polypharm', label: 'Medications', icon: '💊', href: '#', description: 'Polypharmacy review', color: 'orange' },
    { id: 'adl', label: 'ADL Status', icon: '🏠', href: '#', description: 'Activities of daily living', color: 'yellow' },
    { id: 'cognitive', label: 'Cognition', icon: '🧠', href: '#', description: 'Cognitive screening', color: 'lime' },
  ],
  oncology: [
    { id: 'staging', label: 'Staging', icon: '📋', href: '#', description: 'Tumor staging review', color: 'fuchsia' },
    { id: 'chemo', label: 'Chemo Cycles', icon: '💉', href: '#', description: 'Treatment schedule', color: 'pink' },
    { id: 'labs', label: 'Tumor Markers', icon: '🧪', href: '#', description: 'Lab results tracking', color: 'purple' },
    { id: 'pain', label: 'Pain Mgmt', icon: '😣', href: '#', description: 'Pain assessment', color: 'rose' },
  ],
  emergency: [
    { id: 'triage', label: 'Triage', icon: '🚨', href: '#', description: 'Patient triage', color: 'red' },
    { id: 'trauma', label: 'Trauma', icon: '🩹', href: '#', description: 'Trauma assessment', color: 'orange' },
    { id: 'resus', label: 'Resus Calc', icon: '💓', href: '#', description: 'Resuscitation tools', color: 'rose' },
    { id: 'poison', label: 'Toxicology', icon: '☠️', href: '#', description: 'Poison control info', color: 'amber' },
  ],
  nursing: [
    { id: 'vitals', label: 'Vital Signs', icon: '📊', href: '#', description: 'Record vital signs', color: 'pink' },
    { id: 'meds', label: 'Med Admin', icon: '💊', href: '#', description: 'Medication administration', color: 'rose' },
    { id: 'wounds', label: 'Wound Care', icon: '🩹', href: '#', description: 'Wound documentation', color: 'red' },
    { id: 'education', label: 'Education', icon: '📚', href: '#', description: 'Patient education', color: 'blue' },
  ],
  internal: [
    { id: 'history', label: 'Full History', icon: '📋', href: '#', description: 'Comprehensive history', color: 'red' },
    { id: 'labs', label: 'Lab Review', icon: '🧪', href: '#', description: 'Laboratory results', color: 'orange' },
    { id: 'imaging', label: 'Imaging', icon: '📷', href: '#', description: 'Diagnostic imaging', color: 'amber' },
    { id: 'consult', label: 'Consults', icon: '👨‍⚕️', href: '#', description: 'Specialist referrals', color: 'yellow' },
  ],
  general: [
    { id: 'checkup', label: 'Annual Checkup', icon: '✅', href: '#', description: 'Preventive care', color: 'blue' },
    { id: 'vitals', label: 'Vitals', icon: '📊', href: '#', description: 'Check vital signs', color: 'green' },
    { id: 'labs', label: 'Order Labs', icon: '🧪', href: '#', description: 'Laboratory orders', color: 'purple' },
    { id: 'referral', label: 'Refer', icon: '📤', href: '#', description: 'Specialist referral', color: 'indigo' },
  ],
};

// Default actions for specialties not in the list
const DEFAULT_ACTIONS = SPECIALTY_ACTIONS.general;

interface SpecialtyQuickActionsProps {
  specialty: string;
}

export function SpecialtyQuickActions({ specialty }: SpecialtyQuickActionsProps) {
  const actions = SPECIALTY_ACTIONS[specialty] || DEFAULT_ACTIONS;
  
  return (
    <div className="bg-white rounded-2xl shadow border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
          <p className="text-sm text-gray-500">Common tasks for your specialty</p>
        </div>
        <span className="px-2.5 py-1 text-xs font-medium bg-indigo-100 text-indigo-800 rounded-full capitalize">
          {specialty} Mode
        </span>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {actions.map((action) => (
          <button
            key={action.id}
            onClick={() => {
              // Track usage for self-adaptation
              monitorService.logDashboardAction({
                actionType: 'quick_action_click',
                featureId: action.id,
                metadata: {
                  specialty,
                  action_label: action.label,
                },
              });
              // Navigate or perform action (can be customized)
              if (action.href && action.href !== '#') {
                window.location.href = action.href;
              }
            }}
            className={`p-4 rounded-xl border-2 border-gray-100 bg-gradient-to-br from-gray-50 to-white hover:border-${action.color}-300 hover:shadow-md transition-all text-left group cursor-pointer`}
          >
            <div className={`text-2xl mb-2 group-hover:scale-110 transition-transform`}>
              {action.icon}
            </div>
            <div className="font-medium text-gray-900 text-sm mb-0.5">
              {action.label}
            </div>
            <div className="text-xs text-gray-500">
              {action.description}
            </div>
          </button>
        ))}
      </div>
      
      {/* MAPE-K Adaptation Note */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <p className="text-xs text-gray-400 flex items-center gap-1">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          UI adapted for {specialty} specialty via MAPE-K engine
        </p>
      </div>
    </div>
  );
}

