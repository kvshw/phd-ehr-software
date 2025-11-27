/**
 * Demo Mode Wrapper
 * Client-side wrapper for DemoModeProvider to work with Next.js App Router
 */
'use client';

import { DemoModeProvider } from './DemoMode';

export function DemoModeWrapper({ children }: { children: React.ReactNode }) {
  return (
    <DemoModeProvider>
      {children}
    </DemoModeProvider>
  );
}

