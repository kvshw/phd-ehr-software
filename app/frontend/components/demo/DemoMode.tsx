/**
 * Demo Mode Component
 * Provides an interactive guided tour for professor demonstrations
 * 
 * Features:
 * - Step-by-step guided tour
 * - Highlight key features
 * - Show MAPE-K adaptations in action
 * - Before/After comparison views
 * - Auto-advance with manual override
 */
'use client';

import { useState, useEffect, useCallback, createContext, useContext } from 'react';
import { createPortal } from 'react-dom';

interface DemoStep {
  id: string;
  title: string;
  description: string;
  target?: string; // CSS selector for element to highlight
  position: 'top' | 'bottom' | 'left' | 'right' | 'center';
  spotlight?: boolean;
  action?: () => void;
  category: 'introduction' | 'ai' | 'mape-k' | 'finnish' | 'research';
}

const DEMO_STEPS: DemoStep[] = [
  {
    id: 'welcome',
    title: '🎓 Welcome to the PhD Research Platform',
    description: 'This is a Self-Adaptive AI-Assisted Electronic Health Record (EHR) system designed for Finnish healthcare research. The system uses MAPE-K architecture to adapt the UI based on clinician behavior.',
    position: 'center',
    category: 'introduction',
  },
  {
    id: 'dashboard',
    title: '📊 Patient Dashboard',
    description: 'The dashboard shows all patients with their key information at a glance. The layout adapts based on your role (doctor, nurse, researcher) and specialty.',
    target: '[data-demo="patient-list"]',
    position: 'bottom',
    spotlight: true,
    category: 'introduction',
  },
  {
    id: 'ai-suggestions',
    title: '🤖 AI Clinical Suggestions',
    description: 'The AI generates evidence-based clinical suggestions with confidence scores, explanations, and medical citations. Each suggestion includes GRADE evidence levels and links to clinical guidelines.',
    target: '[data-demo="ai-suggestions"]',
    position: 'left',
    spotlight: true,
    category: 'ai',
  },
  {
    id: 'explainable-ai',
    title: '📚 Explainable AI',
    description: 'Every AI suggestion includes:\n• Pathophysiological mechanism\n• Clinical guidelines (AHA, ESC, NICE)\n• PubMed citations\n• Limitations and clinical pearls\n\nThis transparency is crucial for clinician trust and academic rigor.',
    position: 'center',
    category: 'ai',
  },
  {
    id: 'mape-k',
    title: '🔄 MAPE-K Self-Adaptation',
    description: 'The system continuously:\n• Monitors user behavior\n• Analyzes patterns\n• Plans UI adaptations\n• Executes changes\n• Stores knowledge\n\nThe UI adapts to your workflow automatically!',
    target: '[data-demo="adaptation-indicator"]',
    position: 'bottom',
    spotlight: true,
    category: 'mape-k',
  },
  {
    id: 'adaptation-example',
    title: '✨ Adaptation in Action',
    description: 'Watch how the system adapts: If you frequently check vitals before labs, the UI will reorder sections to match your workflow. The adaptation indicator shows when changes are applied.',
    position: 'center',
    category: 'mape-k',
  },
  {
    id: 'finnish-features',
    title: '🇫🇮 Finnish Healthcare Integration',
    description: 'The system includes Finnish-specific features:\n• Henkilötunnus (Personal ID) validation\n• Kela Card integration\n• Municipality-based care\n• Finnish/Swedish/English support\n• Kanta service simulation',
    position: 'center',
    category: 'finnish',
  },
  {
    id: 'feedback-loop',
    title: '📝 Feedback Collection',
    description: 'Clinician feedback on AI suggestions feeds back into the system to improve future recommendations. This creates a learning loop essential for research validation.',
    target: '[data-demo="feedback-buttons"]',
    position: 'top',
    spotlight: true,
    category: 'research',
  },
  {
    id: 'research-analytics',
    title: '📈 Research Analytics',
    description: 'The Research Dashboard provides:\n• Adaptation effectiveness metrics\n• AI suggestion acceptance rates\n• User behavior analytics\n• Exportable data for thesis analysis\n\nAll data is anonymized and GDPR-compliant.',
    position: 'center',
    category: 'research',
  },
  {
    id: 'safety',
    title: '⚠️ Safety & Transparency',
    description: 'All AI outputs are clearly labeled as "Experimental". The system never makes autonomous decisions - it only suggests. Comprehensive audit trails ensure accountability.',
    position: 'center',
    category: 'ai',
  },
  {
    id: 'conclusion',
    title: '🎉 Demo Complete!',
    description: 'You\'ve seen the key features of this PhD research platform:\n\n✓ Self-Adaptive UI (MAPE-K)\n✓ Explainable AI Suggestions\n✓ Finnish Healthcare Integration\n✓ Research-Grade Analytics\n\nThank you for your attention!',
    position: 'center',
    category: 'introduction',
  },
];

