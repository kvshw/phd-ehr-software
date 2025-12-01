'use client';

import { useState, useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/apiClient';
import { TopHeader } from '@/components/layout/TopHeader';

interface Patient {
  id: string;
  first_name: string;
  last_name: string;
  name?: string;
  date_of_birth: string;
  age?: number;
  gender?: string;
  chief_complaint?: string;
  arrival_time?: string;
  triage_status: 'pending' | 'in_progress' | 'completed' | 'referred';
  ai_suggested_specialty?: string;
  ai_confidence?: number;
  assigned_specialty?: string;
  priority: 'critical' | 'urgent' | 'standard' | 'non_urgent';
  symptoms?: string[];
  vitals?: {
    bp?: string;
    hr?: number;
    temp?: number;
    spo2?: number;
  };
}

interface Referral {
  id: string;
  patient_id: string;
  target_specialty: string;
  priority: string;
  status: string;
  chief_complaint?: string;
  created_at: string;
  patient?: {
    id: string;
    name: string;
    age: number;
  };
}

const SPECIALTY_INFO: Record<string, { name: string; icon: string; color: string }> = {
  cardiology: { name: 'Cardiology', icon: '❤️', color: 'bg-red-100 text-red-800' },
  neurology: { name: 'Neurology', icon: '🧠', color: 'bg-purple-100 text-purple-800' },
  orthopedics: { name: 'Orthopedics', icon: '🦴', color: 'bg-orange-100 text-orange-800' },
  pediatrics: { name: 'Pediatrics', icon: '👶', color: 'bg-pink-100 text-pink-800' },
  psychiatry: { name: 'Psychiatry', icon: '🧘', color: 'bg-indigo-100 text-indigo-800' },
  emergency: { name: 'Emergency', icon: '🚑', color: 'bg-red-100 text-red-800' },
  internal: { name: 'Internal Medicine', icon: '🩺', color: 'bg-blue-100 text-blue-800' },
  surgery: { name: 'Surgery', icon: '⚕️', color: 'bg-green-100 text-green-800' },
  dermatology: { name: 'Dermatology', icon: '🔬', color: 'bg-yellow-100 text-yellow-800' },
  oncology: { name: 'Oncology', icon: '🎗️', color: 'bg-violet-100 text-violet-800' },
  general: { name: 'General Practice', icon: '👨‍⚕️', color: 'bg-gray-100 text-gray-800' },
  pulmonology: { name: 'Pulmonology', icon: '🫁', color: 'bg-sky-100 text-sky-800' },
  gastroenterology: { name: 'Gastroenterology', icon: '🏥', color: 'bg-amber-100 text-amber-800' },
  endocrinology: { name: 'Endocrinology', icon: '💉', color: 'bg-lime-100 text-lime-800' },
  nephrology: { name: 'Nephrology', icon: '🫘', color: 'bg-teal-100 text-teal-800' },
  rheumatology: { name: 'Rheumatology', icon: '🦴', color: 'bg-rose-100 text-rose-800' },
  urology: { name: 'Urology', icon: '🏥', color: 'bg-cyan-100 text-cyan-800' },
  infectious_disease: { name: 'Infectious Disease', icon: '🦠', color: 'bg-emerald-100 text-emerald-800' },
  hematology: { name: 'Hematology', icon: '🩸', color: 'bg-red-100 text-red-800' },
  geriatrics: { name: 'Geriatrics', icon: '👴', color: 'bg-slate-100 text-slate-800' },
};

const PRIORITY_COLORS = {
  critical: 'bg-red-500 text-white animate-pulse',
  urgent: 'bg-orange-500 text-white',
  standard: 'bg-yellow-500 text-white',
  non_urgent: 'bg-green-500 text-white',
};

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  accepted: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-indigo-100 text-indigo-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-gray-100 text-gray-800',
};

