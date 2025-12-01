"use client";

import { useState, useEffect } from "react";

interface AdaptationExplanationProps {
  feature: string;
  featureLabel?: string;
  showBadge?: boolean;
  variant?: "tooltip" | "inline" | "card";
  className?: string;
}

interface ExplanationData {
  feature: string;
  has_adaptation: boolean;
  explanation?: string;
  adapted_at?: string;
  confidence?: number;
  metrics?: {
    usage_count?: number;
    daily_average?: number;
    efficiency?: number;
  };
  type?: string;
}

/**
 * AdaptationExplanation Component
 * 
 * Shows users why a feature was adapted/promoted.
 * Builds trust and transparency by explaining MAPE-K decisions.
 */
export function AdaptationExplanation({
  feature,
  featureLabel,
  showBadge = true,
  variant = "tooltip",
  className,
}: AdaptationExplanationProps) {
  const [explanation, setExplanation] = useState<ExplanationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showTooltip, setShowTooltip] = useState(false);

  useEffect(() => {
    fetchExplanation();
  }, [feature]);

  const fetchExplanation = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/assurance/explain/${encodeURIComponent(feature)}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setExplanation(data);
      }
    } catch (error) {
      console.error("Error fetching explanation:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !explanation?.has_adaptation) {
    return null;
  }

  const content = (
    <ExplanationContent
      explanation={explanation}
      featureLabel={featureLabel || feature}
    />
  );

  if (variant === "inline") {
    return (
      <div className={`text-sm text-gray-500 ${className || ""}`}>
        {content}
      </div>
    );
  }

  if (variant === "card") {
    return (
      <div
        className={`rounded-lg border bg-gradient-to-br from-blue-50 to-indigo-50 p-4 ${className || ""}`}
      >
        <div className="flex items-start gap-3">
          <div className="rounded-full bg-blue-100 p-2">
            <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
          </div>
          <div className="flex-1">
            <h4 className="font-medium text-sm mb-1">
              Why "{featureLabel || feature}" was promoted
            </h4>
            {content}
          </div>
        </div>
      </div>
    );
  }

  // Default: tooltip variant
  return (
    <div className={`relative inline-block ${className || ""}`}>
      <button
        className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-700"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        {showBadge && (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
            <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
            Adapted
          </span>
        )}
        {!showBadge && (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )}
      </button>
      
      {showTooltip && (
        <div className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-4 bg-white border rounded-lg shadow-lg">
          <h4 className="font-semibold text-sm mb-2">
            Why "{featureLabel || feature}" was promoted
          </h4>
          {content}
        </div>
      )}
    </div>
  );
}

function ExplanationContent({
  explanation,
  featureLabel,
}: {
  explanation: ExplanationData;
  featureLabel: string;
}) {
  return (
    <div className="space-y-3">
      {/* Main explanation */}
      <p className="text-sm text-gray-600">
        {explanation.explanation ||
          `This feature was adapted based on your usage patterns.`}
      </p>

      {/* Usage stats */}
      {explanation.metrics && (
        <div className="grid grid-cols-2 gap-2 text-xs">
          {explanation.metrics.usage_count !== undefined && (
            <div className="flex items-center gap-2 bg-gray-100 rounded px-2 py-1">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <span className="text-gray-500">Total uses:</span>
              <span className="font-medium">{explanation.metrics.usage_count}</span>
            </div>
          )}
          {explanation.metrics.daily_average !== undefined && (
            <div className="flex items-center gap-2 bg-gray-100 rounded px-2 py-1">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-gray-500">Per day:</span>
              <span className="font-medium">{explanation.metrics.daily_average.toFixed(1)}</span>
            </div>
          )}
        </div>
      )}

      {/* Confidence indicator */}
      {explanation.confidence !== undefined && (
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">Confidence:</span>
          <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 rounded-full transition-all"
              style={{ width: `${explanation.confidence * 100}%` }}
            />
          </div>
          <span className="text-xs font-medium">
            {Math.round(explanation.confidence * 100)}%
          </span>
        </div>
      )}

      {/* Adapted timestamp */}
      {explanation.adapted_at && (
        <p className="text-xs text-gray-500">
          Promoted {formatRelativeTime(explanation.adapted_at)}
        </p>
      )}
    </div>
  );
}

function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return "today";
  if (diffDays === 1) return "yesterday";
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  return `${Math.floor(diffDays / 30)} months ago`;
}

// Export a simpler "Why this moved" badge component
export function WhyThisMovedBadge({
  feature,
  featureLabel,
}: {
  feature: string;
  featureLabel?: string;
}) {
  return (
    <AdaptationExplanation
      feature={feature}
      featureLabel={featureLabel}
      showBadge={true}
      variant="tooltip"
    />
  );
}
