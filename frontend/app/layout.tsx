import './globals.css'
import React from 'react'
import OfflineBanner from '../components/ui/OfflineBanner'

export const metadata = {
  title: 'Helios',
  description: 'Helios Frontend'
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