export default function NurseDashboardPage() {
  const router = useRouter();
  const { isAuthenticated, user, checkAuth, isLoading: authLoading } = useAuthStore();
  const [hasCheckedAuth, setHasCheckedAuth] = useState(false);
  const [activeTab, setActiveTab] = useState<'triage' | 'patients' | 'referrals'>('triage');
  
  // Triage queue state
  const [triageQueue, setTriageQueue] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  
  // All patients state
  const [allPatients, setAllPatients] = useState<Patient[]>([]);
  const [patientsLoading, setPatientsLoading] = useState(false);
  
  // Referrals state
  const [myReferrals, setMyReferrals] = useState<Referral[]>([]);
  const [referralsLoading, setReferralsLoading] = useState(false);
  
  // Referral modal
  const [showReferModal, setShowReferModal] = useState(false);
  const [referPatient, setReferPatient] = useState<Patient | null>(null);
  const [referSpecialty, setReferSpecialty] = useState('');
  const [referPriority, setReferPriority] = useState('standard');
  const [referNotes, setReferNotes] = useState('');
  const [referLoading, setReferLoading] = useState(false);
  
  // AI triage suggestions
  const [aiSuggestion, setAiSuggestion] = useState<{
    specialty: string;
    specialty_confidence: number;
    priority: string;
    explanation: string;
    alternative_specialties?: Record<string, number>;
  } | null>(null);
  const [aiLoading, setAiLoading] = useState(false);

  const [stats, setStats] = useState({
    totalWaiting: 0,
    critical: 0,
    urgent: 0,
    avgWaitTime: '-- min',
    completedToday: 0,
  });

  useEffect(() => {
    const doCheck = async () => {
      await checkAuth();
      setHasCheckedAuth(true);
    };
    doCheck();
  }, [checkAuth]);

  useEffect(() => {
    if (hasCheckedAuth && !isAuthenticated) {
      router.push('/login');
    }
    if (hasCheckedAuth && user && user.role !== 'nurse' && user.role !== 'admin') {
      router.push('/dashboard');
    }
  }, [hasCheckedAuth, isAuthenticated, user, router]);

  // Fetch all patients
  useEffect(() => {
    if (isAuthenticated && activeTab === 'patients') {
      fetchAllPatients();
    }
  }, [isAuthenticated, activeTab]);

  // Fetch my referrals
  useEffect(() => {
    if (isAuthenticated && activeTab === 'referrals') {
      fetchMyReferrals();
    }
  }, [isAuthenticated, activeTab]);

  const fetchAllPatients = async () => {
    setPatientsLoading(true);
    try {
      const response = await apiClient.get('/patients?page=1&page_size=50');
      const patients = response.data.items.map((p: any) => ({
        id: p.id,
        first_name: p.first_name || p.name?.split(' ')[0] || '',
        last_name: p.last_name || p.name?.split(' ').slice(1).join(' ') || '',
        name: p.name,
        date_of_birth: p.date_of_birth,
        age: p.age,
        gender: p.gender,
        triage_status: 'pending' as const,
        priority: 'standard' as const,
      }));
      setAllPatients(patients);
    } catch (error) {
      console.error('Error fetching patients:', error);
    } finally {
      setPatientsLoading(false);
    }
  };

  const fetchMyReferrals = async () => {
    setReferralsLoading(true);
    try {
      const response = await apiClient.get('/referrals/nurse/sent');
      // Ensure we have valid data structure
      if (response.data && Array.isArray(response.data.referrals)) {
        // Validate and sanitize referral data
        const validReferrals = response.data.referrals.map((ref: any) => ({
          id: String(ref.id || ''),
          patient_id: String(ref.patient_id || ''),
          target_specialty: String(ref.target_specialty || ''),
          priority: String(ref.priority || 'standard'),
          status: String(ref.status || 'pending'),
          created_at: typeof ref.created_at === 'string' ? ref.created_at : new Date().toISOString(),
          patient: ref.patient ? {
            id: String(ref.patient.id || ''),
            name: String(ref.patient.name || 'Patient'),
            age: Number(ref.patient.age) || 0,
          } : undefined,
        }));
        setMyReferrals(validReferrals);
      } else {
        setMyReferrals([]);
      }
    } catch (error) {
      console.error('Error fetching referrals:', error);
      // Show demo data if API fails
      setMyReferrals([]);
    } finally {
      setReferralsLoading(false);
    }
  };

  const handleSendToDoctor = async (patient: Patient) => {
    setReferPatient(patient);
    setReferSpecialty('');
    setReferPriority('standard');
    setReferNotes('');
    setAiSuggestion(null);
    setShowReferModal(true);
    
    // Fetch AI triage suggestion for this patient
    setAiLoading(true);
    try {
      console.log('Fetching AI triage suggestion for patient:', patient.id);
      const response = await apiClient.get(`/triage/patient/${patient.id}`);
      console.log('AI triage suggestion response:', response.data);
      const suggestion = response.data;
      setAiSuggestion(suggestion);
      // Pre-fill specialty and priority from AI suggestion
      if (suggestion.specialty) {
        setReferSpecialty(suggestion.specialty);
      }
      if (suggestion.priority) {
        setReferPriority(suggestion.priority);
      }
    } catch (error: any) {
      console.error('Error fetching AI triage suggestion:', error);
      console.error('Error details:', error.response?.data || error.message);
      // Don't show error to user - just proceed without AI suggestion
      // But log it for debugging
      setAiSuggestion(null);
    } finally {
      setAiLoading(false);
    }
  };

  const handleSubmitReferral = async () => {
    if (!referPatient || !referSpecialty) return;
    
    setReferLoading(true);
    try {
      // Determine if nurse overrode AI suggestion
      const aiSuggestedSpecialty = aiSuggestion?.specialty || referPatient.ai_suggested_specialty;
      const nurseOverrode = aiSuggestedSpecialty ? (aiSuggestedSpecialty !== referSpecialty) : false;
      
      console.log('Creating referral with AI data:', {
        ai_suggested_specialty: aiSuggestedSpecialty,
        ai_confidence: aiSuggestion?.specialty_confidence,
        nurse_override: nurseOverrode,
        target_specialty: referSpecialty,
      });
      
      await apiClient.post('/referrals/create', {
        patient_id: referPatient.id,
        target_specialty: referSpecialty,
        priority: referPriority,
        chief_complaint: referPatient.chief_complaint,
        symptoms: referPatient.symptoms || [],
        vitals: referPatient.vitals || {},
        triage_notes: referNotes,
        ai_suggested_specialty: aiSuggestedSpecialty || null,
        ai_confidence: aiSuggestion?.specialty_confidence || (referPatient.ai_confidence ? parseFloat(referPatient.ai_confidence) : null),
        nurse_override: nurseOverrode,
      });
      
      // Update UI
      setShowReferModal(false);
      setReferPatient(null);
      
      // Remove from triage queue if applicable
      setTriageQueue(prev => prev.filter(p => p.id !== referPatient.id));
      
      // Refresh referrals
      if (activeTab === 'referrals') {
        fetchMyReferrals();
      }
      
      alert(`Patient referred to ${SPECIALTY_INFO[referSpecialty]?.name || referSpecialty} successfully!`);
    } catch (error: any) {
      console.error('Error creating referral:', error);
      
      // Handle Pydantic validation errors (array format)
      let errorMessage = 'Failed to create referral. Please try again.';
      
      if (error.response?.data) {
        const data = error.response.data;
        // Pydantic validation errors come as an array
        if (Array.isArray(data.detail)) {
          errorMessage = data.detail.map((err: any) => 
            typeof err === 'string' ? err : err.msg || JSON.stringify(err)
          ).join(', ');
        } else if (typeof data.detail === 'string') {
          errorMessage = data.detail;
        } else if (data.message) {
          errorMessage = data.message;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      // Ensure errorMessage is a string
      if (typeof errorMessage !== 'string') {
        errorMessage = String(errorMessage);
      }
      
      // Check if it's a UUID validation error
      if (errorMessage.includes('Invalid patient ID') || errorMessage.includes('UUID') || errorMessage.includes('badly formed')) {
        alert('⚠️ This patient is a demo/test patient. Please select a real patient from the "All Patients" tab to create a referral.');
      } else if (errorMessage.includes('not found')) {
        alert('⚠️ Patient not found. Please select a valid patient.');
      } else if (errorMessage.includes('table does not exist')) {
        alert('⚠️ Database setup required. Please contact administrator to run the SQL migration script.');
      } else {
        alert(`Failed to create referral: ${errorMessage}`);
      }
    } finally {
      setReferLoading(false);
    }
  };

  if (!hasCheckedAuth || authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 to-cyan-50">
      <TopHeader currentPage="Nurse" />

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Welcome Banner */}
        <div className="bg-gradient-to-r from-teal-600 to-cyan-600 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">
                Good Morning, {user?.first_name || 'Nurse'} 👩‍⚕️
              </h1>
              <p className="text-teal-100 mt-1">Patient Triage & Routing Dashboard</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold">{stats.totalWaiting}</div>
              <div className="text-teal-100 text-sm">Patients Waiting</div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-1 flex gap-1">
          <button
            onClick={() => setActiveTab('triage')}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${
              activeTab === 'triage'
                ? 'bg-teal-600 text-white shadow'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            🚑 Triage Queue
          </button>
          <button
            onClick={() => setActiveTab('patients')}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${
              activeTab === 'patients'
                ? 'bg-teal-600 text-white shadow'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            👥 All Patients
          </button>
          <button
            onClick={() => setActiveTab('referrals')}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${
              activeTab === 'referrals'
                ? 'bg-teal-600 text-white shadow'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            📋 My Referrals
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'triage' && (
          <TriageQueueTab
            triageQueue={triageQueue}
            setTriageQueue={setTriageQueue}
            selectedPatient={selectedPatient}
            setSelectedPatient={setSelectedPatient}
            onSendToDoctor={handleSendToDoctor}
            stats={stats}
          />
        )}

        {activeTab === 'patients' && (
          <AllPatientsTab
            patients={allPatients}
            loading={patientsLoading}
            onSendToDoctor={handleSendToDoctor}
            onRefresh={fetchAllPatients}
          />
        )}

        {activeTab === 'referrals' && (
          <MyReferralsTab
            referrals={myReferrals}
            loading={referralsLoading}
            onRefresh={fetchMyReferrals}
          />
        )}
      </main>

      {/* Referral Modal */}
      {showReferModal && referPatient && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] flex flex-col overflow-hidden">
            <div className="bg-teal-600 px-6 py-4 flex items-center justify-between flex-shrink-0">
              <h2 className="text-lg font-semibold text-white">
                Send Patient to Doctor
              </h2>
              <button
                onClick={() => setShowReferModal(false)}
                className="text-white hover:text-teal-200"
              >
                ✕
              </button>
            </div>
            <div className="p-6 space-y-6 overflow-y-auto flex-1">
              {/* Patient Info */}
              <div className="bg-gray-50 rounded-xl p-4">
                <h3 className="font-semibold text-gray-900">
                  {referPatient.first_name} {referPatient.last_name}
                </h3>
                <p className="text-sm text-gray-500">
                  {referPatient.age || '--'} years • {referPatient.gender || 'Unknown'}
                </p>
                {referPatient.chief_complaint && (
                  <p className="text-sm text-gray-700 mt-2">
                    <strong>Complaint:</strong> {referPatient.chief_complaint}
                  </p>
                )}
              </div>

              {/* AI Triage Suggestion */}
              {aiLoading && (
                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                  <div className="flex items-center gap-2">
                    <div className="animate-spin h-5 w-5 border-2 border-blue-600 border-t-transparent rounded-full"></div>
                    <span className="text-sm text-blue-800">AI is analyzing patient data...</span>
                  </div>
                </div>
              )}
              
              {!aiLoading && !aiSuggestion && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                  <div className="flex items-start gap-2">
                    <span className="text-lg">⚠️</span>
                    <div>
                      <p className="text-sm font-medium text-amber-800">AI Suggestion Unavailable</p>
                      <p className="text-xs text-amber-700 mt-1">
                        Patient may not have enough clinical data (visits, notes, or vitals) for AI analysis. 
                        Please manually select the appropriate specialty.
                      </p>
                    </div>
                  </div>
                </div>
              )}
              
              {aiSuggestion && !aiLoading && (
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">🤖</span>
                      <h3 className="font-semibold text-gray-900">AI Triage Suggestion</h3>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      aiSuggestion.specialty_confidence > 0.8
                        ? 'bg-green-100 text-green-800'
                        : aiSuggestion.specialty_confidence > 0.6
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {(aiSuggestion.specialty_confidence * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-700">Recommended Specialty:</span>
                      <span className={`px-3 py-1 rounded-lg text-sm font-semibold ${
                        SPECIALTY_INFO[aiSuggestion.specialty]?.color || 'bg-gray-100 text-gray-800'
                      }`}>
                        {SPECIALTY_INFO[aiSuggestion.specialty]?.icon} {SPECIALTY_INFO[aiSuggestion.specialty]?.name || aiSuggestion.specialty}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-700">Priority:</span>
                      <span className={`px-3 py-1 rounded-lg text-sm font-semibold ${
                        PRIORITY_COLORS[aiSuggestion.priority as keyof typeof PRIORITY_COLORS] || 'bg-gray-100 text-gray-800'
                      }`}>
                        {aiSuggestion.priority.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                    
                    {aiSuggestion.explanation && (
                      <p className="text-sm text-gray-700 mt-2 italic">
                        {aiSuggestion.explanation}
                      </p>
                    )}
                    
                    {aiSuggestion.alternative_specialties && Object.keys(aiSuggestion.alternative_specialties).length > 0 && (
                      <div className="mt-3 pt-3 border-t border-blue-200">
                        <p className="text-xs font-medium text-gray-600 mb-2">Alternative Options:</p>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(aiSuggestion.alternative_specialties)
                            .slice(0, 3)
                            .map(([spec, score]) => (
                              <span key={spec} className="text-xs px-2 py-1 bg-white rounded border border-blue-200 text-gray-700">
                                {SPECIALTY_INFO[spec]?.name || spec}: {(score * 100).toFixed(0)}%
                              </span>
                            ))}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="mt-3 pt-3 border-t border-blue-200">
                    <p className="text-xs text-gray-600">
                      💡 <strong>Nurse Decision:</strong> Review the AI suggestion above. You can accept it or override with your clinical judgment.
                    </p>
                  </div>
                </div>
              )}

              {/* Specialty Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Select Specialty *
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {Object.entries(SPECIALTY_INFO).map(([id, info]) => (
                    <button
                      key={id}
                      type="button"
                      onClick={() => setReferSpecialty(id)}
                      className={`p-3 border-2 rounded-xl hover:border-teal-500 transition-all text-center ${
                        referSpecialty === id
                          ? 'border-teal-500 bg-teal-50'
                          : 'border-gray-200'
                      }`}
                    >
                      <div className="text-xl mb-1">{info.icon}</div>
                      <div className="text-xs font-medium text-gray-900">{info.name}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Priority Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Priority
                </label>
                <div className="flex gap-2">
                  {['critical', 'urgent', 'standard', 'non_urgent'].map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setReferPriority(p)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                        referPriority === p
                          ? PRIORITY_COLORS[p as keyof typeof PRIORITY_COLORS]
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {p.replace('_', ' ').toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Triage Notes (Optional)
                </label>
                <textarea
                  value={referNotes}
                  onChange={(e) => setReferNotes(e.target.value)}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 text-gray-900 bg-white"
                  placeholder="Add any notes for the doctor..."
                />
              </div>

            </div>
            {/* Actions - Fixed at bottom */}
            <div className="flex gap-3 p-6 border-t border-gray-200 bg-gray-50 flex-shrink-0">
              <button
                onClick={() => setShowReferModal(false)}
                className="flex-1 py-3 bg-gray-100 text-gray-700 rounded-xl font-semibold hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmitReferral}
                disabled={!referSpecialty || referLoading}
                className="flex-1 py-3 bg-teal-600 text-white rounded-xl font-semibold hover:bg-teal-700 transition-colors disabled:opacity-50"
              >
                {referLoading ? 'Sending...' : 'Send to Doctor'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Triage Queue Tab Component
function TriageQueueTab({
  triageQueue,
  setTriageQueue,
  selectedPatient,
  setSelectedPatient,
  onSendToDoctor,
  stats,
}: {
  triageQueue: Patient[];
  setTriageQueue: React.Dispatch<React.SetStateAction<Patient[]>>;
  selectedPatient: Patient | null;
  setSelectedPatient: (p: Patient | null) => void;
  onSendToDoctor: (p: Patient) => void;
  stats: any;
}) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch real patients for triage queue
  useEffect(() => {
    const fetchTriagePatients = async () => {
      setLoading(true);
      setError(null);
      try {
        // Fetch patients with their recent data
        const response = await apiClient.get('/patients?page=1&page_size=50');
        const patients = response.data.items;
        
        // Transform to triage format and get latest vitals/visits for each
        const triagePatients: Patient[] = await Promise.all(
          patients.map(async (p: any) => {
            // Try to get latest vitals
            let vitals: Patient['vitals'] = undefined;
            let chiefComplaint = p.primary_diagnosis || 'Needs assessment';
            
            try {
              const vitalsRes = await apiClient.get(`/vitals/patient/${p.id}?hours=168`); // Last 7 days
              if (vitalsRes.data.items?.length > 0) {
                const latestVital = vitalsRes.data.items[0];
                vitals = {
                  bp: latestVital.bp_sys && latestVital.bp_dia 
                    ? `${latestVital.bp_sys}/${latestVital.bp_dia}` 
                    : undefined,
                  hr: latestVital.hr,
                  temp: latestVital.temp,
                  spo2: latestVital.spo2,
                };
              }
            } catch (e) {
              // Silently fail - patient may not have vitals
            }

            // Try to get latest visit for chief complaint
            try {
              const visitsRes = await apiClient.get(`/visits/patient/${p.id}?limit=1`);
              if (visitsRes.data.visits?.length > 0) {
                chiefComplaint = visitsRes.data.visits[0].chief_complaint || chiefComplaint;
              }
            } catch (e) {
              // Silently fail
            }
            
            // Determine priority based on vitals
            let priority: Patient['priority'] = 'standard';
            if (vitals) {
              if (vitals.spo2 && vitals.spo2 < 92) priority = 'critical';
              else if (vitals.hr && vitals.hr > 120) priority = 'urgent';
              else if (vitals.temp && vitals.temp > 38.5) priority = 'urgent';
              else if (vitals.bp) {
                const [sys] = vitals.bp.split('/').map(Number);
                if (sys > 180 || sys < 90) priority = 'urgent';
              }
            }
            
            const nameParts = (p.name || '').split(' ');
            
            return {
              id: p.id,
              first_name: nameParts[0] || '',
              last_name: nameParts.slice(1).join(' ') || '',
              name: p.name,
              date_of_birth: p.date_of_birth,
              age: p.age,
              gender: p.sex,
              chief_complaint: chiefComplaint,
              arrival_time: new Date().toLocaleTimeString('fi-FI', { hour: '2-digit', minute: '2-digit' }),
              triage_status: 'pending' as const,
              priority,
              vitals,
            };
          })
        );
        
        // Sort by priority (critical first, then urgent, then standard)
        const priorityOrder = { critical: 0, urgent: 1, standard: 2, non_urgent: 3 };
        triagePatients.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
        
        setTriageQueue(triagePatients);
      } catch (err: any) {
        console.error('Error fetching triage patients:', err);
        setError('Failed to load patients. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchTriagePatients();
  }, [setTriageQueue]);

  return (
    <div className="grid grid-cols-3 gap-6">
      {/* Triage Queue */}
      <div className="col-span-2 bg-white rounded-2xl shadow-lg overflow-hidden">
        <div className="bg-teal-600 px-6 py-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">Triage Queue</h2>
          <div className="flex items-center gap-3">
            <span className="bg-teal-500 px-3 py-1 rounded-full text-sm text-white">
              {triageQueue.filter((p) => p.triage_status === 'pending').length} patients
            </span>
            <button
              onClick={() => window.location.reload()}
              className="px-2 py-1 bg-teal-500 hover:bg-teal-400 rounded text-white text-xs"
            >
              🔄 Refresh
            </button>
          </div>
        </div>

        {loading && (
          <div className="p-8 text-center">
            <div className="animate-spin h-8 w-8 border-2 border-teal-600 border-t-transparent rounded-full mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading patients...</p>
          </div>
        )}

        {error && (
          <div className="p-8 text-center">
            <div className="text-red-500 text-4xl mb-4">⚠️</div>
            <p className="text-red-600 font-medium">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700"
            >
              Try Again
            </button>
          </div>
        )}

        {!loading && !error && triageQueue.length === 0 && (
          <div className="p-8 text-center">
            <div className="text-gray-400 text-4xl mb-4">👥</div>
            <p className="text-gray-600 font-medium">No patients in the queue</p>
            <p className="text-sm text-gray-500 mt-1">
              Patients will appear here as they check in
            </p>
          </div>
        )}

        {!loading && !error && (
          <div className="divide-y divide-gray-100 max-h-[600px] overflow-y-auto">
            {triageQueue.map((patient) => (
              <div
                key={patient.id}
                onClick={() => setSelectedPatient(patient)}
                className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                  selectedPatient?.id === patient.id ? 'bg-teal-50' : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${PRIORITY_COLORS[patient.priority]}`}>
                      {patient.priority.toUpperCase()}
                    </span>
                    <div>
                      <div className="font-semibold text-gray-900">
                        {patient.first_name} {patient.last_name}
                      </div>
                      <div className="text-sm text-gray-500 truncate max-w-xs">{patient.chief_complaint}</div>
                      <div className="text-xs text-gray-400 mt-1">
                        {patient.age && `${patient.age}y`} {patient.gender && `• ${patient.gender}`}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {patient.vitals && (
                      <div className="hidden md:flex gap-2 text-xs">
                        {patient.vitals.hr && (
                          <span className={`px-2 py-1 rounded ${patient.vitals.hr > 100 ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-600'}`}>
                            ❤️ {patient.vitals.hr}
                          </span>
                        )}
                        {patient.vitals.spo2 && (
                          <span className={`px-2 py-1 rounded ${patient.vitals.spo2 < 95 ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'}`}>
                            O₂ {patient.vitals.spo2}%
                          </span>
                        )}
                      </div>
                    )}
                    {patient.ai_suggested_specialty && (
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${SPECIALTY_INFO[patient.ai_suggested_specialty]?.color || 'bg-gray-100 text-gray-800'}`}>
                        {SPECIALTY_INFO[patient.ai_suggested_specialty]?.icon} AI: {SPECIALTY_INFO[patient.ai_suggested_specialty]?.name}
                      </span>
                    )}
                    <button
                      onClick={(e) => { e.stopPropagation(); onSendToDoctor(patient); }}
                      className="px-3 py-1.5 bg-teal-600 text-white text-sm rounded-lg hover:bg-teal-700 whitespace-nowrap"
                    >
                      Send →
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Patient Detail */}
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
        <div className="bg-gray-800 px-6 py-4">
          <h2 className="text-lg font-semibold text-white">Patient Details</h2>
        </div>
        {selectedPatient ? (
          <div className="p-6 space-y-4">
            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-teal-100 flex items-center justify-center text-2xl mx-auto mb-3">
                {selectedPatient.first_name[0]}{selectedPatient.last_name[0]}
              </div>
              <h3 className="text-xl font-bold text-gray-900">
                {selectedPatient.first_name} {selectedPatient.last_name}
              </h3>
            </div>
            {selectedPatient.vitals && (
              <div className="bg-blue-50 rounded-xl p-4 grid grid-cols-2 gap-2">
                {selectedPatient.vitals.bp && (
                  <div className="bg-white rounded-lg p-2 text-center">
                    <div className="text-lg font-bold">{selectedPatient.vitals.bp}</div>
                    <div className="text-xs text-gray-500">BP</div>
                  </div>
                )}
                {selectedPatient.vitals.hr && (
                  <div className="bg-white rounded-lg p-2 text-center">
                    <div className="text-lg font-bold">{selectedPatient.vitals.hr}</div>
                    <div className="text-xs text-gray-500">HR</div>
                  </div>
                )}
                {selectedPatient.vitals.temp && (
                  <div className="bg-white rounded-lg p-2 text-center">
                    <div className="text-lg font-bold">{selectedPatient.vitals.temp}°C</div>
                    <div className="text-xs text-gray-500">Temp</div>
                  </div>
                )}
                {selectedPatient.vitals.spo2 && (
                  <div className="bg-white rounded-lg p-2 text-center">
                    <div className="text-lg font-bold">{selectedPatient.vitals.spo2}%</div>
                    <div className="text-xs text-gray-500">SpO2</div>
                  </div>
                )}
              </div>
            )}
            <button
              onClick={() => onSendToDoctor(selectedPatient)}
              className="w-full py-3 bg-teal-600 text-white rounded-xl font-semibold hover:bg-teal-700"
            >
              Send to Doctor →
            </button>
          </div>
        ) : (
          <div className="p-6 text-center text-gray-500">
            <div className="text-4xl mb-4">👆</div>
            <p>Select a patient to view details</p>
          </div>
        )}
      </div>
    </div>
  );
}

// All Patients Tab Component
function AllPatientsTab({
  patients,
  loading,
  onSendToDoctor,
  onRefresh,
}: {
  patients: Patient[];
  loading: boolean;
  onSendToDoctor: (p: Patient) => void;
  onRefresh: () => void;
}) {
  const [search, setSearch] = useState('');
  
  const filteredPatients = patients.filter(p => 
    `${p.first_name} ${p.last_name} ${p.name || ''}`.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
      <div className="bg-blue-600 px-6 py-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">All Patients</h2>
        <button
          onClick={onRefresh}
          className="bg-blue-500 px-3 py-1 rounded text-sm text-white hover:bg-blue-400"
        >
          🔄 Refresh
        </button>
      </div>
      
      <div className="p-4 border-b">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search patients..."
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
        />
      </div>

      {loading ? (
        <div className="p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-500">Loading patients...</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-100 max-h-[500px] overflow-y-auto">
          {filteredPatients.map((patient) => (
            <div key={patient.id} className="p-4 hover:bg-gray-50 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-semibold">
                  {patient.first_name?.[0] || patient.name?.[0] || '?'}
                </div>
                <div>
                  <div className="font-semibold text-gray-900">
                    {patient.first_name} {patient.last_name} {patient.name && !patient.first_name ? patient.name : ''}
                  </div>
                  <div className="text-sm text-gray-500">
                    {patient.age || '--'} years • {patient.gender || 'Unknown'}
                  </div>
                </div>
              </div>
              <button
                onClick={() => onSendToDoctor(patient)}
                className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 text-sm font-medium"
              >
                Send to Doctor →
              </button>
            </div>
          ))}
          {filteredPatients.length === 0 && (
            <div className="p-8 text-center text-gray-500">
              No patients found
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// My Referrals Tab Component
function MyReferralsTab({
  referrals,
  loading,
  onRefresh,
}: {
  referrals: Referral[];
  loading: boolean;
  onRefresh: () => void;
}) {
  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
      <div className="bg-indigo-600 px-6 py-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">My Referrals</h2>
        <button
          onClick={onRefresh}
          className="bg-indigo-500 px-3 py-1 rounded text-sm text-white hover:bg-indigo-400"
        >
          🔄 Refresh
        </button>
      </div>

      {loading ? (
        <div className="p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-2 text-gray-500">Loading referrals...</p>
        </div>
      ) : referrals.length === 0 ? (
        <div className="p-8 text-center text-gray-500">
          <div className="text-4xl mb-4">📋</div>
          <p>No referrals yet</p>
          <p className="text-sm">Send patients to doctors to see them here</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-100">
          {referrals.map((referral) => (
            <div key={referral.id} className="p-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-semibold text-gray-900">
                    {referral.patient?.name || 'Patient'}
                  </div>
                  <div className="text-sm text-gray-500">
                    → {SPECIALTY_INFO[referral.target_specialty]?.icon} {SPECIALTY_INFO[referral.target_specialty]?.name || referral.target_specialty}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[referral.status] || 'bg-gray-100'}`}>
                    {referral.status}
                  </span>
                  <span className="text-xs text-gray-400">
                    {referral.created_at ? new Date(referral.created_at).toLocaleDateString() : 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
