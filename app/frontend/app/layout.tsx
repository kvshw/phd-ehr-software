import type { Metadata } from 'next'
import './globals.css'
import { DemoModeWrapper } from '@/components/demo/DemoModeWrapper'

export const metadata: Metadata = {
  title: 'EHR Research Platform',
  description: 'Self-Adaptive AI-Assisted EHR Research Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <DemoModeWrapper>
          {children}
        </DemoModeWrapper>
      </body>
    </html>
  )
}

