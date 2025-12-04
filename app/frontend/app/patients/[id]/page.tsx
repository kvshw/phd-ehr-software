/**
 * Patient detail page
 */
'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { patientService, Patient } from '@/lib/patientService';
import { PatientHeader } from '@/components/patient-detail/PatientHeader';
import { SectionNavigation, SectionId } from '@/components/patient-detail/SectionNavigation';
import { SummarySection } from '@/components/patient-detail/SummarySection';
import { DemographicsSection } from '@/components/patient-detail/DemographicsSection';
import { DiagnosesSection } from '@/components/patient-detail/DiagnosesSection';
import { ClinicalNotesSection } from '@/components/patient-detail/ClinicalNotesSection';
import { ProblemsSection } from '@/components/patient-detail/ProblemsSection';
import { MedicationsSection } from '@/components/patient-detail/MedicationsSection';
import { AllergiesSection } from '@/components/patient-detail/AllergiesSection';
import { PatientHistorySection } from '@/components/patient-detail/PatientHistorySection';
import { VitalsSection } from '@/components/patient-detail/VitalsSection';
import { LabsSection } from '@/components/patient-detail/LabsSection';
import { ImagingSection } from '@/components/patient-detail/ImagingSection';
import { SuggestionsSection } from '@/components/patient-detail/SuggestionsSection';
import { ConversationSection } from '@/components/conversation/ConversationSection';
import { usePatientDetailStore } from '@/store/patientDetailStore';
import { RiskLevel } from '@/components/RiskBadge';
import { monitorService } from '@/lib/monitorService';
import { adaptationService } from '@/lib/adaptationService';
import { AdaptationIndicator } from '@/components/patient-detail/AdaptationIndicator';
import { BanditIndicator } from '@/components/adaptation/BanditIndicator';
import { TransferLearningIndicator } from '@/components/adaptation/TransferLearningIndicator';
import { SuggestionAuditTrail } from '@/components/safety/SuggestionAuditTrail';
import { AIStatusPanel } from '@/components/safety/AIStatusPanel';
import { TransparencyInfo } from '@/components/safety/TransparencyInfo';
import { TopHeader } from '@/components/layout/TopHeader';
import { AnonymizationNotice } from '@/components/common/AnonymizationNotice';

