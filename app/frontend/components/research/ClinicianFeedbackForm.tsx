'use client';

/**
 * Clinician Feedback Form Component
 * 
 * Collects structured feedback from clinicians for PhD research.
 * Includes:
 * - Likert scale ratings
 * - Clinical relevance assessment
 * - Usability ratings
 * - Free-text comments
 */

import { useState } from 'react';
import { apiClient } from '@/lib/apiClient';

interface FeedbackFormProps {
  suggestionId: string;
  suggestionText: string;
  patientId: string;
  onSubmit?: () => void;
  onCancel?: () => void;
}

interface FeedbackData {
  suggestion_id: string;
  patient_id: string;
  
  // Clinical Assessment (1-5 Likert scale)
  clinical_relevance: number;
  would_act_on: number;
  agreement_with_ai: number;
  explanation_quality: number;
  evidence_usefulness: number;
  
  // Usability (1-5 Likert scale)
  ease_of_understanding: number;
  time_saved: number;
  cognitive_load_reduction: number;
  
  // Free text
  comments: string;
  improvement_suggestions: string;
  
  // Metadata
  time_spent_reviewing_seconds: number;
}

const LIKERT_OPTIONS = [
  { value: 1, label: 'Strongly Disagree', color: 'bg-red-100 border-red-300 text-red-800' },
  { value: 2, label: 'Disagree', color: 'bg-orange-100 border-orange-300 text-orange-800' },
  { value: 3, label: 'Neutral', color: 'bg-gray-100 border-gray-300 text-gray-800' },
  { value: 4, label: 'Agree', color: 'bg-green-100 border-green-300 text-green-800' },
  { value: 5, label: 'Strongly Agree', color: 'bg-emerald-100 border-emerald-300 text-emerald-800' },
];

export function ClinicianFeedbackForm({
  suggestionId,
  suggestionText,
  patientId,
  onSubmit,
  onCancel,
}: FeedbackFormProps) {
  const [startTime] = useState(Date.now());
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  
  const [feedback, setFeedback] = useState<Partial<FeedbackData>>({
    suggestion_id: suggestionId,
    patient_id: patientId,
    clinical_relevance: 0,
    would_act_on: 0,
    agreement_with_ai: 0,
    explanation_quality: 0,
    evidence_usefulness: 0,
    ease_of_understanding: 0,
    time_saved: 0,
    cognitive_load_reduction: 0,
    comments: '',
    improvement_suggestions: '',
  });

  const updateRating = (field: keyof FeedbackData, value: number) => {
    setFeedback((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const timeSpent = Math.round((Date.now() - startTime) / 1000);
      const feedbackData: FeedbackData = {
        ...(feedback as FeedbackData),
        time_spent_reviewing_seconds: timeSpent,
      };

      // Submit to backend
      await apiClient.post('/research/feedback', feedbackData);
      
      setSubmitted(true);
      onSubmit?.();
    } catch (error) {
      console.error('Error submitting feedback:', error);
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
        <div className="text-green-600 text-4xl mb-3">✓</div>
        <h3 className="text-lg font-semibold text-green-800 mb-2">Thank You!</h3>
        <p className="text-green-700 text-sm">
          Your feedback has been recorded and will help improve the AI system.
        </p>
      </div>
    );
  }

  const LikertScale = ({
    label,
    description,
    field,
    value,
  }: {
    label: string;
    description: string;
    field: keyof FeedbackData;
    value: number;
  }) => (
    <div className="mb-6">
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <p className="text-xs text-gray-500 mb-3">{description}</p>
      <div className="flex gap-2">
        {LIKERT_OPTIONS.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => updateRating(field, option.value)}
            className={`flex-1 py-2 px-3 rounded-lg border-2 text-xs font-medium transition-all ${
              value === option.value
                ? option.color + ' ring-2 ring-offset-1 ring-indigo-500'
                : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
          >
            <div className="text-center">
              <div className="text-lg mb-1">{option.value}</div>
              <div className="hidden sm:block">{option.label}</div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-lg p-6 max-w-2xl">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-2">
          📋 Clinician Feedback Form
        </h2>
        <p className="text-sm text-gray-600">
          Your feedback helps improve AI suggestions for clinical decision support.
          This data is used for research purposes only.
        </p>
      </div>

      {/* Suggestion Being Evaluated */}
      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4 mb-6">
        <p className="text-xs font-semibold text-indigo-700 mb-1">Evaluating Suggestion:</p>
        <p className="text-sm text-indigo-900">{suggestionText}</p>
      </div>

      <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
        {/* Section 1: Clinical Assessment */}
        <div className="mb-8">
          <h3 className="text-md font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">
            📊 Clinical Assessment
          </h3>

          <LikertScale
            label="Clinical Relevance"
            description="This suggestion is clinically relevant to the patient's condition."
            field="clinical_relevance"
            value={feedback.clinical_relevance || 0}
          />

          <LikertScale
            label="Actionability"
            description="I would consider acting on this suggestion in clinical practice."
            field="would_act_on"
            value={feedback.would_act_on || 0}
          />

          <LikertScale
            label="Agreement with AI"
            description="I agree with the AI's reasoning and conclusion."
            field="agreement_with_ai"
            value={feedback.agreement_with_ai || 0}
          />

          <LikertScale
            label="Explanation Quality"
            description="The explanation helped me understand why this suggestion was made."
            field="explanation_quality"
            value={feedback.explanation_quality || 0}
          />

          <LikertScale
            label="Evidence Usefulness"
            description="The citations and clinical guidelines provided were helpful."
            field="evidence_usefulness"
            value={feedback.evidence_usefulness || 0}
          />
        </div>

        {/* Section 2: Usability */}
        <div className="mb-8">
          <h3 className="text-md font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">
            ⚙️ Usability Assessment
          </h3>

          <LikertScale
            label="Ease of Understanding"
            description="The suggestion and its explanation were easy to understand."
            field="ease_of_understanding"
            value={feedback.ease_of_understanding || 0}
          />

          <LikertScale
            label="Time Efficiency"
            description="This AI suggestion saved me time in clinical decision-making."
            field="time_saved"
            value={feedback.time_saved || 0}
          />

          <LikertScale
            label="Cognitive Load"
            description="The AI assistance reduced my mental effort in evaluating this case."
            field="cognitive_load_reduction"
            value={feedback.cognitive_load_reduction || 0}
          />
        </div>

        {/* Section 3: Free Text */}
        <div className="mb-8">
          <h3 className="text-md font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200">
            💬 Additional Comments
          </h3>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              General Comments (Optional)
            </label>
            <textarea
              value={feedback.comments}
              onChange={(e) => setFeedback((prev) => ({ ...prev, comments: e.target.value }))}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              placeholder="Any additional thoughts about this suggestion..."
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Improvement Suggestions (Optional)
            </label>
            <textarea
              value={feedback.improvement_suggestions}
              onChange={(e) =>
                setFeedback((prev) => ({ ...prev, improvement_suggestions: e.target.value }))
              }
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              placeholder="How could this AI suggestion be improved?"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors font-medium"
          >
            {submitting ? 'Submitting...' : 'Submit Feedback'}
          </button>
        </div>

        {/* Research Notice */}
        <p className="mt-4 text-xs text-gray-500 text-center">
          🔬 This feedback is collected for academic research purposes.
          All data is anonymized and stored securely.
        </p>
      </form>
    </div>
  );
}

