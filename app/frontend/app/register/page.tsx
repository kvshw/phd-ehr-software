'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiClient } from '@/lib/apiClient';

// Medical specialties for doctors
const MEDICAL_SPECIALTIES = [
  { id: 'cardiology', name: 'Cardiology' },
  { id: 'neurology', name: 'Neurology' },
  { id: 'orthopedics', name: 'Orthopedics' },
  { id: 'pediatrics', name: 'Pediatrics' },
  { id: 'psychiatry', name: 'Psychiatry' },
  { id: 'emergency', name: 'Emergency Medicine' },
  { id: 'internal', name: 'Internal Medicine' },
  { id: 'surgery', name: 'Surgery' },
  { id: 'dermatology', name: 'Dermatology' },
  { id: 'oncology', name: 'Oncology' },
  { id: 'general', name: 'General Practice' },
];

// Nursing departments
const NURSING_DEPARTMENTS = [
  { id: 'emergency_triage', name: 'Emergency Triage' },
  { id: 'inpatient', name: 'Inpatient Care' },
  { id: 'outpatient', name: 'Outpatient Clinic' },
  { id: 'icu', name: 'Intensive Care Unit' },
  { id: 'pediatric_nursing', name: 'Pediatric Nursing' },
  { id: 'surgical', name: 'Surgical Nursing' },
  { id: 'oncology_nursing', name: 'Oncology Nursing' },
  { id: 'mental_health', name: 'Mental Health' },
];

type ClinicalRole = 'doctor' | 'nurse';

