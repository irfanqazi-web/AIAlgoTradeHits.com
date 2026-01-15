import { useState, useEffect } from 'react'
import './App.css'
import Navigation from './components/Navigation'
import TradingDashboard from './components/TradingDashboard'
import SmartDashboard from './components/SmartDashboard'
import AdvancedChart from './components/AdvancedChart'
import PriceAlerts from './components/PriceAlerts'
import PortfolioTracker from './components/PortfolioTracker'
import ComingSoon from './components/ComingSoon'
import AdminPanel from './components/AdminPanel'
import AdminPanelEnhanced from './components/AdminPanelEnhanced'
import Login from './components/Login'
import PasswordChangeModal from './components/PasswordChangeModal'
import DocumentsLibrary from './components/DocumentsLibrary'
import NLPSearch from './components/NLPSearch'
import AIPredictions from './components/AIPredictions'
import AIPatternRecognition from './components/AIPatternRecognition'
import AITradeSignals from './components/AITradeSignals'
import WeeklyAnalysis from './components/WeeklyAnalysis'
import WeeklyDashboard from './components/WeeklyDashboard'
import DataReconciliation from './components/DataReconciliation'
import WeeklyReconciliation from './components/WeeklyReconciliation'
import AITrainingDocs from './components/AITrainingDocs'
import TableInventory from './components/TableInventory'
import DataWarehouseStatus from './components/DataWarehouseStatus'
import StrategyDashboard from './components/StrategyDashboard'
import apiService from './services/api'
import {
  Brain, Target, BarChart3, Briefcase, Bell,
  BookOpen, TrendingUp, Zap, Users, LineChart, Search
} from 'lucide-react'