export default function PatientDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { isAuthenticated, checkAuth, isLoading: authLoading } = useAuthStore();
  const {
    activeSection,
    sectionOrder,
    setActiveSection,
    setSectionOrder,
    setSuggestionDensity,
    setAdaptationActive,
    setAdaptationExplanation,
  } = usePatientDetailStore();
  const patientId = params?.id as string;

  const [patient, setPatient] = useState<Patient | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [riskLevel, setRiskLevel] = useState<RiskLevel>('routine');

  // Wrapper to log navigation and update section
  const handleSectionChange = async (newSection: SectionId) => {
    const previousSection = activeSection;
    setActiveSection(newSection);
    
    // Log navigation for MAPE-K monitoring
    await monitorService.logNavigation({
      patientId: patientId,
      fromSection: previousSection,
      toSection: newSection,
    });
  };

  const [hasCheckedAuth, setHasCheckedAuth] = useState(false);

  useEffect(() => {
    const doCheck = async () => {
      await checkAuth();
      setHasCheckedAuth(true);
    };
    doCheck();
  }, [checkAuth]);

  useEffect(() => {
    // Only redirect AFTER auth check has completed
    if (hasCheckedAuth && !authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [hasCheckedAuth, isAuthenticated, authLoading, router]);

  useEffect(() => {
    // Only fetch patient after auth check completes and user is authenticated
    if (hasCheckedAuth && patientId && isAuthenticated) {
      fetchPatient();
      fetchAndApplyAdaptation();
    }
  }, [hasCheckedAuth, patientId, isAuthenticated]);

  const fetchAndApplyAdaptation = async () => {
    try {
      const adaptation = await adaptationService.getLatestAdaptation(patientId);
      
      if (adaptation && adaptation.plan_json) {
        const plan = adaptation.plan_json;
        
        // Apply section ordering
        if (plan.order && Array.isArray(plan.order)) {
          // Validate that all section IDs are valid
          const validOrder = plan.order.filter((id): id is SectionId => {
            return ['summary', 'demographics', 'diagnoses', 'clinical-notes', 'problems', 'medications', 'allergies', 'history', 'vitals', 'labs', 'imaging', 'suggestions', 'safety'].includes(id);
          });
          
          // Ensure all sections are included (add missing ones at the end)
          const allSections: SectionId[] = ['summary', 'demographics', 'diagnoses', 'clinical-notes', 'problems', 'medications', 'allergies', 'history', 'vitals', 'labs', 'imaging', 'conversation', 'suggestions', 'safety'];
          const missingSections = allSections.filter(s => !validOrder.includes(s));
          const finalOrder = [...validOrder, ...missingSections];
          
          setSectionOrder(finalOrder);
        }
        
        // Apply suggestion density
        if (plan.suggestion_density) {
          setSuggestionDensity(plan.suggestion_density);
        }
        
        // Mark adaptation as active
        setAdaptationActive(true);
        setAdaptationExplanation(plan.explanation || 'Layout adapted based on your usage patterns');
      }
    } catch (err) {
      // Silently fail - adaptations are optional
      console.error('Failed to fetch adaptation plan:', err);
    }
  };

  const fetchPatient = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await patientService.getPatient(patientId);
      setPatient(data);
      // TODO: Fetch risk level from vital risk service (Task 15)
      // For now, default to routine
      setRiskLevel('routine');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load patient');
      console.error('Error fetching patient:', err);
    } finally {
      setLoading(false);
    }
  };

  // Show loading until auth check completes
  if (!hasCheckedAuth || authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading patient data...</p>
        </div>
      </div>
    );
  }

  // Only redirect if auth check completed and user is not authenticated
  if (hasCheckedAuth && !isAuthenticated) {
    return null; // Will redirect to login
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <button
              onClick={() => router.back()}
              className="mb-4 text-sm text-indigo-600 hover:text-indigo-800"
            >
              ← Back to Dashboard
            </button>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800">{error}</p>
              <button
                onClick={fetchPatient}
                className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!patient) {
    return null;
  }

  const sections = [
    { id: 'summary' as SectionId, label: 'Summary' },
    { id: 'demographics' as SectionId, label: 'Demographics' },
    { id: 'diagnoses' as SectionId, label: 'Diagnoses' },
    { id: 'clinical-notes' as SectionId, label: 'Clinical Notes' },
    { id: 'problems' as SectionId, label: 'Problems' },
    { id: 'medications' as SectionId, label: 'Medications' },
    { id: 'allergies' as SectionId, label: 'Allergies' },
    { id: 'history' as SectionId, label: 'History' },
    { id: 'vitals' as SectionId, label: 'Vitals' },
    { id: 'labs' as SectionId, label: 'Labs' },
    { id: 'imaging' as SectionId, label: 'Imaging' },
    { id: 'conversation' as SectionId, label: 'Conversation' },
    { id: 'suggestions' as SectionId, label: 'AI Suggestions' },
    { id: 'safety' as SectionId, label: 'Safety & Transparency' },
  ];

  const renderSection = () => {
    switch (activeSection) {
      case 'summary':
        return <SummarySection patient={patient} />;
      case 'demographics':
        return <DemographicsSection patient={patient} />;
      case 'diagnoses':
        return <DiagnosesSection patient={patient} />;
      case 'clinical-notes':
        return <ClinicalNotesSection patientId={patientId} />;
      case 'problems':
        return <ProblemsSection patientId={patientId} />;
      case 'medications':
        return <MedicationsSection patientId={patientId} />;
      case 'allergies':
        return <AllergiesSection patientId={patientId} />;
      case 'history':
        return <PatientHistorySection patient={patient} />;
      case 'vitals':
        return <VitalsSection patientId={patient.id} />;
      case 'labs':
        return <LabsSection patientId={patient.id} />;
      case 'imaging':
        return <ImagingSection patientId={patient.id} />;
      case 'conversation':
        return <ConversationSection patientId={patient.id} />;
      case 'suggestions':
        return <SuggestionsSection patientId={patient.id} />;
      case 'safety':
        return (
          <div className="space-y-6">
            <AIStatusPanel />
            <SuggestionAuditTrail patientId={patient.id} />
            <TransparencyInfo />
          </div>
        );
      default:
        return <SummarySection patient={patient} />;
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Top Header */}
      <TopHeader currentPage="Overview" />

      <div className="max-w-[1600px] mx-auto px-6 py-8">
        <div className="bg-white rounded-2xl shadow border border-gray-200 p-6 mb-6">
          <button
            onClick={() => router.push('/dashboard')}
            className="mb-4 text-sm text-blue-600 hover:text-blue-800 flex items-center gap-2 font-medium"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Dashboard
          </button>

          <PatientHeader patient={patient} riskLevel={riskLevel} />

          {patient.is_anonymized && (
            <div className="mt-4">
              <AnonymizationNotice />
            </div>
          )}

          <div className="mt-4 flex items-start gap-3 flex-wrap">
            <AdaptationIndicator />
            <BanditIndicator showDetails={true} />
            <TransferLearningIndicator showDetails={true} />
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow border border-gray-200 p-6">
          <SectionNavigation
            sections={sections}
            activeSection={activeSection}
            onSectionChange={handleSectionChange}
            sectionOrder={sectionOrder}
          />

          <div className="mt-6">
            {renderSection()}
          </div>
        </div>
      </div>
    </div>
  );
}