interface DemoContextType {
  isActive: boolean;
  currentStep: number;
  startDemo: () => void;
  endDemo: () => void;
  nextStep: () => void;
  prevStep: () => void;
  goToStep: (index: number) => void;
}

const DemoContext = createContext<DemoContextType | null>(null);

export function useDemoMode() {
  const context = useContext(DemoContext);
  if (!context) {
    // Return a no-op context if not within provider
    return {
      isActive: false,
      currentStep: 0,
      startDemo: () => {},
      endDemo: () => {},
      nextStep: () => {},
      prevStep: () => {},
      goToStep: () => {},
    };
  }
  return context;
}

export function DemoModeProvider({ children }: { children: React.ReactNode }) {
  const [isActive, setIsActive] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  const startDemo = useCallback(() => {
    setIsActive(true);
    setCurrentStep(0);
  }, []);

  const endDemo = useCallback(() => {
    setIsActive(false);
    setCurrentStep(0);
  }, []);

  const nextStep = useCallback(() => {
    setCurrentStep((prev) => Math.min(prev + 1, DEMO_STEPS.length - 1));
  }, []);

  const prevStep = useCallback(() => {
    setCurrentStep((prev) => Math.max(prev - 1, 0));
  }, []);

  const goToStep = useCallback((index: number) => {
    setCurrentStep(Math.max(0, Math.min(index, DEMO_STEPS.length - 1)));
  }, []);

  // Keyboard navigation
  useEffect(() => {
    if (!isActive) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault();
        nextStep();
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        prevStep();
      } else if (e.key === 'Escape') {
        endDemo();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isActive, nextStep, prevStep, endDemo]);

  return (
    <DemoContext.Provider value={{ isActive, currentStep, startDemo, endDemo, nextStep, prevStep, goToStep }}>
      {children}
      {isActive && <DemoOverlay step={DEMO_STEPS[currentStep]} stepIndex={currentStep} totalSteps={DEMO_STEPS.length} />}
    </DemoContext.Provider>
  );
}

