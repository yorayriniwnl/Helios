import './globals.css'
import '@fontsource/inter/300.css'
import '@fontsource/inter/400.css'
import '@fontsource/inter/600.css'
import '@fontsource/inter/700.css'
import '@fontsource/inter/800.css'
import React from 'react'
import OfflineBanner from '../components/ui/OfflineBanner'

export const metadata = {
  title: 'Helios',
  description: 'Real-time energy monitoring and anomaly detection.',
  themeColor: '#0b1220',
  openGraph: {
    title: 'Helios',
    description: 'Real-time energy monitoring and anomaly detection.',
    type: 'website',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-theme="dark">
      <body className="antialiased min-h-screen">
        <div className="min-h-screen flex flex-col">
          <OfflineBanner />
          <main className="flex-1 w-full transition-colors duration-300">
            <div className="container mx-auto py-6">
              {children}
            </div>
          </main>
          <footer className="py-4 text-center text-sm" style={{ color: 'var(--muted)' }}>
            © {new Date().getFullYear()} Helios
          </footer>
        </div>
      </body>
    </html>
  )
}
