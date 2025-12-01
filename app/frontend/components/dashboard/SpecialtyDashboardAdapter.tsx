/**
 * Specialty-Based Dashboard Adapter
 * Reorders and prioritizes dashboard sections based on medical specialty
 * 
 * Based on real EHR usage patterns:
 * - Cardiology: ECG, vitals, cardiac labs first
 * - Neurology: Neuro exam, imaging, cognitive tests first
 * - Emergency: Triage, vitals, rapid assessment first
 * - etc.
 */
'use client';

import React from 'react';

// Specialty-specific dashboard configurations
// Defines what sections to show, in what order, and their priority
export interface DashboardSection {
  id: string;
  label: string;
  component: React.ReactNode;
  priority: number; // 1-10, higher = more important
  specialtyRelevance: Record<string, number>; // Specialty -> relevance score (0-10)
  defaultVisible: boolean;
}

// Specialty-specific section priorities
// Based on real EHR usage patterns for each specialty
const SPECIALTY_PRIORITIES: Record<string, Record<string, number>> = {
  cardiology: {
    // Cardiology doctors use these most:
    'vitals': 10,        // BP, HR monitoring critical
    'ecg': 10,           // ECG review is primary tool
    'cardiac_labs': 9,   // Troponin, BNP, lipids
    'medications': 8,    // Anticoagulants, beta blockers
    'imaging': 7,        // Echo, stress tests
    'appointments': 6,   // Follow-ups important
    'patient_list': 5,   // Standard
    'health_metrics': 4, // Less critical
    'quick_actions': 8,  // CV risk calc, etc.
  },
  neurology: {
    // Neurologists use these most:
    'neuro_exam': 10,    // Neurological examination tools
    'imaging': 10,       // MRI, CT scans critical
    'cognitive_tests': 9, // MMSE, MoCA
    'medications': 8,    // Antiepileptics, etc.
    'appointments': 7,   // Follow-ups for chronic conditions
    'patient_list': 6,
    'vitals': 5,         // Less critical than neuro-specific
    'health_metrics': 4,
    'quick_actions': 8,  // Headache diary, etc.
  },
  emergency: {
    // Emergency doctors need rapid access:
    'triage': 10,        // Triage tools first
    'vitals': 10,        // Critical vitals monitoring
    'rapid_assessment': 9, // Quick assessment tools
    'medications': 7,    // Emergency meds
    'imaging': 8,        // Quick imaging review
    'patient_list': 6,   // Active patients
    'appointments': 3,   // Less relevant in ER
    'health_metrics': 2,
    'quick_actions': 9,  // Resuscitation calc, etc.
  },
  psychiatry: {
    // Psychiatrists focus on:
    'mental_status': 10, // MSE tools
    'screening_tools': 9, // PHQ-9, GAD-7
    'medications': 9,    // Psych meds critical
    'appointments': 8,   // Regular follow-ups
    'patient_list': 7,
    'vitals': 4,         // Less critical
    'imaging': 2,        // Rarely used
    'health_metrics': 3,
    'quick_actions': 8,
  },
  pediatrics: {
    // Pediatricians need:
    'growth_charts': 10, // Growth monitoring
    'immunizations': 9,  // Vaccine schedules
    'development': 9,    // Milestone tracking
    'vitals': 7,         // Age-adjusted vitals
    'appointments': 8,   // Well-child visits
    'patient_list': 6,
    'medications': 5,
    'health_metrics': 4,
    'quick_actions': 7,
  },
  geriatrics: {
    // Geriatricians focus on:
    'polypharmacy': 10,  // Medication review
    'fall_risk': 9,      // Fall prevention
    'cognitive': 9,      // Cognitive screening
    'adl': 8,           // Activities of daily living
    'appointments': 7,
    'patient_list': 6,
    'vitals': 5,
    'health_metrics': 4,
    'quick_actions': 7,
  },
  internal: {
    // Internal medicine - balanced view:
    'comprehensive_history': 9,
    'labs': 9,           // Lab review important
    'imaging': 8,
    'medications': 7,
    'appointments': 7,
    'patient_list': 6,
    'vitals': 6,
    'health_metrics': 5,
    'quick_actions': 6,
  },
  general: {
    // General practice - balanced:
    'preventive_care': 8,
    'vitals': 7,
    'labs': 7,
    'appointments': 8,
    'patient_list': 7,
    'medications': 6,
    'health_metrics': 5,
    'quick_actions': 6,
  },
  // Add more specialties as needed
};

