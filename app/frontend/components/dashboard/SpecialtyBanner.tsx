/**
 * Specialty Banner Component
 * Displays a personalized banner based on the doctor's specialty
 */
'use client';

import React from 'react';

// Specialty configurations with Finnish translations
const SPECIALTY_CONFIG: Record<string, {
  name: string;
  namefi: string;
  icon: string;
  color: string;
  bgGradient: string;
  greeting: string;
  focusAreas: string[];
}> = {
  general: {
    name: 'General Practice',
    namefi: 'Yleislääketiede',
    icon: '🏥',
    color: 'blue',
    bgGradient: 'from-blue-50 to-cyan-50',
    greeting: 'Your patients are waiting',
    focusAreas: ['Preventive Care', 'Chronic Disease Management', 'Primary Assessment'],
  },
  internal: {
    name: 'Internal Medicine',
    namefi: 'Sisätaudit',
    icon: '🫀',
    color: 'red',
    bgGradient: 'from-red-50 to-orange-50',
    greeting: 'Complex cases ahead',
    focusAreas: ['Multi-organ Assessment', 'Diagnostic Workup', 'Treatment Planning'],
  },
  cardiology: {
    name: 'Cardiology',
    namefi: 'Kardiologia',
    icon: '❤️',
    color: 'rose',
    bgGradient: 'from-rose-50 to-pink-50',
    greeting: 'Cardiovascular health focus',
    focusAreas: ['ECG Review', 'Heart Failure', 'Arrhythmia Management', 'Risk Stratification'],
  },
  neurology: {
    name: 'Neurology',
    namefi: 'Neurologia',
    icon: '🧠',
    color: 'purple',
    bgGradient: 'from-purple-50 to-violet-50',
    greeting: 'Neurological assessments',
    focusAreas: ['Cognitive Assessment', 'Stroke Care', 'Movement Disorders', 'Headache Management'],
  },
  psychiatry: {
    name: 'Psychiatry',
    namefi: 'Psykiatria',
    icon: '🧘',
    color: 'teal',
    bgGradient: 'from-teal-50 to-emerald-50',
    greeting: 'Mental health focus',
    focusAreas: ['Mental Status Exam', 'Medication Management', 'Crisis Assessment'],
  },
  pediatrics: {
    name: 'Pediatrics',
    namefi: 'Lastentaudit',
    icon: '👶',
    color: 'sky',
    bgGradient: 'from-sky-50 to-blue-50',
    greeting: 'Young patients need you',
    focusAreas: ['Growth Monitoring', 'Immunizations', 'Developmental Assessment'],
  },
  geriatrics: {
    name: 'Geriatrics',
    namefi: 'Geriatria',
    icon: '👴',
    color: 'amber',
    bgGradient: 'from-amber-50 to-yellow-50',
    greeting: 'Senior care excellence',
    focusAreas: ['Polypharmacy Review', 'Fall Prevention', 'Cognitive Health', 'Palliative Care'],
  },
  surgery: {
    name: 'Surgery',
    namefi: 'Kirurgia',
    icon: '🔪',
    color: 'slate',
    bgGradient: 'from-slate-50 to-gray-50',
    greeting: 'Surgical precision',
    focusAreas: ['Pre-op Assessment', 'Wound Care', 'Post-op Follow-up'],
  },
  orthopedics: {
    name: 'Orthopedics',
    namefi: 'Ortopedia',
    icon: '🦴',
    color: 'zinc',
    bgGradient: 'from-zinc-50 to-stone-50',
    greeting: 'Musculoskeletal care',
    focusAreas: ['Joint Assessment', 'Fracture Care', 'Rehabilitation Planning'],
  },
  oncology: {
    name: 'Oncology',
    namefi: 'Onkologia',
    icon: '🎗️',
    color: 'fuchsia',
    bgGradient: 'from-fuchsia-50 to-pink-50',
    greeting: 'Cancer care focus',
    focusAreas: ['Tumor Staging', 'Treatment Response', 'Supportive Care', 'Follow-up'],
  },
  pulmonology: {
    name: 'Pulmonology',
    namefi: 'Keuhkosairaudet',
    icon: '🫁',
    color: 'cyan',
    bgGradient: 'from-cyan-50 to-sky-50',
    greeting: 'Respiratory health',
    focusAreas: ['Spirometry Review', 'COPD Management', 'Asthma Control', 'Sleep Apnea'],
  },
  endocrinology: {
    name: 'Endocrinology',
    namefi: 'Endokrinologia',
    icon: '⚗️',
    color: 'lime',
    bgGradient: 'from-lime-50 to-green-50',
    greeting: 'Metabolic balance',
    focusAreas: ['Diabetes Management', 'Thyroid Disorders', 'Hormone Therapy'],
  },
  emergency: {
    name: 'Emergency Medicine',
    namefi: 'Ensihoito',
    icon: '🚑',
    color: 'red',
    bgGradient: 'from-red-50 to-rose-50',
    greeting: 'Critical care ready',
    focusAreas: ['Triage', 'Acute Stabilization', 'Rapid Assessment', 'Trauma Care'],
  },
  nursing: {
    name: 'Nursing',
    namefi: 'Hoitotyö',
    icon: '👩‍⚕️',
    color: 'pink',
    bgGradient: 'from-pink-50 to-rose-50',
    greeting: 'Patient care excellence',
    focusAreas: ['Vital Monitoring', 'Patient Education', 'Care Coordination', 'Documentation'],
  },
};

interface SpecialtyBannerProps {
  specialty: string;
  userName?: string;
}

export function SpecialtyBanner({ specialty, userName }: SpecialtyBannerProps) {
  const config = SPECIALTY_CONFIG[specialty] || SPECIALTY_CONFIG.general;
  const currentHour = new Date().getHours();
  const timeGreeting = currentHour < 12 ? 'Good morning' : currentHour < 17 ? 'Good afternoon' : 'Good evening';
  
  return (
    <div className={`bg-gradient-to-r ${config.bgGradient} rounded-2xl shadow border border-${config.color}-200 p-6`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4">
          <div className={`h-14 w-14 rounded-xl bg-${config.color}-100 flex items-center justify-center text-3xl shadow-sm`}>
            {config.icon}
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h2 className={`text-xl font-bold text-${config.color}-900`}>
                {timeGreeting}, {userName || 'Doctor'}
              </h2>
              <span className={`px-2 py-0.5 text-xs font-medium bg-${config.color}-100 text-${config.color}-800 rounded-full`}>
                {config.name}
              </span>
            </div>
            <p className={`text-sm text-${config.color}-700 mb-3`}>{config.greeting}</p>
            
            {/* Focus Areas */}
            <div className="flex flex-wrap gap-2">
              {config.focusAreas.map((area, index) => (
                <span
                  key={index}
                  className={`px-2.5 py-1 text-xs font-medium bg-white/70 text-${config.color}-800 rounded-lg border border-${config.color}-200`}
                >
                  {area}
                </span>
              ))}
            </div>
          </div>
        </div>
        
        <a
          href="/settings"
          className={`text-sm text-${config.color}-600 hover:text-${config.color}-800 font-medium flex items-center gap-1`}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Change
        </a>
      </div>
    </div>
  );
}

