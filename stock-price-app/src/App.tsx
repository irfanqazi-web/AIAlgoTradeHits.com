/**
 * App Component - Root application component
 *
 * Handles routing, authentication flow, and view rendering.
 * Now fully integrated with SSOT Context layer.
 *
 * @version 5.4.0 - TypeScript Migration
 */

import { useState, useEffect, useCallback, memo } from 'react'
import { useAuth } from '@/context'
import '@/App.css'
import type { LucideIcon } from 'lucide-react'

// Shared Components
import Navigation from '@/components/shared/Navigation'
import Login from '@/components/shared/Login'
import PasswordChangeModal from '@/components/shared/PasswordChangeModal'
import ComingSoon from '@/components/shared/ComingSoon'

// Dashboard Components
import TradingDashboard from '@/components/dashboard/TradingDashboard'
import SmartDashboard from '@/components/dashboard/SmartDashboard'

// Chart Components
import ProfessionalChart from '@/components/charts/ProfessionalChart'

// Portfolio Components
import PriceAlerts from '@/components/portfolio/PriceAlerts'
import PortfolioTracker from '@/components/portfolio/PortfolioTracker'

// Admin Components
import AdminPanelEnhanced from '@/components/admin/AdminPanelEnhanced'
import TableInventory from '@/components/admin/TableInventory'
import DatabaseSummary from '@/components/admin/DatabaseSummary'

// Content Components
import DocumentsLibrary from '@/components/content/DocumentsLibrary'
import AITrainingDocs from '@/components/content/AITrainingDocs'

// Signal Components
import AIPredictions from '@/components/signals/AIPredictions'
import AIPatternRecognition from '@/components/signals/AIPatternRecognition'
import AITradeSignals from '@/components/signals/AITradeSignals'
import MultiTimeframeTrader from '@/components/signals/MultiTimeframeTrader'
import OpportunityReport from '@/components/signals/OpportunityReport'
import WalkForwardValidation from '@/components/signals/WalkForwardValidation'

// Analytics Components
import StrategyDashboard from '@/components/analytics/StrategyDashboard'
import MarketMovers from '@/components/analytics/MarketMovers'
import ETFAnalytics from '@/components/analytics/ETFAnalytics'

// Data Components
import DataWarehouseStatus from '@/components/data/DataWarehouseStatus'
import DataExportDownload from '@/components/data/DataExportDownload'
import MLTestDataDownload from '@/components/data/MLTestDataDownload'

import {
  Brain, Target, BarChart3, Users, Zap
} from 'lucide-react'

// Type definitions
type ViewType =
  | 'dashboard'
  | 'markets'
  | 'ai-signals'
  | 'charts'
  | 'weekly'
  | 'analysis'
  | 'portfolio'
  | 'alerts'
  | 'strategies'
  | 'documents'
  | 'ai-training'
  | 'settings'
  | 'admin'
  | 'table-inventory'
  | 'data-warehouse-status'
  | 'market-movers'
  | 'fundamentals'
  | 'etf-analytics'
  | 'database-summary'
  | 'data-export'
  | 'ml-test-data'
  | 'trade-analysis'
  | 'opportunity-report'
  | 'walk-forward'
  | string

type SearchMethod = 'text' | 'voice' | 'nlp'

interface LoginCredentials {
  email: string
  password: string
}

// Memoized Loading Component
const LoadingScreen = memo(function LoadingScreen() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
      <div className="flex flex-col items-center gap-4">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <span className="text-slate-400">Loading...</span>
      </div>
    </div>
  )
})

