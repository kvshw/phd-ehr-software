/**
 * Conversation Summary Component
 * Displays AI-generated summary, key points, and recommendations
 */
'use client';

import { useState, useEffect } from 'react';
import { conversationService, ConversationAnalysis } from '@/lib/conversationService';

interface ConversationSummaryProps {
  sessionId: string;
}

export function ConversationSummary({ sessionId }: ConversationSummaryProps) {
  const [analysis, setAnalysis] = useState<ConversationAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [regenerating, setRegenerating] = useState(false);

  useEffect(() => {
    fetchAnalysis();
  }, [sessionId]);

  const fetchAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const session = await conversationService.getSession(sessionId);
      if (session.analysis) {
        setAnalysis(session.analysis);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load analysis');
      console.error('Error fetching analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  const regenerateAnalysis = async () => {
    setRegenerating(true);
    setError(null);
    try {
      const newAnalysis = await conversationService.analyzeSession(sessionId, true);
      setAnalysis(newAnalysis);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to regenerate analysis');
      console.error('Error regenerating analysis:', err);
    } finally {
      setRegenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow border border-gray-200 p-6">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      </div>
    );
  }

  if (error && !analysis) {
    return (
      <div className="bg-white rounded-xl shadow border border-gray-200 p-6">
        <div className="text-red-600 mb-4">{error}</div>
        <button
          onClick={regenerateAnalysis}
          disabled={regenerating}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
        >
          {regenerating ? 'Generating...' : 'Generate Analysis'}
        </button>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="bg-white rounded-xl shadow border border-gray-200 p-6">
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">No analysis available yet</p>
          <button
            onClick={regenerateAnalysis}
            disabled={regenerating}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          >
            {regenerating ? 'Generating...' : 'Generate Analysis'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-indigo-100">
            <svg className="h-5 w-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900">Conversation Analysis</h2>
        </div>
        <button
          onClick={regenerateAnalysis}
          disabled={regenerating}
          className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
        >
          {regenerating ? 'Regenerating...' : 'Regenerate'}
        </button>
      </div>

      {/* Summary */}
      {analysis.summary && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Summary</h3>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{analysis.summary}</p>
          </div>
        </div>
      )}

      {/* Key Points */}
      {analysis.key_points && analysis.key_points.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Key Points</h3>
          <ul className="space-y-2">
            {analysis.key_points.map((point, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-indigo-600 mt-1">•</span>
                <span className="text-sm text-gray-700">{point}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Patient Concerns */}
      {analysis.concerns_identified && analysis.concerns_identified.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Patient Concerns</h3>
          <div className="space-y-2">
            {analysis.concerns_identified.map((concern, index) => (
              <div key={index} className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <p className="text-sm text-gray-700">{concern}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Medical Terms */}
      {analysis.medical_terms && analysis.medical_terms.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Medical Terms Identified</h3>
          <div className="flex flex-wrap gap-2">
            {analysis.medical_terms.map((term, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full"
              >
                {term}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {analysis.recommendations && (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Recommendations</h3>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-sm text-gray-700">{analysis.recommendations}</p>
          </div>
        </div>
      )}
    </div>
  );
}

