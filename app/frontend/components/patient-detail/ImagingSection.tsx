/**
 * Imaging section component with viewer
 */
'use client';

import { ImageViewer } from './ImageViewer';

interface ImagingSectionProps {
  patientId: string;
}

export function ImagingSection({ patientId }: ImagingSectionProps) {
  return <ImageViewer patientId={patientId} />;
}

