/**
 * AI Suggestions Panel Component
 * Displays suggestion cards with explanations, relevance scores, and action buttons
 */
'use client';

import { useState, useEffect, useMemo } from 'react';
import { suggestionService, Suggestion } from '@/lib/suggestionService';
import { monitorService } from '@/lib/monitorService';
import { usePatientDetailStore } from '@/store/patientDetailStore';

interface SuggestionsPanelProps {
  patientId: string;
}

type SuggestionAction = 'accept' | 'ignore' | 'not_relevant';

export function SuggestionsPanel({ patientId }: SuggestionsPanelProps) {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [generatingAdaptation, setGeneratingAdaptation] = useState(false);
  const { suggestionDensity } = usePatientDetailStore();

  useEffect(() => {
    fetchSuggestions();
  }, [patientId]);

  // Filter suggestions based on density setting
  const filteredSuggestions = useMemo(() => {
    if (suggestionDensity === 'low') {
      // Show only high-confidence suggestions (>= 0.7)
      return suggestions.filter(s => (s.confidence ?? 0) >= 0.7);
    } else if (suggestionDensity === 'medium') {
      // Show suggestions with confidence >= 0.4
      return suggestions.filter(s => (s.confidence ?? 0) >= 0.4);
    } else {
      // 'high' - show all suggestions
      return suggestions;
    }
  }, [suggestions, suggestionDensity]);

  const fetchSuggestions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await suggestionService.getPatientSuggestions(patientId);
      setSuggestions(response.items);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load suggestions');
      console.error('Error fetching suggestions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateSuggestions = async () => {
    setGenerating(true);
    setActionLoading('generating');
    setError(null);
    try {
      // Generate suggestions via diagnosis helper
      await suggestionService.generateSuggestions(patientId);
      
      // Refresh suggestions list
      await fetchSuggestions();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate suggestions. Make sure AI model services are running.');
      console.error('Error generating suggestions:', err);
    } finally {
      setGenerating(false);
      setActionLoading(null);
    }
  };

  const handleAction = async (suggestionId: string, action: SuggestionAction) => {
    setActionLoading(suggestionId);
    try {
      // Find the suggestion to get its type and source
      const suggestion = suggestions.find((s) => s.id === suggestionId);
      
      // Log the action for MAPE-K monitoring
      await monitorService.logSuggestionAction({
        suggestionId,
        action,
        suggestionType: suggestion?.type,
        suggestionSource: suggestion?.source,
        patientId: patientId,
      });

      // Submit feedback with patient_id to ensure it's stored correctly
      await suggestionService.submitFeedback({
        suggestion_id: suggestionId,
        action,
        patient_id: patientId, // Explicitly include patient_id
      });

      console.log(`✅ Feedback submitted: ${action} for suggestion ${suggestionId}, patient ${patientId}`);

      // Remove suggestion from list after action
      setSuggestions((prev) => prev.filter((s) => s.id !== suggestionId));
    } catch (err: any) {
      console.error('❌ Error submitting feedback:', err);
      console.error('Error details:', {
        suggestionId,
        action,
        patientId,
        error: err.response?.data || err.message,
      });
      // Show user-friendly error message
      setError(`Failed to submit feedback: ${err.response?.data?.detail || err.message || 'Unknown error'}`);
      // Don't remove suggestion if feedback fails
    } finally {
      setActionLoading(null);
    }
  };

  // Format confidence score as percentage
  const formatConfidence = (confidence: number | null): string => {
    if (confidence === null) return 'N/A';
    return `${(confidence * 100).toFixed(0)}%`;
  };

  // Get confidence color
  const getConfidenceColor = (confidence: number | null): string => {
    if (confidence === null) return 'bg-gray-100 text-gray-800';
    if (confidence >= 0.7) return 'bg-green-100 text-green-800';
    if (confidence >= 0.4) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  // Get source badge color
  const getSourceColor = (source: string): string => {
    switch (source.toLowerCase()) {
      case 'vital_risk':
        return 'bg-blue-100 text-blue-800';
      case 'image_analysis':
        return 'bg-purple-100 text-purple-800';
      case 'diagnosis_helper':
        return 'bg-indigo-100 text-indigo-800';
      case 'rules':
        return 'bg-gray-100 text-gray-800';
      case 'ai_model':
        return 'bg-green-100 text-green-800';
      case 'hybrid':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading AI suggestions...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
        <button
          onClick={fetchSuggestions}
          className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-xl border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-indigo-100">
            <svg className="h-5 w-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900">AI Suggestions</h2>
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            Experimental
          </span>
        </div>
        <button
          onClick={handleGenerateSuggestions}
          disabled={loading || generating || actionLoading !== null}
          className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {generating ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Generating...
            </>
          ) : (
            <>
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Generate Suggestions
            </>
          )}
        </button>
      </div>

      {/* MAPE-K Testing: Generate Adaptation Button */}
      <div className="mb-6 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-blue-900">MAPE-K Adaptation Testing</p>
            <p className="text-xs text-blue-700 mt-1">Generate an adaptation plan based on your usage patterns</p>
          </div>
          <button
            onClick={async () => {
              setGeneratingAdaptation(true);
              try {
                const response = await fetch(`http://localhost:8000/api/v1/mape-k/plan?patient_id=${patientId}`, {
                  method: 'POST',
                  credentials: 'include',
                  headers: {
                    'Content-Type': 'application/json',
                  },
                });
                
                if (response.ok) {
                  const data = await response.json();
                  alert(`✅ Adaptation plan generated!\n\nExplanation: ${data.explanation}\n\nReloading page to apply changes...`);
                  setTimeout(() => window.location.reload(), 1000);
                } else {
                  const error = await response.json();
                  alert(`❌ Error: ${error.detail || 'Failed to generate plan. Make sure you have some navigation activity first.'}`);
                }
              } catch (err) {
                alert(`❌ Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
              } finally {
                setGeneratingAdaptation(false);
              }
            }}
            disabled={generatingAdaptation}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow"
          >
            {generatingAdaptation ? 'Generating...' : 'Generate Adaptation'}
          </button>
        </div>
      </div>

      {filteredSuggestions.length === 0 ? (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <p className="text-gray-500 mb-2">
            {suggestions.length === 0
              ? 'No AI suggestions available at this time.'
              : `No suggestions match the current density setting (${suggestionDensity}).`}
          </p>
          {suggestions.length > 0 && (
            <p className="text-sm text-gray-400">
              Showing only high-confidence suggestions. Adjust density setting to see more.
            </p>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredSuggestions.map((suggestion) => (
            <div
              key={suggestion.id}
              className="border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSourceColor(
                        suggestion.source
                      )}`}
                    >
                      {suggestion.source.replace('_', ' ').toUpperCase()}
                    </span>
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getConfidenceColor(
                        suggestion.confidence
                      )}`}
                    >
                      Confidence: {formatConfidence(suggestion.confidence)}
                    </span>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                      Experimental
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">{suggestion.text}</h3>
                </div>
              </div>

              {/* Explanation with enhanced explainability */}
              <div className="mb-4">
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <svg
                      className="w-4 h-4 text-indigo-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <span className="text-xs font-semibold text-gray-700">Explanation</span>
                    
                    {/* Evidence Level Badge */}
                    {(suggestion as any).evidence_level && (
                      <span className={`ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                        (suggestion as any).evidence_level === 'High' ? 'bg-green-100 text-green-800' :
                        (suggestion as any).evidence_level === 'Moderate' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        Evidence: {(suggestion as any).evidence_level}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">{suggestion.explanation}</p>
                  
                  {/* Evidence Details Section */}
                  {((suggestion as any).mechanism || (suggestion as any).citations?.length > 0 || (suggestion as any).guidelines?.length > 0) && (
                    <details className="mt-3 pt-3 border-t border-gray-200">
                      <summary className="text-xs font-semibold text-indigo-600 cursor-pointer hover:text-indigo-800">
                        📚 View Medical Evidence & Citations
                      </summary>
                      <div className="mt-3 space-y-3">
                        {/* Mechanism */}
                        {(suggestion as any).mechanism && (
                          <div>
                            <p className="text-xs font-semibold text-gray-700 mb-1">Pathophysiological Mechanism:</p>
                            <p className="text-xs text-gray-600">{(suggestion as any).mechanism}</p>
                          </div>
                        )}
                        
                        {/* Clinical Pearl */}
                        {(suggestion as any).clinical_pearl && (
                          <div className="bg-amber-50 border border-amber-200 rounded p-2">
                            <p className="text-xs font-semibold text-amber-800">💡 Clinical Pearl:</p>
                            <p className="text-xs text-amber-700">{(suggestion as any).clinical_pearl}</p>
                          </div>
                        )}
                        
                        {/* Guidelines */}
                        {(suggestion as any).guidelines?.length > 0 && (
                          <div>
                            <p className="text-xs font-semibold text-gray-700 mb-1">Clinical Guidelines:</p>
                            <ul className="text-xs text-gray-600 space-y-1">
                              {(suggestion as any).guidelines.map((g: any, i: number) => (
                                <li key={i} className="flex items-start gap-1">
                                  <span className="text-indigo-500">•</span>
                                  <span>
                                    <strong>{g.organization}</strong> ({g.year}): {g.title}
                                    {g.url && (
                                      <a href={g.url} target="_blank" rel="noopener noreferrer" className="ml-1 text-indigo-600 hover:underline">
                                        [Link]
                                      </a>
                                    )}
                                  </span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        
                        {/* Citations */}
                        {(suggestion as any).citations?.length > 0 && (
                          <div>
                            <p className="text-xs font-semibold text-gray-700 mb-1">Key References:</p>
                            <ul className="text-xs text-gray-600 space-y-1">
                              {(suggestion as any).citations.slice(0, 3).map((c: any, i: number) => (
                                <li key={i} className="flex items-start gap-1">
                                  <span className="text-indigo-500">{i + 1}.</span>
                                  <span>
                                    {c.authors} ({c.year}). {c.title}. <em>{c.journal}</em>.
                                    {c.pmid && (
                                      <a 
                                        href={`https://pubmed.ncbi.nlm.nih.gov/${c.pmid}/`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="ml-1 text-indigo-600 hover:underline"
                                      >
                                        PMID: {c.pmid}
                                      </a>
                                    )}
                                  </span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        
                        {/* Limitations */}
                        {(suggestion as any).limitations?.length > 0 && (
                          <div className="bg-red-50 border border-red-200 rounded p-2">
                            <p className="text-xs font-semibold text-red-800">⚠️ Important Limitations:</p>
                            <ul className="text-xs text-red-700 mt-1 space-y-0.5">
                              {(suggestion as any).limitations.map((l: string, i: number) => (
                                <li key={i}>• {l}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </details>
                  )}
                  
                  <div className="mt-2 pt-2 border-t border-gray-200">
                    <p className="text-xs text-gray-600">
                      <strong>Source:</strong> {suggestion.source.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                      {suggestion.confidence !== null && (
                        <>
                          {' • '}
                          <strong>Confidence:</strong> {(suggestion.confidence * 100).toFixed(0)}%
                        </>
                      )}
                      {(suggestion as any).recommendation_strength && (
                        <>
                          {' • '}
                          <strong>Recommendation:</strong> {(suggestion as any).recommendation_strength}
                        </>
                      )}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      This explanation is generated by the AI model to help you understand the
                      reasoning behind this suggestion. Evidence-based citations are provided for academic review.
                    </p>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-3 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handleAction(suggestion.id, 'accept')}
                  disabled={actionLoading === suggestion.id}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md text-sm font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {actionLoading === suggestion.id ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
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
                      Processing...
                    </span>
                  ) : (
                    'Accept'
                  )}
                </button>
                <button
                  onClick={() => handleAction(suggestion.id, 'ignore')}
                  disabled={actionLoading === suggestion.id}
                  className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Ignore
                </button>
                <button
                  onClick={() => handleAction(suggestion.id, 'not_relevant')}
                  disabled={actionLoading === suggestion.id}
                  className="flex-1 px-4 py-2 bg-red-100 text-red-700 rounded-md text-sm font-medium hover:bg-red-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Not Relevant
                </button>
              </div>

              {/* Footer */}
              <div className="mt-3 text-xs text-gray-500">
                Created: {new Date(suggestion.created_at).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Safety Notice */}
      <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex items-start gap-2">
          <svg
            className="w-5 h-5 text-yellow-600 mt-0.5"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          <div>
            <p className="text-sm font-medium text-yellow-800">
              Experimental AI Output - For Research Purposes Only
            </p>
            <p className="text-xs text-yellow-700 mt-1">
              All AI suggestions are experimental and should not be used as the sole basis for
              clinical decisions. Always verify with clinical judgment and standard protocols.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