function App(): JSX.Element {
  // View state
  const [currentView, setCurrentView] = useState<ViewType>('dashboard')
  const [isMenuOpen, setIsMenuOpen] = useState<boolean>(true)
  const [showPasswordChange, setShowPasswordChange] = useState<boolean>(false)

  // Search state
  const [searchQuery, setSearchQuery] = useState<string | null>(null)
  const [searchMethod, setSearchMethod] = useState<SearchMethod>('text')

  // Auth from Context (SSOT - Single Source of Truth)
  const {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    changePassword
  } = useAuth()

  // Handle login success from Login component
  const handleLoginSuccess = useCallback(async (credentials: LoginCredentials): Promise<void> => {
    if (credentials?.email && credentials?.password) {
      await login(credentials.email, credentials.password)
    }
  }, [login])

  // Handle password change success
  const handlePasswordChangeSuccess = useCallback(async (): Promise<void> => {
    setShowPasswordChange(false)
  }, [])

  // Handle logout
  const handleLogout = useCallback(async (): Promise<void> => {
    await logout()
    setCurrentView('dashboard')
  }, [logout])

  // Toggle menu
  const handleMenuToggle = useCallback((): void => {
    setIsMenuOpen(prev => !prev)
  }, [])

  // Search handler function
  const handleSearch = useCallback((query: string, method: SearchMethod = 'text'): void => {
    setSearchQuery(query)
    setSearchMethod(method)
    if (!currentView.startsWith('dashboard') && !currentView.startsWith('markets')) {
      setCurrentView('dashboard')
    }
  }, [currentView])

  // Check if first login requires password change
  useEffect(() => {
    if (user?.isFirstLogin) {
      setShowPasswordChange(true)
    }
  }, [user])

  // Show loading screen while checking auth
  if (isLoading) {
    return <LoadingScreen />
  }

  // Show login if not authenticated
  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />
  }

  const renderView = (): JSX.Element | null => {
    // Dashboard is handled separately below
    if (currentView === 'dashboard' || currentView.startsWith('markets')) {
      return null
    }

    // AI Signals Section
    if (currentView === 'ai-signals' || currentView.startsWith('ai-signals-')) {
      const subView = currentView.split('-')[2]

      if (subView === 'predictions') {
        return <AIPredictions symbol="BTCUSD" timeframe="daily" />
      }

      if (subView === 'patterns') {
        return <AIPatternRecognition symbol="BTCUSD" timeframe="daily" />
      }

      if (subView === 'sentiment') {
        return <ComingSoon
          title="Sentiment Analysis"
          description="Natural language processing analyzes social media, news, and market sentiment to gauge crowd psychology."
          icon={Users}
          availableIn="Phase 2 (3 months)"
          features={[
            "Twitter and Reddit sentiment scoring",
            "Real-time news impact analysis",
            "Fear & Greed Index tracking",
            "Influencer activity monitoring",
            "Sentiment-driven trading signals"
          ]}
        />
      }

      if (subView === 'signals') {
        return <AITradeSignals symbol="BTCUSD" timeframe="daily" />
      }

      if (subView === 'anomalies') {
        return <ComingSoon
          title="Anomaly Detection"
          description="AI algorithms identify unusual market activity, volume spikes, and potential manipulation in real-time."
          icon={Zap}
          availableIn="Phase 2 (3 months)"
          features={[
            "Unusual volume and price spike detection",
            "Whale transaction tracking",
            "Flash crash and pump detection",
            "Order flow imbalance alerts",
            "Market manipulation warnings"
          ]}
        />
      }

      // Default AI Signals landing
      return <ComingSoon
        title="AI-Powered Trading Intelligence"
        description="Harness the power of machine learning to gain insights that traditional analysis can't provide."
        icon={Brain}
        availableIn="Phase 1-2 (2-3 months)"
        features={[
          "Price predictions using LSTM neural networks",
          "Chart pattern recognition with computer vision",
          "Social media and news sentiment analysis",
          "AI-generated trade signals and recommendations",
          "Anomaly detection for unusual market activity"
        ]}
      />
    }

    // Charts Section
    if (currentView === 'charts' || currentView.startsWith('charts-')) {
      return <ProfessionalChart symbol="BTCUSD" marketType="crypto" />
    }

    // Weekly Section
    if (currentView === 'weekly' || currentView.startsWith('weekly-')) {
      return <SmartDashboard searchQuery={null} searchMethod="text" />
    }

    // Analysis Section
    if (currentView === 'analysis' || currentView.startsWith('analysis-')) {
      return <StrategyDashboard />
    }

    // Portfolio Section
    if (currentView === 'portfolio' || currentView.startsWith('portfolio-')) {
      return <PortfolioTracker />
    }

    // Alerts Section
    if (currentView === 'alerts' || currentView.startsWith('alerts-')) {
      return <PriceAlerts marketType="crypto" />
    }

    // Strategies Section
    if (currentView === 'strategies' || currentView.startsWith('strategies-')) {
      return <StrategyDashboard />
    }

    // Documents Section
    if (currentView === 'documents' || currentView.startsWith('documents-')) {
      return <DocumentsLibrary />
    }

    // AI Training Section
    if (currentView === 'ai-training' || currentView.startsWith('ai-training-')) {
      return <AITrainingDocs theme="dark" />
    }

    // Settings
    if (currentView === 'settings') {
      return (
        <div className="p-8 max-w-3xl mx-auto">
          <h2 className="text-white text-2xl font-semibold mb-6">Account Settings</h2>

          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-5 mb-5">
            <h3 className="text-emerald-400 font-semibold mb-4">Profile Information</h3>
            <div className="text-white mb-3">
              <strong>Name:</strong> {user?.name || user?.email?.split('@')[0]}
            </div>
            <div className="text-white mb-3">
              <strong>Email:</strong> {user?.email}
            </div>
            <div className="text-white mb-3">
              <strong>Role:</strong> <span className="capitalize">{user?.role}</span>
            </div>
          </div>

          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-5">
            <h3 className="text-emerald-400 font-semibold mb-4">Security</h3>
            <button
              onClick={() => setShowPasswordChange(true)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg mr-3 transition-colors"
            >
              Change Password
            </button>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      )
    }

    // Admin Panel
    if (currentView === 'admin') {
      if (user?.role === 'admin') {
        return <AdminPanelEnhanced onClose={() => setCurrentView('dashboard')} />
      } else {
        return <ComingSoon
          title="Access Denied"
          description="You do not have permission to access the admin panel."
          icon={Target}
          availableIn="Admin Only"
          features={[]}
        />
      }
    }

    // Table Inventory
    if (currentView === 'table-inventory') {
      return <TableInventory theme="dark" />
    }

    // Data Warehouse Status
    if (currentView === 'data-warehouse-status') {
      return <DataWarehouseStatus theme="dark" />
    }

    // Market Movers
    if (currentView === 'market-movers') {
      return <MarketMovers theme="dark" />
    }

    // Fundamentals
    if (currentView === 'fundamentals') {
      return <ComingSoon
        title="Fundamentals View"
        description="Company profiles, financial data, and fundamental analysis."
        icon={BarChart3}
        availableIn="Phase 2"
        features={[
          "Company profile and overview",
          "Financial statements",
          "Earnings reports",
          "Analyst ratings"
        ]}
      />
    }

    // ETF Analytics
    if (currentView === 'etf-analytics') {
      return <ETFAnalytics theme="dark" />
    }

    // Database Summary
    if (currentView === 'database-summary') {
      return <DatabaseSummary theme="dark" />
    }

    // Data Export
    if (currentView === 'data-export') {
      return <DataExportDownload theme="dark" />
    }

    // ML Test Data
    if (currentView === 'ml-test-data') {
      return <MLTestDataDownload theme="dark" />
    }

    // Multi-Timeframe Trade Analysis
    if (currentView === 'trade-analysis' || currentView.startsWith('trade-')) {
      return <MultiTimeframeTrader theme="dark" />
    }

    // Daily Opportunity Report
    if (currentView === 'opportunity-report') {
      return <OpportunityReport theme="dark" />
    }

    // Walk-Forward ML Validation
    if (currentView === 'walk-forward' || currentView.startsWith('walk-forward-')) {
      return <WalkForwardValidation theme="dark" />
    }

    // Default fallback
    return <TradingDashboard />
  }

  return (
    <div className="app bg-slate-900 min-h-screen">
      <Navigation
        currentView={currentView}
        onViewChange={setCurrentView}
        isMenuOpen={isMenuOpen}
        onMenuToggle={handleMenuToggle}
        currentUser={user}
        onSearch={handleSearch}
        onLogout={handleLogout}
      />
      <main
        className="transition-all duration-300 ease-in-out"
        style={{
          marginLeft: isMenuOpen ? '280px' : '0',
          marginTop: '64px'
        }}
      >
        {currentView === 'dashboard' || currentView.startsWith('markets') ? (
          <SmartDashboard searchQuery={searchQuery} searchMethod={searchMethod} />
        ) : (
          renderView()
        )}
      </main>

      {/* Password Change Modal */}
      {showPasswordChange && (
        <PasswordChangeModal
          onClose={() => setShowPasswordChange(false)}
          onSuccess={handlePasswordChangeSuccess}
          onChangePassword={changePassword}
          isFirstLogin={user?.isFirstLogin}
        />
      )}
    </div>
  )
}

export default App