function App() {
  const [currentView, setCurrentView] = useState('dashboard')
  const [isMenuOpen, setIsMenuOpen] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [currentUser, setCurrentUser] = useState(null)
  const [showPasswordChange, setShowPasswordChange] = useState(false)
  const [isCheckingAuth, setIsCheckingAuth] = useState(true)

  // Search handler state - MUST be at top level
  const [searchQuery, setSearchQuery] = useState(null)
  const [searchMethod, setSearchMethod] = useState('text')

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('auth_token')
      if (token) {
        const response = await apiService.verifyToken()
        if (response.success) {
          const user = apiService.getCurrentUser()
          setCurrentUser(user)
          setIsAuthenticated(true)
        } else {
          apiService.logout()
        }
      }
      setIsCheckingAuth(false)
    }

    checkAuth()
  }, [])

  const handleLoginSuccess = (user) => {
    setCurrentUser(user)
    setIsAuthenticated(true)
  }

  const handlePasswordChangeSuccess = () => {
    setShowPasswordChange(false)
    // Update user object to reflect password change
    if (currentUser) {
      const updatedUser = { ...currentUser, first_login_completed: true }
      setCurrentUser(updatedUser)
      localStorage.setItem('user', JSON.stringify(updatedUser))
    }
  }

  const handleLogout = () => {
    apiService.logout()
    setIsAuthenticated(false)
    setCurrentUser(null)
    setCurrentView('dashboard')
  }

  // Show loading screen while checking auth
  if (isCheckingAuth) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#0a0e27',
        color: 'white'
      }}>
        <div>Loading...</div>
      </div>
    )
  }

  // Show login if not authenticated
  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />
  }

  const renderView = () => {
    // Dashboard is handled separately below, skip it here
    if (currentView === 'dashboard' || currentView.startsWith('markets')) {
      return null;
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
      return <AdvancedChart symbol="BTCUSD" marketType="crypto" />
    }

    // Weekly Dashboard - All 6 Asset Types in One View
    if (currentView === 'weekly' || currentView === 'weekly-dashboard') {
      return <WeeklyDashboard />
    }

    // Analysis Section - 6 Asset Types
    if (currentView === 'analysis' || currentView.startsWith('analysis-')) {
      const subView = currentView.split('-')[1]

      if (subView === 'stocks') {
        return <WeeklyAnalysis assetType="stocks" />
      }
      if (subView === 'cryptos') {
        return <WeeklyAnalysis assetType="cryptos" />
      }
      if (subView === 'etfs') {
        return <WeeklyAnalysis assetType="etfs" />
      }
      if (subView === 'forex') {
        return <WeeklyAnalysis assetType="forex" />
      }
      if (subView === 'indices') {
        return <WeeklyAnalysis assetType="indices" />
      }
      if (subView === 'commodities') {
        return <WeeklyAnalysis assetType="commodities" />
      }

      // Default to stocks weekly
      return <WeeklyAnalysis assetType="stocks" />
    }

    // Portfolio Section
    if (currentView === 'portfolio' || currentView.startsWith('portfolio-')) {
      return <PortfolioTracker />
    }

    // Alerts Section
    if (currentView === 'alerts' || currentView.startsWith('alerts-')) {
      return <PriceAlerts marketType="crypto" />
    }

    // Strategies Section - now uses real StrategyDashboard
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
        <div style={{ padding: '32px', maxWidth: '800px', margin: '0 auto' }}>
          <h2 style={{ color: 'white', marginBottom: '24px' }}>Account Settings</h2>

          <div style={{
            background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
            borderRadius: '16px',
            padding: '24px',
            border: '1px solid #334155',
            marginBottom: '20px'
          }}>
            <h3 style={{ color: '#10b981', marginBottom: '16px' }}>Profile Information</h3>
            <div style={{ color: 'white', marginBottom: '12px' }}>
              <strong>Name:</strong> {currentUser?.username}
            </div>
            <div style={{ color: 'white', marginBottom: '12px' }}>
              <strong>Email:</strong> {currentUser?.email}
            </div>
            <div style={{ color: 'white', marginBottom: '12px' }}>
              <strong>Role:</strong> {currentUser?.role}
            </div>
          </div>

          <div style={{
            background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
            borderRadius: '16px',
            padding: '24px',
            border: '1px solid #334155',
            marginBottom: '20px'
          }}>
            <h3 style={{ color: '#10b981', marginBottom: '16px' }}>Security</h3>
            <button
              onClick={() => setShowPasswordChange(true)}
              style={{
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                padding: '12px 24px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                marginRight: '12px'
              }}
            >
              Change Password
            </button>
            <button
              onClick={handleLogout}
              style={{
                background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                padding: '12px 24px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              Logout
            </button>
          </div>
        </div>
      )
    }

    // Admin Panel
    if (currentView === 'admin') {
      if (currentUser?.role === 'admin') {
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

    // Data Reconciliation
    if (currentView === 'data-reconciliation') {
      return <DataReconciliation />
    }

    // Weekly Reconciliation
    if (currentView === 'weekly-reconciliation') {
      return <WeeklyReconciliation />
    }

    // Table Inventory - BigQuery tables with row counts
    if (currentView === 'table-inventory') {
      return <TableInventory theme="dark" />
    }

    // Data Warehouse Status - Monitor batch download progress
    if (currentView === 'data-warehouse-status') {
      return <DataWarehouseStatus theme="dark" />
    }

    // Default fallback
    return <TradingDashboard />
  }

  // Search handler function
  const handleSearch = (query, method = 'text') => {
    setSearchQuery(query);
    setSearchMethod(method);
    // Ensure we're on dashboard view
    if (!currentView.startsWith('dashboard') && !currentView.startsWith('markets')) {
      setCurrentView('dashboard');
    }
  };

  return (
    <div className="app" style={{ margin: 0, padding: 0 }}>
      <Navigation
        currentView={currentView}
        onViewChange={setCurrentView}
        isMenuOpen={isMenuOpen}
        onMenuToggle={() => setIsMenuOpen(!isMenuOpen)}
        currentUser={currentUser}
        onSearch={handleSearch}
      />
      <div style={{
        marginLeft: isMenuOpen ? '280px' : '0',
        marginTop: '64px',
        transition: 'margin-left 0.3s ease'
      }}>
        {currentView === 'dashboard' || currentView.startsWith('markets') ? (
          <SmartDashboard searchQuery={searchQuery} searchMethod={searchMethod} />
        ) : (
          renderView()
        )}
      </div>
    </div>
  )
}

export default App
