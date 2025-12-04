/**
 * Create New Patient Page
 * Allows clinicians and admins to create new synthetic patients
 */
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { patientService, PatientCreate } from '@/lib/patientService';
import { TopHeader } from '@/components/layout/TopHeader';

export default function NewPatientPage() {
  console.log('🟢 NewPatientPage component rendered');
  
  const router = useRouter();
  const { user, isAuthenticated, checkAuth, isLoading } = useAuthStore();
  const [formData, setFormData] = useState<PatientCreate>({
    name: '',
    age: 1,
    sex: 'M',
    primary_diagnosis: null,
    // Finnish fields
    henkilotunnus: null,
    kela_card_number: null,
    date_of_birth: null,
    kela_eligible: true,
    municipality_code: null,
    municipality_name: null,
    // Contact
    phone: null,
    email: null,
    address: null,
    postal_code: null,
    city: null,
    // Emergency contact
    emergency_contact_name: null,
    emergency_contact_phone: null,
    emergency_contact_relation: null,
  });
  const [showFinnishFields, setShowFinnishFields] = useState(false);
  const [showContactFields, setShowContactFields] = useState(false);
  const [errors, setErrors] = useState<Partial<Record<keyof PatientCreate, string>>>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // All hooks must be called before any conditional returns
  useEffect(() => {
    console.log('🟢 checkAuth called');
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    console.log('🟡 Auth state changed:', { isLoading, isAuthenticated, userRole: user?.role, hasUser: !!user });
    
    // Don't redirect while still loading - wait for auth to complete
    if (isLoading) {
      console.log('⏳ Still loading, waiting for auth to complete...');
      return;
    }

    // Wait a bit for state to settle after loading completes
    const timeoutId = setTimeout(() => {
      console.log('🟡 Timeout check - Auth state:', { isLoading, isAuthenticated, userRole: user?.role, hasUser: !!user });

      // Check authentication
      if (!isAuthenticated) {
        console.log('Not authenticated, redirecting to login');
        router.push('/login');
        return;
      }

      // Check user role - must have user object
      if (!user) {
        console.log('No user object after loading, redirecting to login');
        router.push('/login');
        return;
      }

      // Check if user has permission (clinician or admin)
      if (user.role !== 'clinician' && user.role !== 'admin') {
        console.log(`User role "${user.role}" is not allowed. Redirecting to dashboard.`);
        router.push('/dashboard');
        return;
      }

      console.log('User authenticated and authorized:', user.role);
    }, 100); // Small delay to let state settle

    return () => clearTimeout(timeoutId);
  }, [isAuthenticated, isLoading, user, router]);

  // Handle conditional rendering after all hooks
  if (isLoading) {
    console.log('⏳ Component is loading, showing spinner');
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    console.log('Not authenticated or no user:', { isAuthenticated, hasUser: !!user });
    return null;
  }

  // Check if user has permission (clinician or admin)
  if (user.role !== 'clinician' && user.role !== 'admin') {
    console.log(`User role "${user.role}" is not allowed. Showing nothing.`);
    return null;
  }

  console.log('Component ready to render form. User:', { role: user.role, email: user.email });

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof PatientCreate, string>> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (formData.age <= 0 || formData.age > 150) {
      newErrors.age = 'Age must be between 1 and 150';
    }

    if (!formData.sex || !['M', 'F', 'Other'].includes(formData.sex)) {
      newErrors.sex = 'Sex must be M, F, or Other';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    console.log('🔵 Form submit handler called');
    e.preventDefault();
    setError(null);

    console.log('🔵 Form data:', formData);
    console.log('🔵 Validating form...');

    // Validate form
    const isValid = validateForm();
    console.log('🔵 Form validation result:', isValid);
    console.log('🔵 Form errors:', errors);

    if (!isValid) {
      console.log('Form validation failed');
      setError('Please fix the errors in the form before submitting.');
      return;
    }

    console.log('Form validation passed');

    setSubmitting(true);

    try {
      // Prepare patient data - include all fields, removing empty strings
      const patientData: PatientCreate = {
        name: formData.name.trim(),
        age: formData.age,
        sex: formData.sex,
        primary_diagnosis: formData.primary_diagnosis?.trim() || null,
        // Finnish fields
        henkilotunnus: formData.henkilotunnus?.trim() || null,
        kela_card_number: formData.kela_card_number?.trim() || null,
        date_of_birth: formData.date_of_birth || null,
        kela_eligible: formData.kela_eligible ?? true,
        municipality_code: formData.municipality_code?.trim() || null,
        municipality_name: formData.municipality_name?.trim() || null,
        // Contact fields
        phone: formData.phone?.trim() || null,
        email: formData.email?.trim() || null,
        address: formData.address?.trim() || null,
        postal_code: formData.postal_code?.trim() || null,
        city: formData.city?.trim() || null,
        // Emergency contact
        emergency_contact_name: formData.emergency_contact_name?.trim() || null,
        emergency_contact_phone: formData.emergency_contact_phone?.trim() || null,
        emergency_contact_relation: formData.emergency_contact_relation?.trim() || null,
      };

      console.log('Creating patient with data:', patientData);
      const patient = await patientService.createPatient(patientData);
      console.log('Patient created successfully:', patient);

      // Redirect to patient detail page
      router.push(`/patients/${patient.id}`);
    } catch (err: any) {
      console.error('Full error object:', err);
      console.error('Error response:', err.response);
      console.error('Error response data:', err.response?.data);
      console.error('Error message:', err.message);
      
      let errorMessage = 'Failed to create patient. Please try again.';
      
      if (err.response?.status === 401) {
        errorMessage = 'Authentication required. Please log in again.';
      } else if (err.response?.status === 403) {
        errorMessage = 'You do not have permission to create patients. Only clinicians and admins can create patients.';
      } else if (err.response?.status === 422) {
        errorMessage = err.response?.data?.detail || 'Invalid form data. Please check your inputs.';
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  // Validate and auto-fill from henkilötunnus
  const handleHenkilotunnusChange = (value: string) => {
    setFormData((prev) => ({
      ...prev,
      henkilotunnus: value || null,
    }));
    
    // Clear henkilötunnus error
    if (errors.henkilotunnus) {
      setErrors((prev) => ({ ...prev, henkilotunnus: undefined }));
    }
    
    // If henkilötunnus is provided, try to extract info (client-side validation)
    // Note: Full validation happens on backend
    if (value && value.length >= 10) {
      // Basic format check: YYMMDD-XXXX or YYMMDD+XXXX or YYMMDDAXXXX
      const pattern = /^(\d{6})([-+A])(\d{3})([0-9A-Y])$/i;
      if (pattern.test(value.replace(/\s/g, ''))) {
        // Format looks valid, backend will do full validation
        // We could add client-side extraction here if needed
      }
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;
    
    // Handle checkbox
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({
        ...prev,
        [name]: checked,
      }));
      return;
    }
    
    // Special handling for henkilötunnus
    if (name === 'henkilotunnus') {
      handleHenkilotunnusChange(value);
      return;
    }
    
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'age' ? (value === '' ? 1 : parseInt(value) || 1) : (value || null),
    }));
    
    // Clear error for this field
    if (errors[name as keyof PatientCreate]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <TopHeader currentPage="Overview" />
      <div className="max-w-3xl mx-auto py-8 sm:px-6 lg:px-8">
        <div className="px-4 sm:px-0">
          {/* Header */}
          <div className="mb-8">
            <button
              onClick={() => router.back()}
              className="text-indigo-600 hover:text-indigo-800 mb-6 flex items-center gap-2 text-sm font-medium transition-colors"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
              Back to Dashboard
            </button>
            <div className="flex items-center gap-4">
              <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-indigo-100">
                <svg className="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Create New Patient</h1>
                <p className="mt-1 text-sm text-gray-600">
                  Add a new synthetic patient to the research system
                </p>
              </div>
            </div>
          </div>

          {/* Form */}
          <div className="bg-white shadow rounded-xl border border-gray-200 p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-start">
                    <svg className="h-5 w-5 text-red-400 mt-0.5 mr-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                    <p className="text-red-800 text-sm">{error}</p>
                  </div>
                </div>
              )}

              {/* Name */}
              <div>
                <label
                  htmlFor="name"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Patient Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className={`w-full px-4 py-3 border rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-gray-900 ${
                    errors.name ? 'border-red-300 bg-red-50' : 'border-gray-300 bg-white'
                  }`}
                  placeholder="Enter patient name"
                  required
                />
                {errors.name && (
                  <p className="mt-1 text-sm text-red-600">{errors.name}</p>
                )}
              </div>

              {/* Age and Sex Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Age */}
                <div>
                  <label
                    htmlFor="age"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Age <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    id="age"
                    name="age"
                    value={formData.age || ''}
                    onChange={handleChange}
                    min="1"
                    max="150"
                    className={`w-full px-4 py-3 border rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-gray-900 ${
                      errors.age ? 'border-red-300 bg-red-50' : 'border-gray-300 bg-white'
                    }`}
                    required
                    placeholder="Enter age"
                  />
                  {errors.age && (
                    <p className="mt-1 text-sm text-red-600">{errors.age}</p>
                  )}
                </div>

                {/* Sex */}
                <div>
                  <label
                    htmlFor="sex"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Sex <span className="text-red-500">*</span>
                  </label>
                  <select
                    id="sex"
                    name="sex"
                    value={formData.sex}
                    onChange={handleChange}
                    className={`w-full px-4 py-3 border rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-gray-900 ${
                      errors.sex ? 'border-red-300 bg-red-50' : 'border-gray-300 bg-white'
                    }`}
                    required
                  >
                    <option value="M">Male</option>
                    <option value="F">Female</option>
                    <option value="Other">Other</option>
                  </select>
                  {errors.sex && (
                    <p className="mt-1 text-sm text-red-600">{errors.sex}</p>
                  )}
                </div>
              </div>

              {/* Primary Diagnosis */}
              <div>
                <label
                  htmlFor="primary_diagnosis"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Primary Diagnosis (Optional)
                </label>
                <textarea
                  id="primary_diagnosis"
                  name="primary_diagnosis"
                  value={formData.primary_diagnosis || ''}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors resize-none text-gray-900 bg-white"
                  placeholder="Enter primary diagnosis (e.g., Post-operative recovery, Pneumonia, etc.)"
                />
                <p className="mt-1 text-xs text-gray-500">
                  This is synthetic data for research purposes only
                </p>
              </div>

              {/* Finnish Healthcare Fields Section */}
              <div className="pt-6 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => setShowFinnishFields(!showFinnishFields)}
                  className="flex items-center justify-between w-full text-left mb-4"
                >
                  <div className="flex items-center gap-2">
                    <svg className="h-5 w-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                    </svg>
                    <h3 className="text-lg font-semibold text-gray-900">Finnish Healthcare Information (Optional)</h3>
                  </div>
                  <svg
                    className={`h-5 w-5 text-gray-500 transition-transform ${showFinnishFields ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {showFinnishFields && (
                  <div className="space-y-6 pt-4">
                    {/* Henkilötunnus */}
                    <div>
                      <label
                        htmlFor="henkilotunnus"
                        className="block text-sm font-medium text-gray-700 mb-2"
                      >
                        Henkilötunnus (Finnish Personal ID)
                      </label>
                      <input
                        type="text"
                        id="henkilotunnus"
                        name="henkilotunnus"
                        value={formData.henkilotunnus || ''}
                        onChange={handleChange}
                        className={`w-full px-4 py-3 border rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-gray-900 ${
                          errors.henkilotunnus ? 'border-red-300 bg-red-50' : 'border-gray-300 bg-white'
                        }`}
                        placeholder="YYMMDD-XXXX (e.g., 120345-1234)"
                        maxLength={11}
                      />
                      {errors.henkilotunnus && (
                        <p className="mt-1 text-sm text-red-600">{errors.henkilotunnus}</p>
                      )}
                      <p className="mt-1 text-xs text-gray-500">
                        Format: YYMMDD-XXXX. Age, date of birth, and sex will be auto-filled if valid.
                      </p>
                    </div>

                    {/* Kela Card Number */}
                    <div>
                      <label
                        htmlFor="kela_card_number"
                        className="block text-sm font-medium text-gray-700 mb-2"
                      >
                        Kela Card Number
                      </label>
                      <input
                        type="text"
                        id="kela_card_number"
                        name="kela_card_number"
                        value={formData.kela_card_number || ''}
                        onChange={handleChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-gray-900 bg-white"
                        placeholder="Kela health insurance card number"
                      />
                    </div>

                    {/* Municipality */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label
                          htmlFor="municipality_code"
                          className="block text-sm font-medium text-gray-700 mb-2"
                        >
                          Municipality Code
                        </label>
                        <input
                          type="text"
                          id="municipality_code"
                          name="municipality_code"
                          value={formData.municipality_code || ''}
                          onChange={handleChange}
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-gray-900 bg-white"
                          placeholder="e.g., 091 (Helsinki)"
                          maxLength={10}
                        />
                      </div>
                      <div>
                        <label
                          htmlFor="municipality_name"
                          className="block text-sm font-medium text-gray-700 mb-2"
                        >
                          Municipality Name
                        </label>
                        <input
                          type="text"
                          id="municipality_name"
                          name="municipality_name"
                          value={formData.municipality_name || ''}
                          onChange={handleChange}
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-gray-900 bg-white"
                          placeholder="e.g., Helsinki"
                        />
                      </div>
                    </div>

                    {/* Kela Eligible */}
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="kela_eligible"
                        name="kela_eligible"
                        checked={formData.kela_eligible ?? true}
                        onChange={handleChange}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                      />
                      <label htmlFor="kela_eligible" className="ml-2 block text-sm text-gray-700">
                        Eligible for Kela benefits
                      </label>
                    </div>
                  </div>
                )}
              </div>

              {/* Contact Information Section */}
              <div className="pt-6 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => setShowContactFields(!showContactFields)}
                  className="flex items-center justify-between w-full text-left mb-4"
                >
                  <div className="flex items-center gap-2">
                    <svg className="h-5 w-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                    </svg>
                    <h3 className="text-lg font-semibold text-gray-900">Contact Information (Optional)</h3>
                  </div>
                  <svg
                    className={`h-5 w-5 text-gray-500 transition-transform ${showContactFields ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {showContactFields && (
                  <div className="space-y-6 pt-4">
                    {/* Phone and Email */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label
                          htmlFor="phone"
                          className="block text-sm font-medium text-gray-700 mb-2"
                        >
                          Phone Number
                        </label>
                        <input
                          type="tel"
                          id="phone"
                          name="phone"
                          value={formData.phone || ''}
                          onChange={handleChange}
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-gray-900 bg-white"
                          placeholder="+358 50 123 4567"
                        />
                      </div>
                      <div>
                        <label
                          htmlFor="email"
                          className="block text-sm font-medium text-gray-700 mb-2"
                        >
                          Email Address
                        </label>
                        <input
                          type="email"
                          id="email"
                          name="email"
                          value={formData.email || ''}
                          onChange={handleChange}
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-gray-900 bg-white"
                          placeholder="patient@example.com"
                        />
                      </div>
                    </div>

                    {/* Address */}
                    <div>
                      <label
                        htmlFor="address"
                        className="block text-sm font-medium text-gray-700 mb-2"
                      >
                        Street Address
                      </label>
                      <input
                        type="text"
                        id="address"
                        name="address"
                        value={formData.address || ''}
                        onChange={handleChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-gray-900 bg-white"
                        placeholder="Street address"
                      />
                    </div>

                    {/* Postal Code and City */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label
                          htmlFor="postal_code"
                          className="block text-sm font-medium text-gray-700 mb-2"
                        >
                          Postal Code
                        </label>
                        <input
                          type="text"
                          id="postal_code"
                          name="postal_code"
                          value={formData.postal_code || ''}
                          onChange={handleChange}
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-gray-900 bg-white"
                          placeholder="00100"
                          maxLength={10}
                        />
                      </div>
                      <div>
                        <label
                          htmlFor="city"
                          className="block text-sm font-medium text-gray-700 mb-2"
                        >
                          City
                        </label>
                        <input
                          type="text"
                          id="city"
                          name="city"
                          value={formData.city || ''}
                          onChange={handleChange}
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-gray-900 bg-white"
                          placeholder="Helsinki"
                        />
                      </div>
                    </div>

                    {/* Emergency Contact */}
                    <div className="pt-4 border-t border-gray-200">
                      <h4 className="text-sm font-semibold text-gray-900 mb-4">Emergency Contact</h4>
                      <div className="space-y-4">
                        <div>
                          <label
                            htmlFor="emergency_contact_name"
                            className="block text-sm font-medium text-gray-700 mb-2"
                          >
                            Emergency Contact Name
                          </label>
                          <input
                            type="text"
                            id="emergency_contact_name"
                            name="emergency_contact_name"
                            value={formData.emergency_contact_name || ''}
                            onChange={handleChange}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-gray-900 bg-white"
                            placeholder="Full name"
                          />
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div>
                            <label
                              htmlFor="emergency_contact_phone"
                              className="block text-sm font-medium text-gray-700 mb-2"
                            >
                              Emergency Contact Phone
                            </label>
                            <input
                              type="tel"
                              id="emergency_contact_phone"
                              name="emergency_contact_phone"
                              value={formData.emergency_contact_phone || ''}
                              onChange={handleChange}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-gray-900 bg-white"
                              placeholder="+358 50 123 4567"
                            />
                          </div>
                          <div>
                            <label
                              htmlFor="emergency_contact_relation"
                              className="block text-sm font-medium text-gray-700 mb-2"
                            >
                              Relation
                            </label>
                            <input
                              type="text"
                              id="emergency_contact_relation"
                              name="emergency_contact_relation"
                              value={formData.emergency_contact_relation || ''}
                              onChange={handleChange}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-gray-900 bg-white"
                              placeholder="e.g., Spouse, Parent, Sibling"
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Submit Buttons */}
              <div className="flex items-center justify-end gap-4 pt-6 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => router.back()}
                  className="px-5 py-2.5 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-all font-medium"
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-6 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium shadow flex items-center gap-2 transform hover:scale-105 active:scale-95"
                >
                  {submitting ? (
                    <>
                      <svg
                        className="animate-spin h-4 w-4"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        />
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        />
                      </svg>
                      Creating...
                    </>
                  ) : (
                    'Create Patient'
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Info Box */}
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-xl p-5">
            <div className="flex items-start gap-2">
              <svg
                className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                  clipRule="evenodd"
                />
              </svg>
              <div>
                <p className="text-sm font-medium text-blue-800">
                  Synthetic Data Only
                </p>
                <p className="text-xs text-blue-700 mt-1">
                  All patient data in this system is synthetic and for research
                  purposes only. No real patient information should be entered.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

