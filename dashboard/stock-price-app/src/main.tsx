/**
 * Main Entry Point
 *
 * Application bootstrap with providers.
 *
 * @version 5.4.0 - TypeScript Migration
 */

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { GoogleOAuthProvider } from '@react-oauth/google'
import { AppProvider } from '@/context'
import '@/index.css'
import App from '@/App'

// Google OAuth Client ID
const GOOGLE_CLIENT_ID: string = import.meta.env.VITE_GOOGLE_CLIENT_ID || '1075463475276-gtc3p6tqm4c2104hrfrot4itdecm3avd.apps.googleusercontent.com'

// Get root element with null check
const rootElement = document.getElementById('root')

if (!rootElement) {
  throw new Error('Root element not found')
}

createRoot(rootElement).render(
  <StrictMode>
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <AppProvider>
        <App />
      </AppProvider>
    </GoogleOAuthProvider>
  </StrictMode>,
)
