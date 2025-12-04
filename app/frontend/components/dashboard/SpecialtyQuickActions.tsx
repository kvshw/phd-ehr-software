/**
 * Specialty-based Quick Actions Component
 * Shows relevant quick actions based on the doctor's specialty
 * Tracks usage for MAPE-K self-adaptation
 */
'use client';

import React from 'react';
import { monitorService } from '@/lib/monitorService';

// Quick actions by specialty - using abbreviations instead of emojis
const SPECIALTY_ACTIONS: Record<string, Array<{
  id: string;
  label: string;
  abbrev: string;
  href: string;
  description: string;
  color: string;
}>> = {
  cardiology: [
    { id: 'ecg', label: 'ECG Review', abbrev: 'ECG', href: '#', description: 'Review recent ECGs', color: 'rose' },
    { id: 'bp', label: 'BP Trends', abbrev: 'BP', href: '#', description: 'Blood pressure monitoring', color: 'red' },
    { id: 'echo', label: 'Echo Results', abbrev: 'ECHO', href: '#', description: 'Echocardiogram reports', color: 'pink' },
    { id: 'risk', label: 'CV Risk Calc', abbrev: 'CVR', href: '#', description: 'Calculate cardiovascular risk', color: 'amber' },
  ],
  neurology: [
    { id: 'neuro', label: 'Neuro Exam', abbrev: 'NEX', href: '#', description: 'Neurological examination', color: 'purple' },
    { id: 'mri', label: 'MRI Review', abbrev: 'MRI', href: '#', description: 'Brain imaging results', color: 'violet' },
    { id: 'cognitive', label: 'Cognitive Test', abbrev: 'COG', href: '#', description: 'MMSE / MoCA scoring', color: 'indigo' },
    { id: 'headache', label: 'Headache Diary', abbrev: 'HA', href: '#', description: 'Track headache patterns', color: 'fuchsia' },
  ],
  psychiatry: [
    { id: 'mse', label: 'Mental Status', abbrev: 'MSE', href: '#', description: 'Mental status examination', color: 'teal' },
    { id: 'phq9', label: 'PHQ-9 Score', abbrev: 'PHQ', href: '#', description: 'Depression screening', color: 'emerald' },
    { id: 'gad7', label: 'GAD-7 Score', abbrev: 'GAD', href: '#', description: 'Anxiety screening', color: 'cyan' },
    { id: 'meds', label: 'Psych Meds', abbrev: 'RX', href: '#', description: 'Medication management', color: 'green' },
  ],
  pediatrics: [
    { id: 'growth', label: 'Growth Chart', abbrev: 'GRW', href: '#', description: 'Height/weight percentiles', color: 'sky' },
    { id: 'vaccines', label: 'Vaccines', abbrev: 'VAX', href: '#', description: 'Immunization schedule', color: 'blue' },
    { id: 'develop', label: 'Development', abbrev: 'DEV', href: '#', description: 'Developmental milestones', color: 'cyan' },
    { id: 'feeding', label: 'Nutrition', abbrev: 'NUT', href: '#', description: 'Feeding and nutrition', color: 'lime' },
  ],
  geriatrics: [
    { id: 'falls', label: 'Fall Risk', abbrev: 'FRA', href: '#', description: 'Fall risk assessment', color: 'amber' },
    { id: 'polypharm', label: 'Medications', abbrev: 'PPR', href: '#', description: 'Polypharmacy review', color: 'orange' },
    { id: 'adl', label: 'ADL Status', abbrev: 'ADL', href: '#', description: 'Activities of daily living', color: 'yellow' },
    { id: 'cognitive', label: 'Cognition', abbrev: 'COG', href: '#', description: 'Cognitive screening', color: 'lime' },
  ],
  oncology: [
    { id: 'staging', label: 'Staging', abbrev: 'STG', href: '#', description: 'Tumor staging review', color: 'fuchsia' },
    { id: 'chemo', label: 'Chemo Cycles', abbrev: 'CHM', href: '#', description: 'Treatment schedule', color: 'pink' },
    { id: 'labs', label: 'Tumor Markers', abbrev: 'TMK', href: '#', description: 'Lab results tracking', color: 'purple' },
    { id: 'pain', label: 'Pain Mgmt', abbrev: 'PAN', href: '#', description: 'Pain assessment', color: 'rose' },
  ],
  emergency: [
    { id: 'triage', label: 'Triage', abbrev: 'TRI', href: '#', description: 'Patient triage', color: 'red' },
    { id: 'trauma', label: 'Trauma', abbrev: 'TRM', href: '#', description: 'Trauma assessment', color: 'orange' },
    { id: 'resus', label: 'Resus Calc', abbrev: 'RES', href: '#', description: 'Resuscitation tools', color: 'rose' },
    { id: 'poison', label: 'Toxicology', abbrev: 'TOX', href: '#', description: 'Poison control info', color: 'amber' },
  ],
  nursing: [
    { id: 'vitals', label: 'Vital Signs', abbrev: 'VS', href: '#', description: 'Record vital signs', color: 'pink' },
    { id: 'meds', label: 'Med Admin', abbrev: 'MAR', href: '#', description: 'Medication administration', color: 'rose' },
    { id: 'wounds', label: 'Wound Care', abbrev: 'WND', href: '#', description: 'Wound documentation', color: 'red' },
    { id: 'education', label: 'Education', abbrev: 'EDU', href: '#', description: 'Patient education', color: 'blue' },
  ],
  internal: [
    { id: 'history', label: 'Full History', abbrev: 'H&P', href: '#', description: 'Comprehensive history', color: 'red' },
    { id: 'labs', label: 'Lab Review', abbrev: 'LAB', href: '#', description: 'Laboratory results', color: 'orange' },
    { id: 'imaging', label: 'Imaging', abbrev: 'IMG', href: '#', description: 'Diagnostic imaging', color: 'amber' },
    { id: 'consult', label: 'Consults', abbrev: 'CON', href: '#', description: 'Specialist referrals', color: 'yellow' },
  ],
  general: [
    { id: 'checkup', label: 'Annual Checkup', abbrev: 'AWV', href: '#', description: 'Preventive care', color: 'blue' },
    { id: 'vitals', label: 'Vitals', abbrev: 'VS', href: '#', description: 'Check vital signs', color: 'green' },
    { id: 'labs', label: 'Order Labs', abbrev: 'LAB', href: '#', description: 'Laboratory orders', color: 'purple' },
    { id: 'referral', label: 'Refer', abbrev: 'REF', href: '#', description: 'Specialist referral', color: 'indigo' },
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
            <div className={`text-sm font-bold mb-2 group-hover:scale-110 transition-transform text-${action.color}-600 bg-${action.color}-100 w-10 h-10 rounded-lg flex items-center justify-center`}>
              {action.abbrev}
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