// Default priorities for specialties not explicitly defined
const DEFAULT_PRIORITIES: Record<string, number> = {
  'appointments': 7,
  'patient_list': 6,
  'vitals': 6,
  'medications': 6,
  'health_metrics': 5,
  'quick_actions': 6,
};

/**
 * Get section priority for a given specialty
 */
export function getSectionPriority(sectionId: string, specialty: string | null | undefined): number {
  if (!specialty) {
    return DEFAULT_PRIORITIES[sectionId] || 5;
  }
  
  const specialtyConfig = SPECIALTY_PRIORITIES[specialty];
  if (!specialtyConfig) {
    return DEFAULT_PRIORITIES[sectionId] || 5;
  }
  
  return specialtyConfig[sectionId] || DEFAULT_PRIORITIES[sectionId] || 5;
}

/**
 * Sort sections by specialty priority
 */
export function sortSectionsBySpecialty(
  sections: DashboardSection[],
  specialty: string | null | undefined
): DashboardSection[] {
  return [...sections].sort((a, b) => {
    const priorityA = getSectionPriority(a.id, specialty);
    const priorityB = getSectionPriority(b.id, specialty);
    
    // Higher priority first
    if (priorityB !== priorityA) {
      return priorityB - priorityA;
    }
    
    // If same priority, use default priority
    return b.priority - a.priority;
  });
}

/**
 * Filter sections based on specialty relevance
 * Hides sections with very low relevance (< 3)
 */
export function filterSectionsBySpecialty(
  sections: DashboardSection[],
  specialty: string | null | undefined
): DashboardSection[] {
  if (!specialty) {
    return sections.filter(s => s.defaultVisible);
  }
  
  return sections.filter(section => {
    const priority = getSectionPriority(section.id, specialty);
    // Show if priority >= 3 or explicitly marked as defaultVisible
    return priority >= 3 || section.defaultVisible;
  });
}

/**
 * Get recommended section layout for specialty
 * Returns: { visible: [...], hidden: [...], order: [...] }
 */
export function getSpecialtyLayout(
  sections: DashboardSection[],
  specialty: string | null | undefined
): {
  visible: DashboardSection[];
  hidden: DashboardSection[];
  order: string[];
} {
  const filtered = filterSectionsBySpecialty(sections, specialty);
  const sorted = sortSectionsBySpecialty(filtered, specialty);
  const hidden = sections.filter(s => !sorted.includes(s));
  
  return {
    visible: sorted,
    hidden,
    order: sorted.map(s => s.id),
  };
}

/**
 * Component to wrap dashboard sections with specialty-based adaptation
 */
interface SpecialtyDashboardAdapterProps {
  specialty: string | null | undefined;
  sections: DashboardSection[];
  children?: React.ReactNode;
}

export function SpecialtyDashboardAdapter({
  specialty,
  sections,
  children,
}: SpecialtyDashboardAdapterProps) {
  const layout = getSpecialtyLayout(sections, specialty);
  
  return (
    <div className="space-y-6">
      {/* Render sections in specialty-optimized order */}
      {layout.visible.map((section) => (
        <div key={section.id} data-section-id={section.id} data-priority={getSectionPriority(section.id, specialty)}>
          {section.component}
        </div>
      ))}
      
      {/* Optional: Show hidden sections in a collapsible "More" section */}
      {layout.hidden.length > 0 && (
        <details className="bg-gray-50 rounded-lg p-4">
          <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
            More Sections ({layout.hidden.length})
          </summary>
          <div className="mt-4 space-y-4">
            {layout.hidden.map((section) => (
              <div key={section.id}>
                {section.component}
              </div>
            ))}
          </div>
        </details>
      )}
      
      {children}
    </div>
  );
}

/**
 * Hook to get specialty-optimized section configuration
 */
export function useSpecialtyLayout(specialty: string | null | undefined) {
  return React.useMemo(() => {
    return {
      getPriority: (sectionId: string) => getSectionPriority(sectionId, specialty),
      sortSections: (sections: DashboardSection[]) => sortSectionsBySpecialty(sections, specialty),
      filterSections: (sections: DashboardSection[]) => filterSectionsBySpecialty(sections, specialty),
      getLayout: (sections: DashboardSection[]) => getSpecialtyLayout(sections, specialty),
    };
  }, [specialty]);
}

