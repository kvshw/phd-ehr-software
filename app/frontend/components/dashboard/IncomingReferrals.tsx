'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/apiClient';
import { useRouter } from 'next/navigation';

interface Referral {
  id: string;
  patient_id: string;
  target_specialty: string;
  priority: string;
  status: string;
  chief_complaint?: string;
  symptoms?: string[];
  vitals?: Record<string, any>;
  triage_notes?: string;
  ai_suggested_specialty?: string;
  ai_confidence?: string;
  nurse_override: boolean;
  created_at: string;
  patient?: {
    id: string;
    name: string;
    age: number;
    gender?: string;
    mrn?: string;
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
};

const PRIORITY_COLORS = {
  critical: 'bg-red-500 text-white animate-pulse',
  urgent: 'bg-orange-500 text-white',
  standard: 'bg-yellow-500 text-white',
  non_urgent: 'bg-green-500 text-white',
};

export function IncomingReferrals({ specialty }: { specialty?: string }) {
  const router = useRouter();
  const [referrals, setReferrals] = useState<Referral[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReferral, setSelectedReferral] = useState<Referral | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchReferrals();
  }, [specialty]);

  const fetchReferrals = async () => {
    setLoading(true);
    try {
      const params = specialty ? `?specialty=${specialty}` : '';
      const response = await apiClient.get(`/referrals/doctor/queue${params}`);
      console.log('Referrals API response:', response.data); // Debug log
      console.log('Referrals data structure:', {
        hasData: !!response.data,
        hasReferrals: !!response.data?.referrals,
        isArray: Array.isArray(response.data?.referrals),
        count: response.data?.referrals?.length,
        firstReferral: response.data?.referrals?.[0],
      });
      // Ensure we have valid data structure
      if (response.data && Array.isArray(response.data.referrals)) {
        console.log(`Found ${response.data.referrals.length} referrals`); // Debug log
        // Validate and sanitize referral data
        const validReferrals = response.data.referrals.map((ref: any) => {
          const referral = {
            id: String(ref.id || ''),
            patient_id: String(ref.patient_id || ''),
            target_specialty: String(ref.target_specialty || ''),
            priority: String(ref.priority || 'standard'),
            status: String(ref.status || 'pending'),
            chief_complaint: ref.chief_complaint ? String(ref.chief_complaint) : undefined,
            symptoms: Array.isArray(ref.symptoms) ? ref.symptoms.map((s: any) => String(s)) : [],
            vitals: ref.vitals && typeof ref.vitals === 'object' ? ref.vitals : {},
            triage_notes: ref.triage_notes ? String(ref.triage_notes) : undefined,
            ai_suggested_specialty: ref.ai_suggested_specialty ? String(ref.ai_suggested_specialty) : undefined,
            ai_confidence: ref.ai_confidence ? (typeof ref.ai_confidence === 'string' ? ref.ai_confidence : String(ref.ai_confidence)) : undefined,
            nurse_override: typeof ref.nurse_override === 'boolean' ? ref.nurse_override : (ref.nurse_override === 'true' || ref.nurse_override === true),
            created_at: typeof ref.created_at === 'string' ? ref.created_at : new Date().toISOString(),
            patient: ref.patient ? {
              id: String(ref.patient.id || ''),
              name: String(ref.patient.name || 'Patient'),
              age: Number(ref.patient.age) || 0,
              gender: ref.patient.gender ? String(ref.patient.gender) : undefined,
              mrn: ref.patient.mrn ? String(ref.patient.mrn) : undefined,
            } : undefined,
          };
          
          // Debug log for AI data
          if (referral.ai_suggested_specialty) {
            console.log('Referral with AI data:', {
              id: referral.id,
              ai_suggested_specialty: referral.ai_suggested_specialty,
              ai_confidence: referral.ai_confidence,
              nurse_override: referral.nurse_override,
            });
          } else {
            console.log('Referral WITHOUT AI data:', {
              id: referral.id,
              target_specialty: referral.target_specialty,
            });
          }
          
          return referral;
        });
        setReferrals(validReferrals);
      } else {
        console.log('No referrals array in response, setting empty array');
        setReferrals([]);
      }
    } catch (error) {
      console.error('Error fetching referrals:', error);
      console.error('Error details:', error);
      // Only show demo data if there's an actual error, not if table is empty
      // Check if it's a table not found error
      const errorMsg = (error as any)?.response?.data?.detail || (error as any)?.message || '';
      if (errorMsg.includes('table does not exist') || errorMsg.includes('relation')) {
        console.log('Table does not exist - showing empty state');
        setReferrals([]);
      } else {
        // Demo data for other errors
        setReferrals([
          {
            id: '1',
            patient_id: 'p1',
            target_specialty: specialty || 'cardiology',
            priority: 'urgent',
            status: 'pending',
            chief_complaint: 'Chest pain, shortness of breath',
            symptoms: ['chest_pain', 'dyspnea'],
            vitals: { bp: '145/92', hr: 98, spo2: 94 },
            triage_notes: 'Patient reports sudden onset chest pain. History of hypertension.',
            ai_suggested_specialty: 'cardiology',
            ai_confidence: '0.92',
            nurse_override: false,
            created_at: new Date().toISOString(),
            patient: { id: 'p1', name: 'Maria Virtanen', age: 46, gender: 'Female' },
          },
          {
            id: '2',
            patient_id: 'p2',
            target_specialty: specialty || 'cardiology',
            priority: 'standard',
            status: 'accepted',
            chief_complaint: 'Palpitations, mild dizziness',
            symptoms: ['palpitations', 'dizziness'],
            vitals: { bp: '128/82', hr: 88, spo2: 98 },
            ai_suggested_specialty: 'cardiology',
            ai_confidence: '0.78',
            nurse_override: false,
            created_at: new Date(Date.now() - 3600000).toISOString(),
            patient: { id: 'p2', name: 'Mikko Lahtinen', age: 58, gender: 'Male' },
          },
        ]);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (referral: Referral) => {
    setActionLoading(true);
    try {
      await apiClient.put(`/referrals/${referral.id}/status`, {
        status: 'accepted',
        notes: 'Accepted for consultation',
      });
      setReferrals(prev => 
        prev.map(r => r.id === referral.id ? { ...r, status: 'accepted' } : r)
      );
    } catch (error) {
      console.error('Error accepting referral:', error);
      // Update locally for demo
      setReferrals(prev => 
        prev.map(r => r.id === referral.id ? { ...r, status: 'accepted' } : r)
      );
    } finally {
      setActionLoading(false);
    }
  };

  const handleComplete = async (referral: Referral) => {
    setActionLoading(true);
    try {
      await apiClient.put(`/referrals/${referral.id}/status`, {
        status: 'completed',
        notes: 'Consultation completed',
      });
      setReferrals(prev => prev.filter(r => r.id !== referral.id));
    } catch (error) {
      console.error('Error completing referral:', error);
      setReferrals(prev => prev.filter(r => r.id !== referral.id));
    } finally {
      setActionLoading(false);
    }
  };

  const handleViewPatient = (patientId: string) => {
    router.push(`/patients/${patientId}`);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-2 text-gray-500">Loading referrals...</p>
      </div>
    );
  }

  if (referrals.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6 text-center">
        <div className="text-4xl mb-4">📬</div>
        <h3 className="text-lg font-semibold text-gray-700">No Incoming Referrals</h3>
        <p className="text-gray-500 text-sm mt-2">
          New patient referrals from nurses will appear here
        </p>
        <div className="mt-4 p-3 bg-blue-50 rounded-lg text-left text-sm text-blue-800">
          <p className="font-medium mb-1">💡 To test referrals:</p>
          <ol className="list-decimal list-inside space-y-1 text-xs">
            <li>Login as a <strong>Nurse</strong> (or create a nurse account)</li>
            <li>Go to <strong>All Patients</strong> tab</li>
            <li>Select a patient and click <strong>"Send to Doctor"</strong></li>
            <li>Choose your specialty ({specialty || 'cardiology'})</li>
            <li>Return here to see the referral</li>
          </ol>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">📥</span>
          <h2 className="text-lg font-semibold text-white">Incoming Referrals</h2>
        </div>
        <span className="bg-white/20 px-3 py-1 rounded-full text-sm text-white">
          {referrals.filter(r => r.status === 'pending').length} pending
        </span>
      </div>

      <div className="divide-y divide-gray-100">
        {referrals.map((referral) => (
          <div
            key={referral.id}
            className={`p-4 hover:bg-gray-50 transition-colors ${
              selectedReferral?.id === referral.id ? 'bg-blue-50' : ''
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4">
                {/* Priority Badge */}
                <span className={`px-2 py-1 rounded text-xs font-bold ${
                  PRIORITY_COLORS[referral.priority as keyof typeof PRIORITY_COLORS] || 'bg-gray-500 text-white'
                }`}>
                  {referral.priority.replace('_', ' ').toUpperCase()}
                </span>
                
                {/* AI Prediction Badge */}
                {referral.ai_suggested_specialty && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs">🤖</span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      referral.nurse_override
                        ? 'bg-orange-100 text-orange-800 border border-orange-200'
                        : 'bg-green-100 text-green-800 border border-green-200'
                    }`}>
                      AI: {SPECIALTY_INFO[referral.ai_suggested_specialty]?.name || referral.ai_suggested_specialty}
                      {referral.ai_confidence && ` (${(parseFloat(referral.ai_confidence) * 100).toFixed(0)}%)`}
                      {referral.nurse_override && ' • Nurse Override'}
                    </span>
                  </div>
                )}

                {/* Patient Info */}
                <div>
                  <div className="font-semibold text-gray-900">
                    {referral.patient?.name || 'Patient'}
                  </div>
                  <div className="text-sm text-gray-500">
                    {referral.patient?.age} years • {referral.patient?.gender}
                  </div>
                  <div className="text-sm text-gray-700 mt-1">
                    {referral.chief_complaint}
                  </div>
                  {referral.triage_notes && (
                    <div className="text-xs text-gray-500 mt-1 italic">
                      Note: {referral.triage_notes}
                    </div>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex flex-col gap-2 items-end">
                <div className="flex items-center gap-2">
                  {referral.status === 'pending' ? (
                    <button
                      onClick={() => handleAccept(referral)}
                      disabled={actionLoading}
                      className="px-3 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 disabled:opacity-50"
                    >
                      ✓ Accept
                    </button>
                  ) : (
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                      Accepted
                    </span>
                  )}
                  <button
                    onClick={() => handleViewPatient(referral.patient_id)}
                    className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
                  >
                    View Patient
                  </button>
                  {referral.status === 'accepted' && (
                    <button
                      onClick={() => handleComplete(referral)}
                      disabled={actionLoading}
                      className="px-3 py-1.5 bg-gray-600 text-white text-sm rounded-lg hover:bg-gray-700 disabled:opacity-50"
                    >
                      Complete
                    </button>
                  )}
                </div>
                <span className="text-xs text-gray-400">
                  {new Date(referral.created_at).toLocaleTimeString()}
                </span>
              </div>
            </div>

            {/* Vitals Summary */}
            {referral.vitals && Object.keys(referral.vitals).length > 0 && (
              <div className="mt-3 flex gap-3">
                {referral.vitals.bp && (
                  <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                    BP: {referral.vitals.bp}
                  </span>
                )}
                {referral.vitals.hr && (
                  <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                    HR: {referral.vitals.hr}
                  </span>
                )}
                {referral.vitals.spo2 && (
                  <span className={`text-xs px-2 py-1 rounded ${
                    referral.vitals.spo2 < 95 ? 'bg-red-100 text-red-800' : 'bg-gray-100'
                  }`}>
                    SpO2: {referral.vitals.spo2}%
                  </span>
                )}
              </div>
            )}

            {/* AI Prediction Details */}
            {referral.ai_suggested_specialty && (
              <div className={`mt-3 p-3 rounded-lg border ${
                referral.nurse_override
                  ? 'bg-orange-50 border-orange-200'
                  : 'bg-blue-50 border-blue-200'
              }`}>
                <div className="flex items-start gap-2">
                  <span className="text-lg">🤖</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-semibold text-gray-700">AI Triage Prediction:</span>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        SPECIALTY_INFO[referral.ai_suggested_specialty]?.color || 'bg-gray-100 text-gray-800'
                      }`}>
                        {SPECIALTY_INFO[referral.ai_suggested_specialty]?.icon} {SPECIALTY_INFO[referral.ai_suggested_specialty]?.name || referral.ai_suggested_specialty}
                      </span>
                      {referral.ai_confidence && (
                        <span className="text-xs text-gray-600">
                          ({(parseFloat(referral.ai_confidence) * 100).toFixed(0)}% confidence)
                        </span>
                      )}
                    </div>
                    {referral.nurse_override && (
                      <div className="text-xs text-orange-700 mt-1">
                        ⚠️ <strong>Nurse Override:</strong> Nurse selected {SPECIALTY_INFO[referral.target_specialty]?.name || referral.target_specialty} instead of AI suggestion
                      </div>
                    )}
                    {!referral.nurse_override && (
                      <div className="text-xs text-green-700 mt-1">
                        ✓ Nurse accepted AI suggestion
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