function DemoOverlay({ step, stepIndex, totalSteps }: { step: DemoStep; stepIndex: number; totalSteps: number }) {
  const { nextStep, prevStep, endDemo, goToStep } = useDemoMode();
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);

  useEffect(() => {
    if (step.target) {
      const element = document.querySelector(step.target);
      if (element) {
        setTargetRect(element.getBoundingClientRect());
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        setTargetRect(null);
      }
    } else {
      setTargetRect(null);
    }
  }, [step.target]);

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'introduction': return 'bg-blue-500';
      case 'ai': return 'bg-purple-500';
      case 'mape-k': return 'bg-green-500';
      case 'finnish': return 'bg-indigo-500';
      case 'research': return 'bg-amber-500';
      default: return 'bg-gray-500';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'introduction': return '📖';
      case 'ai': return '🤖';
      case 'mape-k': return '🔄';
      case 'finnish': return '🇫🇮';
      case 'research': return '📊';
      default: return '📌';
    }
  };

  const tooltipPosition = () => {
    if (!targetRect || step.position === 'center') {
      return {
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
      };
    }

    const offset = 20;
    switch (step.position) {
      case 'top':
        return {
          top: `${targetRect.top - offset}px`,
          left: `${targetRect.left + targetRect.width / 2}px`,
          transform: 'translate(-50%, -100%)',
        };
      case 'bottom':
        return {
          top: `${targetRect.bottom + offset}px`,
          left: `${targetRect.left + targetRect.width / 2}px`,
          transform: 'translate(-50%, 0)',
        };
      case 'left':
        return {
          top: `${targetRect.top + targetRect.height / 2}px`,
          left: `${targetRect.left - offset}px`,
          transform: 'translate(-100%, -50%)',
        };
      case 'right':
        return {
          top: `${targetRect.top + targetRect.height / 2}px`,
          left: `${targetRect.right + offset}px`,
          transform: 'translate(0, -50%)',
        };
      default:
        return {
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
        };
    }
  };

  return createPortal(
    <div className="fixed inset-0 z-[9999]">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={endDemo} />
      
      {/* Spotlight */}
      {targetRect && step.spotlight && (
        <div
          className="absolute bg-white/10 ring-4 ring-white/50 rounded-lg transition-all duration-300"
          style={{
            top: targetRect.top - 8,
            left: targetRect.left - 8,
            width: targetRect.width + 16,
            height: targetRect.height + 16,
          }}
        />
      )}
      
      {/* Tooltip */}
      <div
        className="absolute bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 overflow-hidden transition-all duration-300"
        style={tooltipPosition()}
      >
        {/* Category Header */}
        <div className={`${getCategoryColor(step.category)} px-6 py-3 flex items-center gap-3`}>
          <span className="text-2xl">{getCategoryIcon(step.category)}</span>
          <span className="text-white font-medium capitalize">{step.category.replace('-', ' ')}</span>
          <span className="ml-auto text-white/80 text-sm">
            {stepIndex + 1} / {totalSteps}
          </span>
        </div>
        
        {/* Content */}
        <div className="p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-3">{step.title}</h3>
          <p className="text-gray-600 whitespace-pre-line leading-relaxed">{step.description}</p>
        </div>
        
        {/* Progress Bar */}
        <div className="px-6 pb-4">
          <div className="flex gap-1">
            {DEMO_STEPS.map((_, index) => (
              <button
                key={index}
                onClick={() => goToStep(index)}
                className={`h-1.5 flex-1 rounded-full transition-colors ${
                  index === stepIndex
                    ? getCategoryColor(DEMO_STEPS[index].category)
                    : index < stepIndex
                    ? 'bg-gray-300'
                    : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
        </div>
        
        {/* Navigation */}
        <div className="px-6 py-4 bg-gray-50 flex items-center justify-between border-t">
          <button
            onClick={prevStep}
            disabled={stepIndex === 0}
            className="px-4 py-2 text-gray-600 hover:text-gray-900 disabled:opacity-30 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Previous
          </button>
          
          <button
            onClick={endDemo}
            className="px-4 py-2 text-gray-500 hover:text-gray-700 text-sm"
          >
            Press ESC to exit
          </button>
          
          {stepIndex === totalSteps - 1 ? (
            <button
              onClick={endDemo}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
            >
              Finish
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </button>
          ) : (
            <button
              onClick={nextStep}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
            >
              Next
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          )}
        </div>
      </div>
      
      {/* Keyboard Hints */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex items-center gap-4 text-white/70 text-sm">
        <span className="flex items-center gap-1">
          <kbd className="px-2 py-1 bg-white/20 rounded">←</kbd>
          <kbd className="px-2 py-1 bg-white/20 rounded">→</kbd>
          Navigate
        </span>
        <span className="flex items-center gap-1">
          <kbd className="px-2 py-1 bg-white/20 rounded">Space</kbd>
          Next
        </span>
        <span className="flex items-center gap-1">
          <kbd className="px-2 py-1 bg-white/20 rounded">ESC</kbd>
          Exit
        </span>
      </div>
    </div>,
    document.body
  );
}

/**
 * Demo Mode Trigger Button
 * Add this to your header or navigation
 */
export function DemoModeButton() {
  const { startDemo, isActive } = useDemoMode();
  
  if (isActive) return null;
  
  return (
    <button
      onClick={startDemo}
      className="px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-lg hover:from-indigo-600 hover:to-purple-600 shadow-lg hover:shadow-xl transition-all flex items-center gap-2 text-sm font-medium"
    >
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      Start Demo
    </button>
  );
}

export default DemoModeProvider;

