/**
 * User Profile Settings Page
 * Allows doctors to select their specialty and update profile
 */
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { TopHeader } from '@/components/layout/TopHeader';
import { apiClient } from '@/lib/apiClient';

// Medical specialties available in Finland
const MEDICAL_SPECIALTIES = [
  { id: 'general', name: 'General Practice', namefi: 'Yleislääketiede', icon: '🏥' },
  { id: 'internal', name: 'Internal Medicine', namefi: 'Sisätaudit', icon: '🫀' },
  { id: 'cardiology', name: 'Cardiology', namefi: 'Kardiologia', icon: '❤️' },
  { id: 'neurology', name: 'Neurology', namefi: 'Neurologia', icon: '🧠' },
  { id: 'psychiatry', name: 'Psychiatry', namefi: 'Psykiatria', icon: '🧘' },
  { id: 'pediatrics', name: 'Pediatrics', namefi: 'Lastentaudit', icon: '👶' },
  { id: 'geriatrics', name: 'Geriatrics', namefi: 'Geriatria', icon: '👴' },
  { id: 'surgery', name: 'Surgery', namefi: 'Kirurgia', icon: '🔪' },
  { id: 'orthopedics', name: 'Orthopedics', namefi: 'Ortopedia', icon: '🦴' },
  { id: 'oncology', name: 'Oncology', namefi: 'Onkologia', icon: '🎗️' },
  { id: 'pulmonology', name: 'Pulmonology', namefi: 'Keuhkosairaudet', icon: '🫁' },
  { id: 'gastroenterology', name: 'Gastroenterology', namefi: 'Gastroenterologia', icon: '🍽️' },
  { id: 'endocrinology', name: 'Endocrinology', namefi: 'Endokrinologia', icon: '⚗️' },
  { id: 'nephrology', name: 'Nephrology', namefi: 'Nefrologia', icon: '💧' },
  { id: 'dermatology', name: 'Dermatology', namefi: 'Ihotaudit', icon: '🧴' },
  { id: 'ophthalmology', name: 'Ophthalmology', namefi: 'Silmätaudit', icon: '👁️' },
  { id: 'radiology', name: 'Radiology', namefi: 'Radiologia', icon: '📷' },
  { id: 'anesthesiology', name: 'Anesthesiology', namefi: 'Anestesiologia', icon: '💉' },
  { id: 'emergency', name: 'Emergency Medicine', namefi: 'Ensihoito', icon: '🚑' },
  { id: 'nursing', name: 'Nursing', namefi: 'Hoitotyö', icon: '👩‍⚕️' },
];

