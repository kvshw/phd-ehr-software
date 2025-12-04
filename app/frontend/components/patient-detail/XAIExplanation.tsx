'use client';

import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { xaiService, XAIExplanation as XAIExplanationType, QuickXAIResponse, DecisionFactors } from '@/lib/xaiService';

interface XAIExplanationProps {
  suggestionId: string;
  suggestionText: string;
  confidence: number;
  onClose?: () => void;
}

export function XAIExplanation({ suggestionId, suggestionText, confidence, onClose }: XAIExplanationProps) {
  const [explanation, setExplanation] = useState<XAIExplanationType | null>(null);
  const [quickExplanation, setQuickExplanation] = useState<QuickXAIResponse | null>(null);
  const [decisionFactors, setDecisionFactors] = useState<DecisionFactors | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [showFullExplanation, setShowFullExplanation] = useState(false);

  useEffect(() => {
    const fetchExplanations = async () => {
      setLoading(true);
      setError(null);
      try {
        // Fetch quick explanation first for immediate display
        const quickData = await xaiService.getQuickExplanation(suggestionId);
        setQuickExplanation(quickData);

        // Fetch decision factors
        const factorsData = await xaiService.getDecisionFactors(suggestionId);
        setDecisionFactors(factorsData);

        // Fetch full explanation in background
        const fullData = await xaiService.getExplanation(suggestionId);
        setExplanation(fullData);
      } catch (err) {
        console.error('[ERROR] Failed to fetch XAI explanation:', err);
        setError('Failed to load AI explanation. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchExplanations();
  }, [suggestionId]);

  const getDirectionColor = (direction: string) => {
    switch (direction) {
      case 'positive':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'negative':
        return 'bg-green-100 text-green-800 border-green-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'High':
        return 'text-red-600';
      case 'Moderate':
        return 'text-yellow-600';
      default:
        return 'text-gray-600';
    }
  };

  const getBarColor = (importance: number, direction: string) => {
    if (direction === 'positive') {
      return importance > 0.7 ? '#ef4444' : importance > 0.4 ? '#f97316' : '#fbbf24';
    }
    return importance > 0.7 ? '#22c55e' : importance > 0.4 ? '#84cc16' : '#a3e635';
  };

  if (loading) {
    return (
      <div className="mt-4 border border-blue-200 rounded-lg bg-blue-50">
        <div className="p-4">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
            <span className="text-blue-700">Generating AI explanation...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-4 border border-red-200 rounded-lg bg-red-50">
        <div className="p-4">
          <div className="flex items-center space-x-3">
            <svg className="h-5 w-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span className="text-red-700">{error}</span>
            <button 
              onClick={() => window.location.reload()}
              className="px-3 py-1 text-sm border border-red-300 rounded hover:bg-red-100"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mt-4 border border-blue-200 rounded-lg">
      {/* Header */}
      <div className="py-3 px-4 bg-blue-50 border-b border-blue-200 flex items-center justify-between rounded-t-lg">
        <h4 className="text-sm font-medium text-blue-800 flex items-center">
          <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          AI Explanation (XAI)
        </h4>
        {onClose && (
          <button onClick={onClose} className="p-1 hover:bg-blue-100 rounded">
            <svg className="h-4 w-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
      
      <div className="p-4">
        {/* Quick Summary */}
        {quickExplanation && (
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <h5 className="font-medium text-sm text-gray-700 mb-2">Key Insight</h5>
            <p className="text-sm text-gray-600">{quickExplanation.key_insight}</p>
            <p className="text-xs text-gray-500 mt-2">{quickExplanation.confidence_explanation}</p>
          </div>
        )}

        {/* Decision Factors Summary */}
        {decisionFactors && (
          <div className="mb-4">
            <h5 className="font-medium text-sm text-gray-700 mb-2">
              Decision Factors ({decisionFactors.total_factors_analyzed} analyzed)
            </h5>
            <div className="space-y-2">
              {decisionFactors.decision_factors.slice(0, 3).map((factor, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-white border rounded">
                  <div className="flex-1">
                    <span className="text-sm font-medium">{factor.factor}</span>
                    <span className="text-xs text-gray-500 ml-2">({factor.value})</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getDirectionColor(factor.direction)}`}>
                      {factor.direction === 'positive' ? 'Risk Factor' : 'Protective'}
                    </span>
                    <span className={`text-xs font-medium ${getImpactColor(factor.impact)}`}>
                      {factor.impact} Impact
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Toggle Full Explanation */}
        <button
          onClick={() => setShowFullExplanation(!showFullExplanation)}
          className="w-full mb-4 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center justify-center"
        >
          {showFullExplanation ? (
            <>
              <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
              Hide Detailed Analysis
            </>
          ) : (
            <>
              <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
              Show Detailed Analysis
            </>
          )}
        </button>

        {showFullExplanation && explanation && (
          <div>
            {/* Tabs */}
            <div className="flex border-b border-gray-200 mb-4">
              {['overview', 'features', 'counterfactual', 'path'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 text-sm font-medium ${
                    activeTab === tab
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab === 'overview' && 'Overview'}
                  {tab === 'features' && 'Features'}
                  {tab === 'counterfactual' && 'What-If'}
                  {tab === 'path' && 'Decision Path'}
                </button>
              ))}
            </div>

            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-4">
                <div className="p-3 bg-blue-50 rounded-lg">
                  <h5 className="font-medium text-sm text-blue-800 mb-2">Summary</h5>
                  <p className="text-sm text-gray-700">{explanation.summary}</p>
                </div>

                {/* Confidence Breakdown */}
                <div className="p-3 bg-gray-50 rounded-lg">
                  <h5 className="font-medium text-sm text-gray-800 mb-2">Confidence Breakdown</h5>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600">Total Confidence</span>
                    <span className="font-medium text-lg">
                      {Math.round(explanation.confidence_breakdown.total_confidence * 100)}%
                    </span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-600 rounded-full"
                      style={{ width: `${explanation.confidence_breakdown.total_confidence * 100}%` }}
                    />
                  </div>
                  <div className="mt-3 space-y-1">
                    {explanation.confidence_breakdown.components.map((comp, idx) => (
                      <div key={idx} className="flex items-center justify-between text-xs">
                        <span className="text-gray-600">{comp.feature}</span>
                        <span className="text-gray-800">+{Math.round(comp.contribution * 100)}%</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Local Explanation (LIME-style) */}
                <div className="p-3 bg-amber-50 rounded-lg">
                  <h5 className="font-medium text-sm text-amber-800 mb-2">
                    Local Interpretation (LIME)
                  </h5>
                  <p className="text-sm text-gray-700 mb-2">{explanation.local_explanation.interpretation}</p>
                  <div className="flex items-center text-xs text-gray-500">
                    <span>Local Accuracy: {Math.round(explanation.local_explanation.local_accuracy * 100)}%</span>
                  </div>
                </div>
              </div>
            )}

            {/* Features Tab (SHAP-style) */}
            {activeTab === 'features' && (
              <div className="space-y-4">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <h5 className="font-medium text-sm text-gray-800 mb-3">Feature Importance (SHAP)</h5>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        layout="vertical"
                        data={explanation.feature_importance.slice(0, 8).map(f => ({
                          name: f.feature,
                          value: f.importance,
                          direction: f.direction
                        }))}
                        margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" domain={[0, 1]} />
                        <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} />
                        <Tooltip
                          formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, 'Importance']}
                        />
                        <Bar dataKey="value">
                          {explanation.feature_importance.slice(0, 8).map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={getBarColor(entry.importance, entry.direction)} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex justify-center space-x-4 mt-2 text-xs">
                    <div className="flex items-center">
                      <div className="w-3 h-3 bg-red-500 rounded mr-1"></div>
                      <span>Risk Factor (increases suggestion)</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-3 h-3 bg-green-500 rounded mr-1"></div>
                      <span>Protective (decreases suggestion)</span>
                    </div>
                  </div>
                </div>

                {/* Feature Details */}
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {explanation.feature_importance.map((feature, idx) => (
                    <div key={idx} className="p-2 bg-white border rounded text-sm">
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{feature.feature}</span>
                        <span className={`px-2 py-0.5 rounded text-xs border ${getDirectionColor(feature.direction)}`}>
                          {Math.round(feature.importance * 100)}%
                        </span>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        <span>Value: {feature.value} {feature.unit}</span>
                        {feature.normal_range && (
                          <span className="ml-2">(Normal: {feature.normal_range})</span>
                        )}
                      </div>
                      <p className="text-xs text-gray-600 mt-1">{feature.explanation}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Counterfactual Tab */}
            {activeTab === 'counterfactual' && (
              <div className="space-y-4">
                <div className="p-3 bg-purple-50 rounded-lg">
                  <h5 className="font-medium text-sm text-purple-800 mb-2">What Would Change the Outcome?</h5>
                  <p className="text-sm text-gray-700">{explanation.counterfactual.scenario}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    Feasibility: {explanation.counterfactual.feasibility}
                  </p>
                </div>

                <div className="space-y-2">
                  <h6 className="font-medium text-sm text-gray-700">Changes Needed:</h6>
                  {explanation.counterfactual.changes_needed.map((change, idx) => (
                    <div key={idx} className="p-3 bg-white border rounded">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-sm">{change.feature}</span>
                        <span className="px-2 py-0.5 rounded text-xs bg-gray-100">{change.timeline}</span>
                      </div>
                      <div className="flex items-center text-sm">
                        <span className="text-red-600">{change.current_value} {change.unit}</span>
                        <span className="mx-2 text-gray-400">to</span>
                        <span className="text-green-600">{change.target_value} {change.unit}</span>
                      </div>
                      <p className="text-xs text-gray-600 mt-2">{change.intervention}</p>
                    </div>
                  ))}
                </div>

                {explanation.counterfactual.clinical_note && (
                  <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                    <div className="flex items-start">
                      <svg className="h-4 w-4 text-yellow-600 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <p className="text-xs text-yellow-800">{explanation.counterfactual.clinical_note}</p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Decision Path Tab */}
            {activeTab === 'path' && (
              <div className="space-y-4">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <h5 className="font-medium text-sm text-gray-800 mb-3">How the AI Made This Decision</h5>
                  <div className="space-y-3">
                    {explanation.decision_path.map((step, idx) => (
                      <div key={idx} className="flex">
                        <div className="flex flex-col items-center mr-3">
                          <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                            {step.step}
                          </div>
                          {idx < explanation.decision_path.length - 1 && (
                            <div className="w-0.5 h-full bg-blue-200 mt-1"></div>
                          )}
                        </div>
                        <div className="flex-1 pb-4">
                          <h6 className="font-medium text-sm text-gray-800">{step.action}</h6>
                          <p className="text-xs text-gray-600 mt-1">{step.description}</p>
                          <p className="text-xs text-blue-600 mt-1">Result: {step.outcome}</p>
                          {step.data_used && step.data_used.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              {step.data_used.map((data, dataIdx) => (
                                <span key={dataIdx} className="px-2 py-0.5 bg-gray-100 rounded text-xs">
                                  {data}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Contrastive Analysis (Why This vs That) */}
        {explanation?.contrastive && !showFullExplanation && (
          <div className="mt-4 p-3 bg-indigo-50 rounded-lg">
            <h5 className="font-medium text-sm text-indigo-800 mb-2">{explanation.contrastive.question}</h5>
            <div className="space-y-2">
              {explanation.contrastive.alternatives_considered.slice(0, 2).map((alt, idx) => (
                <div key={idx} className="text-xs">
                  <span className="font-medium text-gray-700">{alt.alternative}:</span>
                  <span className="text-gray-600 ml-1">{alt.why_not_chosen}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Disclaimer */}
        <div className="mt-4 p-2 bg-gray-100 rounded text-xs text-gray-500 flex items-start">
          <svg className="h-3 w-3 mr-1 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          This AI explanation is provided to support clinical decision-making. The final decision rests with the clinician.
        </div>
      </div>
    </div>
  );
}

/**
 * Compact inline XAI indicator for suggestion cards
 */
export function XAIIndicator({ 
  suggestionId, 
  onClick 
}: { 
  suggestionId: string; 
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="text-xs text-blue-600 hover:text-blue-800 hover:bg-blue-50 px-2 py-1 rounded flex items-center"
    >
      <svg className="h-3 w-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      Why this suggestion?
    </button>
  );
}

export default XAIExplanation;
