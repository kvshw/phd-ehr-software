/**
 * Patient detail store for managing section ordering and state
 */
import { create } from 'zustand';
import { SectionId } from '@/components/patient-detail/SectionNavigation';

interface PatientDetailState {
  activeSection: SectionId;
  sectionOrder: SectionId[];
  suggestionDensity: 'low' | 'medium' | 'high';
  adaptationActive: boolean;
  adaptationExplanation: string | null;
  setActiveSection: (section: SectionId) => void;
  setSectionOrder: (order: SectionId[]) => void;
  setSuggestionDensity: (density: 'low' | 'medium' | 'high') => void;
  setAdaptationActive: (active: boolean) => void;
  setAdaptationExplanation: (explanation: string | null) => void;
  resetSectionOrder: () => void;
  resetAdaptation: () => void;
}

const defaultSectionOrder: SectionId[] = [
  'summary',
  'demographics',
  'diagnoses',
  'medications',
  'allergies',
  'vitals',
  'labs',
  'imaging',
  'suggestions',
  'safety',
];

export const usePatientDetailStore = create<PatientDetailState>((set) => ({
  activeSection: 'summary',
  sectionOrder: defaultSectionOrder,
  suggestionDensity: 'medium',
  adaptationActive: false,
  adaptationExplanation: null,
  
  setActiveSection: (section) => set({ activeSection: section }),
  
  setSectionOrder: (order) => set({ sectionOrder: order }),
  
  setSuggestionDensity: (density) => set({ suggestionDensity: density }),
  
  setAdaptationActive: (active) => set({ adaptationActive: active }),
  
  setAdaptationExplanation: (explanation) => set({ adaptationExplanation: explanation }),
  
  resetSectionOrder: () => set({ sectionOrder: defaultSectionOrder }),
  
  resetAdaptation: () => set({
    sectionOrder: defaultSectionOrder,
    suggestionDensity: 'medium',
    adaptationActive: false,
    adaptationExplanation: null,
  }),
}));