export default function RegisterPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Form data
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    clinicalRole: '' as ClinicalRole | '',
    specialty: '',
    department: '',
    firstName: '',
    lastName: '',
    title: '',
    licenseNumber: '',
    hetiNumber: '',
    primaryWorkplace: '',
  });

  const handleRoleSelect = (role: ClinicalRole) => {
    setFormData({ ...formData, clinicalRole: role, specialty: '', department: '' });
    setStep(2);
  };

  const handleSpecialtySelect = (specialty: string) => {
    setFormData({ ...formData, specialty });
    setStep(3);
  };

  const handleDepartmentSelect = (department: string) => {
    setFormData({ ...formData, department });
    setStep(3);
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setIsLoading(true);

    try {
      // Submit registration
      await apiClient.post('/auth/register-request', {
        email: formData.email,
        password: formData.password,
        role: formData.clinicalRole === 'doctor' ? 'clinician' : 'nurse',
        specialty: formData.clinicalRole === 'doctor' ? formData.specialty : null,
        department: formData.clinicalRole === 'nurse' ? formData.department : null,
        first_name: formData.firstName,
        last_name: formData.lastName,
        title: formData.clinicalRole === 'doctor' ? 'Dr.' : formData.title || 'RN',
        license_number: formData.licenseNumber,
        heti_number: formData.hetiNumber,
        primary_workplace: formData.primaryWorkplace,
      });

      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-blue-50 py-12 px-4">
        <div className="max-w-md w-full text-center space-y-6 bg-white rounded-2xl shadow-xl p-8">
          <div className="mx-auto flex items-center justify-center h-20 w-20 rounded-full bg-green-100">
            <svg className="h-10 w-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900">Registration Submitted!</h2>
          <p className="text-gray-600">
            Your account request has been submitted for review. An administrator will review and approve your account shortly.
          </p>
          <p className="text-sm text-gray-500">
            You will receive an email notification once your account is approved.
          </p>
          <Link
            href="/login"
            className="inline-block mt-4 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Back to Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-2xl w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-indigo-100 mb-4">
            <svg className="h-8 w-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-gray-900">Create Your Account</h2>
          <p className="mt-2 text-gray-600">Join the EHR Research Platform</p>
        </div>

        {/* Progress Steps */}
        <div className="flex justify-center space-x-4">
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className={`flex items-center justify-center h-10 w-10 rounded-full font-semibold ${
                step >= s ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500'
              }`}
            >
              {s}
            </div>
          ))}
        </div>

        {/* Step 1: Role Selection */}
        {step === 1 && (
          <div className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
            <h3 className="text-xl font-semibold text-gray-900 text-center">What is your role?</h3>
            
            <div className="grid grid-cols-2 gap-6">
              <button
                type="button"
                onClick={() => handleRoleSelect('doctor')}
                className="p-8 border-2 border-gray-200 rounded-2xl hover:border-indigo-500 hover:bg-indigo-50 transition-all group text-center"
              >
                <div className="h-16 w-16 mx-auto mb-4 rounded-full bg-indigo-100 flex items-center justify-center">
                  <svg className="h-8 w-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <h4 className="text-xl font-semibold text-gray-900 group-hover:text-indigo-600">Doctor</h4>
                <p className="text-sm text-gray-500 mt-2">
                  Physician, Specialist, or General Practitioner
                </p>
              </button>

              <button
                type="button"
                onClick={() => handleRoleSelect('nurse')}
                className="p-8 border-2 border-gray-200 rounded-2xl hover:border-teal-500 hover:bg-teal-50 transition-all group text-center"
              >
                <div className="h-16 w-16 mx-auto mb-4 rounded-full bg-teal-100 flex items-center justify-center">
                  <svg className="h-8 w-8 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </div>
                <h4 className="text-xl font-semibold text-gray-900 group-hover:text-teal-600">Nurse</h4>
                <p className="text-sm text-gray-500 mt-2">
                  RN, LPN, Nurse Practitioner, or Care Coordinator
                </p>
              </button>
            </div>

            <div className="text-center pt-4">
              <Link href="/login" className="text-sm text-indigo-600 hover:underline">
                Already have an account? Sign in
              </Link>
            </div>
          </div>
        )}

        {/* Step 2: Specialty/Department Selection */}
        {step === 2 && (
          <div className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
            <button
              type="button"
              onClick={() => setStep(1)}
              className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
            >
              ← Back to role selection
            </button>

            <h3 className="text-xl font-semibold text-gray-900 text-center">
              {formData.clinicalRole === 'doctor' ? 'Select Your Specialty' : 'Select Your Department'}
            </h3>

            {formData.clinicalRole === 'doctor' ? (
              <div className="grid grid-cols-3 gap-4">
                {MEDICAL_SPECIALTIES.map((spec) => (
                  <button
                    key={spec.id}
                    type="button"
                    onClick={() => handleSpecialtySelect(spec.id)}
                    className={`p-4 border-2 rounded-xl hover:border-indigo-500 hover:bg-indigo-50 transition-all text-center ${
                      formData.specialty === spec.id ? 'border-indigo-500 bg-indigo-50' : 'border-gray-200'
                    }`}
                  >
                    <div className="text-sm font-medium text-gray-900">{spec.name}</div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                {NURSING_DEPARTMENTS.map((dept) => (
                  <button
                    key={dept.id}
                    type="button"
                    onClick={() => handleDepartmentSelect(dept.id)}
                    className={`p-4 border-2 rounded-xl hover:border-teal-500 hover:bg-teal-50 transition-all text-left ${
                      formData.department === dept.id ? 'border-teal-500 bg-teal-50' : 'border-gray-200'
                    }`}
                  >
                    <div className="text-sm font-medium text-gray-900">{dept.name}</div>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Step 3: Account Details */}
        {step === 3 && (
          <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
            <button
              type="button"
              onClick={() => setStep(2)}
              className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
            >
              ← Back
            </button>

            <h3 className="text-xl font-semibold text-gray-900">Account Details</h3>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">First Name *</label>
                <input
                  type="text"
                  required
                  value={formData.firstName}
                  onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                  placeholder="John"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Last Name *</label>
                <input
                  type="text"
                  required
                  value={formData.lastName}
                  onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                  placeholder="Smith"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email Address *</label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                placeholder="john.smith@hospital.fi"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Password *</label>
                <input
                  type="password"
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                  placeholder="••••••••"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Confirm Password *</label>
                <input
                  type="password"
                  required
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                  placeholder="••••••••"
                />
              </div>
            </div>

            {formData.clinicalRole === 'nurse' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <select
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                >
                  <option value="RN">Registered Nurse (RN)</option>
                  <option value="LPN">Licensed Practical Nurse (LPN)</option>
                  <option value="NP">Nurse Practitioner (NP)</option>
                  <option value="CNA">Certified Nursing Assistant (CNA)</option>
                </select>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">License Number</label>
                <input
                  type="text"
                  value={formData.licenseNumber}
                  onChange={(e) => setFormData({ ...formData, licenseNumber: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                  placeholder="FI-12345"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">HETI Number</label>
                <input
                  type="text"
                  value={formData.hetiNumber}
                  onChange={(e) => setFormData({ ...formData, hetiNumber: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                  placeholder="Optional"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Primary Workplace</label>
              <input
                type="text"
                value={formData.primaryWorkplace}
                onChange={(e) => setFormData({ ...formData, primaryWorkplace: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 bg-white"
                placeholder="Helsinki University Hospital"
              />
            </div>

            {error && (
              <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-red-700 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className={`w-full py-4 px-6 rounded-xl font-semibold text-white transition-all ${
                isLoading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : formData.clinicalRole === 'doctor'
                  ? 'bg-indigo-600 hover:bg-indigo-700'
                  : 'bg-teal-600 hover:bg-teal-700'
              }`}
            >
              {isLoading ? 'Submitting...' : 'Create Account'}
            </button>

            <p className="text-center text-xs text-gray-500">
              By creating an account, you agree to our Terms of Service and Privacy Policy.
              Your account will require admin approval before access is granted.
            </p>
          </form>
        )}
      </div>
    </div>
  );
}

