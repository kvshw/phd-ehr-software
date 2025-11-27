/**
 * AI Suggestions Section component
 */
'use client';

import { SuggestionsPanel } from './SuggestionsPanel';

interface SuggestionsSectionProps {
  patientId: string;
}

export function SuggestionsSection({ patientId }: SuggestionsSectionProps) {
  return <SuggestionsPanel patientId={patientId} />;
}