export default function SettingsPage() {
  const { user, isAuthenticated, isLoading, checkAuth } = useAuthStore();
  const router = useRouter();
  
  const [formData, setFormData] = useState({
    specialty: '',
    first_name: '',
    last_name: '',
    title: '',
    department: '',
    primary_workplace: '',
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  // Load current user data into form
  useEffect(() => {
    if (user) {
      setFormData({
        specialty: user.specialty || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        title: user.title || '',
        department: user.department || '',
        primary_workplace: user.primary_workplace || '',
      });
    }
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      await apiClient.put('/auth/me', formData);
      
      // Refresh auth state to get updated user data
      await checkAuth();
      
      setMessage({ type: 'success', text: 'Profile updated successfully! Dashboard will adapt to your specialty.' });
    } catch (error: any) {
      console.error('Error updating profile:', error);
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to update profile' });
    } finally {
      setSaving(false);
    }
  };

  const handleSpecialtySelect = (specialtyId: string) => {
    setFormData(prev => ({ ...prev, specialty: specialtyId }));
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <TopHeader currentPage="Settings" />
      
      <main className="max-w-4xl mx-auto px-6 py-8">
        {/* Back Button */}
        <button
          onClick={() => router.push('/dashboard')}
          className="mb-6 flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span>Back to Dashboard</span>
        </button>

        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Profile Settings</h1>
          <p className="text-gray-600 mt-2">
            Update your profile and select your medical specialty. The dashboard will adapt based on your specialty.
          </p>
        </div>

        {/* Success/Error Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.type === 'success' 
              ? 'bg-green-50 border border-green-200 text-green-800'
              : 'bg-red-50 border border-red-200 text-red-800'
          }`}>
            <div className="flex items-center gap-2">
              <span>{message.type === 'success' ? '✅' : '❌'}</span>
              <span>{message.text}</span>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Specialty Selection */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span>🩺</span> Medical Specialty
            </h2>
            <p className="text-sm text-gray-600 mb-6">
              Select your primary specialty. This will customize your dashboard, prioritize relevant AI suggestions, and adapt the UI to your workflow.
            </p>
            
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {MEDICAL_SPECIALTIES.map((specialty) => (
                <button
                  key={specialty.id}
                  type="button"
                  onClick={() => handleSpecialtySelect(specialty.id)}
                  className={`p-4 rounded-xl border-2 text-left transition-all hover:shadow-md ${
                    formData.specialty === specialty.id
                      ? 'border-indigo-500 bg-indigo-50 ring-2 ring-indigo-200'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <div className="text-2xl mb-2">{specialty.icon}</div>
                  <div className="font-medium text-gray-900 text-sm">{specialty.name}</div>
                  <div className="text-xs text-gray-500">{specialty.namefi}</div>
                </button>
              ))}
            </div>

            {formData.specialty && (
              <div className="mt-4 p-3 bg-indigo-50 border border-indigo-200 rounded-lg">
                <p className="text-sm text-indigo-800">
                  <strong>Selected:</strong> {MEDICAL_SPECIALTIES.find(s => s.id === formData.specialty)?.name}
                  {' • '}
                  Dashboard will be customized for this specialty.
                </p>
              </div>
            )}
          </div>

          {/* Personal Information */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span>👤</span> Personal Information
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                <input
                  type="text"
                  value={formData.first_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, first_name: e.target.value }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Enter your first name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                <input
                  type="text"
                  value={formData.last_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, last_name: e.target.value }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Enter your last name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Professional Title</label>
                <select
                  value={formData.title}
                  onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">Select title</option>
                  <option value="Dr.">Dr. (Lääkäri)</option>
                  <option value="Prof.">Prof. (Professori)</option>
                  <option value="Nurse">Nurse (Sairaanhoitaja)</option>
                  <option value="Specialist">Specialist (Erikoislääkäri)</option>
                  <option value="Resident">Resident (Erikoistuva lääkäri)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
                <input
                  type="text"
                  value={formData.department}
                  onChange={(e) => setFormData(prev => ({ ...prev, department: e.target.value }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="e.g., Cardiology Unit"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Primary Workplace</label>
                <input
                  type="text"
                  value={formData.primary_workplace}
                  onChange={(e) => setFormData(prev => ({ ...prev, primary_workplace: e.target.value }))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="e.g., Helsinki University Hospital (HUS)"
                />
              </div>
            </div>
          </div>

          {/* Account Info (Read-only) */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span>🔐</span> Account Information
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  value={user?.email || ''}
                  disabled
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                <input
                  type="text"
                  value={user?.role || ''}
                  disabled
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-500 capitalize"
                />
              </div>
            </div>
          </div>

          {/* MAPE-K Adaptation Info */}
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl border border-indigo-200 p-6">
            <h2 className="text-lg font-semibold text-indigo-900 mb-2 flex items-center gap-2">
              <span>🔄</span> How Your Specialty Affects the UI
            </h2>
            <ul className="text-sm text-indigo-800 space-y-2">
              <li>• <strong>Dashboard Layout:</strong> Sections reordered based on specialty-typical workflow</li>
              <li>• <strong>AI Suggestions:</strong> Prioritized based on specialty relevance</li>
              <li>• <strong>Quick Actions:</strong> Customized for common specialty tasks</li>
              <li>• <strong>Lab Highlights:</strong> Key tests for your specialty emphasized</li>
              <li>• <strong>Risk Alerts:</strong> Specialty-specific risk factors highlighted</li>
            </ul>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end gap-4">
            <button
              type="button"
              onClick={() => router.push('/dashboard')}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors flex items-center gap-2"
            >
              {saving ? (
                <>
                  <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                  Saving...
                </>
              ) : (
                <>
                  <span>💾</span>
                  Save Changes
                </>
              )}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}

