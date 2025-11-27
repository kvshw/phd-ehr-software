/**
 * Labs section component with table
 */
'use client';

import { LabsTable } from './LabsTable';

interface LabsSectionProps {
  patientId: string;
}

export function LabsSection({ patientId }: LabsSectionProps) {
  return <LabsTable patientId={patientId} />;
}

