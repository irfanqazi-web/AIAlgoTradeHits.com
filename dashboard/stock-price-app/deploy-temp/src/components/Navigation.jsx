import React, { useState, useRef, useEffect } from 'react';
import {
  Home, TrendingUp, Brain, Briefcase, BarChart3, Bell,
  Target, BookOpen, Settings, Menu, X, Search, ChevronDown,
  LineChart, Users, Zap, Shield, HelpCircle, FileText, Mic, MicOff,
  PieChart, DollarSign, Globe, Activity, Coins, Database, HardDrive
} from 'lucide-react';

const Navigation = ({ currentView, onViewChange, onMenuToggle, isMenuOpen, currentUser, onSearch }) => {
  const [activeDropdown, setActiveDropdown] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const recognitionRef = useRef(null);

  // Initialize Speech Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        let final = '';
        for (let i = 0; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            final = transcript;
          } else {
            setSearchQuery(transcript);
          }
        }
        if (final) {
          setSearchQuery(final);
          setIsListening(false);
          handleSearch(final, 'voice');
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  const startListening = () => {
    if (recognitionRef.current) {
      setIsListening(true);
      setSearchQuery('');
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const handleSearch = (query = searchQuery, method = 'text') => {
    if (query.trim() && onSearch) {
      onSearch(query, method);
    }
  };

  const suggestions = [
    // Stocks
    'oversold tech stocks daily',
    'top 10 stock gainers weekly',
    'high volume stocks hourly',
    // Crypto
    'bitcoin price daily',
    'oversold crypto weekly',
    'top crypto gainers',
    // Forex
    'EUR/USD forex daily',
    'forex high volatility',
    // ETFs
    'SPY etf daily',
    'etf with bullish MACD',
    // Indices
    'S&P 500 index weekly',
    // Commodities
    'gold price daily',
    'silver commodities'
  ];

  const menuItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: Home,
      path: '/dashboard',
      description: 'Market overview and portfolio summary'
    },
    {
      id: 'ai-signals',
      label: 'AI Signals',
      icon: Brain,
      path: '/ai-signals',
      badge: 'NEW',
      description: 'AI-powered trading intelligence',
      submenu: [
        { id: 'predictions', label: 'Price Predictions', icon: TrendingUp },
        { id: 'patterns', label: 'Pattern Recognition', icon: Target },
        { id: 'sentiment', label: 'Sentiment Analysis', icon: Users },
        { id: 'trade-signals', label: 'Trade Signals', icon: Zap },
        { id: 'anomalies', label: 'Anomaly Detection', icon: Shield },
      ]
    },
    {
      id: 'portfolio',
      label: 'Portfolio',
      icon: Briefcase,
      path: '/portfolio',
      description: 'Manage and optimize your portfolio',
      submenu: [
        { id: 'overview', label: 'Portfolio Overview', icon: Briefcase },
        { id: 'transactions', label: 'Transaction History', icon: TrendingUp },
        { id: 'optimizer', label: 'AI Optimizer', icon: Brain },
        { id: 'rebalancing', label: 'Rebalancing', icon: Target },
      ]
    },
    {
      id: 'alerts',
      label: 'Alerts',
      icon: Bell,
      path: '/alerts',
      description: 'Smart price and indicator alerts',
      submenu: [
        { id: 'price-alerts', label: 'Price Alerts', icon: TrendingUp },
        { id: 'indicator-alerts', label: 'Indicator Alerts', icon: BarChart3 },
        { id: 'ai-alerts', label: 'AI Alerts', icon: Brain },
        { id: 'portfolio-alerts', label: 'Portfolio Alerts', icon: Briefcase },
      ]
    },
    {
      id: 'strategies',
      label: 'Strategies',
      icon: Target,
      path: '/strategies',
      badge: 'LIVE',
      description: 'Rise Cycle, Sector Momentum & Paper Trading',
      submenu: [
        { id: 'dashboard', label: 'Strategy Dashboard', icon: Target },
        { id: 'sectors', label: 'Sector Momentum', icon: TrendingUp },
        { id: 'rise-cycles', label: 'Rise Cycle Analyzer', icon: BarChart3 },
        { id: 'paper-trading', label: 'Paper Trading', icon: Brain },
      ]
    },
    {
      id: 'ai-training',
      label: 'AI Training',
      icon: Brain,
      path: '/ai-training',
      badge: 'AI',
      description: 'Train and manage AI model documents'
    },
    {
      id: 'documents',
      label: 'Documents',
      icon: FileText,
      path: '/documents',
      description: 'Project documentation and guides'
    },
    {
      id: 'data-reconciliation',
      label: 'Data Reconciliation',
      icon: Activity,
      path: '/data-reconciliation',
      badge: 'VERIFY',
      description: 'View and verify all downloaded stock data fields'
    },
    {
      id: 'weekly-reconciliation',
      label: 'Weekly Analysis',
      icon: TrendingUp,
      path: '/weekly-reconciliation',
      badge: 'CHARTS',
      description: 'Weekly trends with charts and complete data verification'
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: Settings,
      path: '/settings',
      description: 'Account and platform settings'
    },
  ];

  // Add admin menu item for admin users
  if (currentUser?.role === 'admin') {
    menuItems.push({
      id: 'admin',
      label: 'Admin Panel',
      icon: Shield,
      path: '/admin',
      badge: 'ADMIN',
      description: 'User management and system administration'
    });
    menuItems.push({
      id: 'table-inventory',
      label: 'Table Inventory',
      icon: Database,
      path: '/table-inventory',
      badge: 'AI',
      description: 'BigQuery tables with AI-powered insights'
    });
    menuItems.push({
      id: 'data-warehouse-status',
      label: 'Data Warehouse',
      icon: HardDrive,
      path: '/data-warehouse-status',
      badge: 'LIVE',
      description: 'Monitor data collection progress in real-time'
    });
  }

  const handleItemClick = (item) => {
    if (item.submenu) {
      setActiveDropdown(activeDropdown === item.id ? null : item.id);
    } else {
      onViewChange(item.id);
      if (window.innerWidth < 1024) {
        onMenuToggle();
      }
    }
  };

  const handleSubmenuClick = (parentId, submenuId) => {
    onViewChange(`${parentId}-${submenuId}`);
    setActiveDropdown(null);
    if (window.innerWidth < 1024) {
      onMenuToggle();
    }
  };

  return (
    <>
      {/* Top Navigation Bar */}
      <nav style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        height: '64px',
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        borderBottom: '1px solid #334155',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        padding: '0 20px',
        justifyContent: 'space-between'
      }}>
        {/* Logo and Menu Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <button
            onClick={onMenuToggle}
            style={{
              background: 'none',
              border: 'none',
              color: 'white',
              cursor: 'pointer',
              padding: '8px',
              display: 'flex',
              alignItems: 'center',
              borderRadius: '8px',
              transition: 'background 0.2s'
            }}
            onMouseEnter={(e) => e.target.style.background = '#334155'}
            onMouseLeave={(e) => e.target.style.background = 'none'}
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>

          <div style={{
            fontSize: '24px',
            fontWeight: 'bold',
            background: 'linear-gradient(135deg, #10b981 0%, #3b82f6 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            AIAlgoTradeHits
          </div>
        </div>

        {/* Smart Search Bar */}
        <div style={{
          flex: 1,
          maxWidth: '700px',
          margin: '0 40px',
          position: 'relative'
        }}>
          <input
            type="text"
            placeholder={isListening ? "Listening..." : "Ask anything... (e.g., 'oversold stocks' or 'top 10 gainers')"}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleSearch(searchQuery, 'text');
              }
            }}
            style={{
              width: '100%',
              padding: '14px 160px 14px 20px',
              background: 'white',
              border: isListening ? '2px solid #10b981' : '2px solid #e2e8f0',
              borderRadius: '24px',
              color: '#1e293b',
              fontSize: '15px',
              outline: 'none',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
              transition: 'all 0.2s'
            }}
          />
          <div style={{
            position: 'absolute',
            right: '12px',
            top: '50%',
            transform: 'translateY(-50%)',
            display: 'flex',
            gap: '8px',
            alignItems: 'center'
          }}>
            {/* Help Icon with Tooltip */}
            <div
              style={{ position: 'relative', display: 'inline-block' }}
              onMouseEnter={() => setShowHelp(true)}
              onMouseLeave={() => setShowHelp(false)}
            >
              <button
                style={{
                  background: 'none',
                  border: '1px solid #94a3b8',
                  color: '#64748b',
                  cursor: 'help',
                  padding: '6px',
                  display: 'flex',
                  alignItems: 'center',
                  borderRadius: '50%',
                  transition: 'all 0.2s',
                  width: '32px',
                  height: '32px',
                  justifyContent: 'center'
                }}
              >
                <HelpCircle size={18} />
              </button>

              {/* Hover Tooltip */}
              {showHelp && (
                <div style={{
                  position: 'absolute',
                  top: '100%',
                  right: 0,
                  marginTop: '12px',
                  width: '320px',
                  background: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '12px',
                  boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)',
                  zIndex: 1001,
                  padding: '16px'
                }}>
                  <div style={{
                    fontSize: '14px',
                    fontWeight: 'bold',
                    color: '#1e293b',
                    marginBottom: '12px',
                    borderBottom: '1px solid #e2e8f0',
                    paddingBottom: '8px'
                  }}>
                    💡 Search Examples:
                  </div>
                  <div style={{ fontSize: '13px', color: '#64748b', lineHeight: '1.6' }}>
                    {suggestions.map((suggestion, idx) => (
                      <div
                        key={idx}
                        onClick={() => {
                          setSearchQuery(suggestion);
                          handleSearch(suggestion, 'text');
                          setShowHelp(false);
                        }}
                        style={{
                          padding: '6px 8px',
                          cursor: 'pointer',
                          borderRadius: '6px',
                          marginBottom: '4px',
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background = '#f1f5f9';
                          e.currentTarget.style.color = '#1e293b';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background = 'transparent';
                          e.currentTarget.style.color = '#64748b';
                        }}
                      >
                        • {suggestion}
                      </div>
                    ))}
                  </div>
                  {/* Tooltip Arrow */}
                  <div style={{
                    position: 'absolute',
                    top: '-6px',
                    right: '20px',
                    width: '12px',
                    height: '12px',
                    background: 'white',
                    border: '1px solid #e2e8f0',
                    borderBottom: 'none',
                    borderRight: 'none',
                    transform: 'rotate(45deg)'
                  }} />
                </div>
              )}
            </div>

            {/* Voice Button */}
            <button
              onClick={isListening ? stopListening : startListening}
              style={{
                background: isListening ? '#ef4444' : '#10b981',
                border: 'none',
                color: 'white',
                cursor: 'pointer',
                padding: '8px',
                display: 'flex',
                alignItems: 'center',
                borderRadius: '8px',
                transition: 'background 0.2s'
              }}
              title={isListening ? "Stop listening" : "Voice search"}
            >
              {isListening ? <MicOff size={18} /> : <Mic size={18} />}
            </button>
            {/* Search Button */}
            <button
              onClick={() => handleSearch(searchQuery, 'text')}
              disabled={!searchQuery.trim()}
              style={{
                background: searchQuery.trim() ? '#3b82f6' : '#94a3b8',
                border: 'none',
                color: 'white',
                cursor: searchQuery.trim() ? 'pointer' : 'not-allowed',
                padding: '8px 16px',
                display: 'flex',
                alignItems: 'center',
                borderRadius: '8px',
                transition: 'background 0.2s',
                fontSize: '14px',
                fontWeight: '600'
              }}
            >
              <Search size={18} />
            </button>
          </div>
        </div>

        {/* User Menu */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button style={{
            background: 'none',
            border: '1px solid #334155',
            color: 'white',
            padding: '8px 16px',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <Bell size={18} />
            <span style={{
              background: '#ef4444',
              borderRadius: '50%',
              width: '8px',
              height: '8px',
              position: 'relative',
              top: '-8px',
              right: '0'
            }} />
          </button>

          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 'bold',
            cursor: 'pointer'
          }}>
            U
          </div>
        </div>
      </nav>

      {/* Side Navigation Menu */}
      <div style={{
        position: 'fixed',
        top: '64px',
        left: 0,
        bottom: 0,
        width: isMenuOpen ? '280px' : '0',
        background: 'linear-gradient(180deg, #1e293b 0%, #0f172a 100%)',
        borderRight: isMenuOpen ? '1px solid #334155' : 'none',
        overflowY: 'auto',
        overflowX: 'hidden',
        transition: 'width 0.3s ease',
        zIndex: 999
      }}>
        {isMenuOpen && (
          <div style={{ padding: '20px 0' }}>
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentView === item.id || currentView.startsWith(`${item.id}-`);
              const hasDropdown = item.submenu && item.submenu.length > 0;
              const isDropdownOpen = activeDropdown === item.id;

              return (
                <div key={item.id} style={{ marginBottom: '4px' }}>
                  {/* Main Menu Item */}
                  <div
                    onClick={() => handleItemClick(item)}
                    style={{
                      padding: '12px 20px',
                      color: isActive ? '#10b981' : '#94a3b8',
                      background: isActive ? 'rgba(16, 185, 129, 0.1)' : 'transparent',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      transition: 'all 0.2s',
                      borderLeft: isActive ? '3px solid #10b981' : '3px solid transparent'
                    }}
                    onMouseEnter={(e) => {
                      if (!isActive) e.currentTarget.style.background = '#334155';
                    }}
                    onMouseLeave={(e) => {
                      if (!isActive) e.currentTarget.style.background = 'transparent';
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <Icon size={20} />
                      <span style={{ fontWeight: isActive ? 'bold' : 'normal' }}>
                        {item.label}
                      </span>
                      {item.badge && (
                        <span style={{
                          background: item.badge === 'NEW' ? '#3b82f6' : '#10b981',
                          color: 'white',
                          fontSize: '10px',
                          padding: '2px 6px',
                          borderRadius: '4px',
                          fontWeight: 'bold'
                        }}>
                          {item.badge}
                        </span>
                      )}
                    </div>
                    {hasDropdown && (
                      <ChevronDown
                        size={16}
                        style={{
                          transform: isDropdownOpen ? 'rotate(180deg)' : 'rotate(0)',
                          transition: 'transform 0.2s'
                        }}
                      />
                    )}
                  </div>

                  {/* Submenu */}
                  {hasDropdown && isDropdownOpen && (
                    <div style={{
                      background: '#0a0e1a',
                      borderLeft: '2px solid #334155',
                      marginLeft: '20px'
                    }}>
                      {item.submenu.map((subitem) => {
                        const SubIcon = subitem.icon;
                        const isSubActive = currentView === `${item.id}-${subitem.id}`;

                        return (
                          <div
                            key={subitem.id}
                            onClick={() => handleSubmenuClick(item.id, subitem.id)}
                            style={{
                              padding: '10px 20px',
                              color: isSubActive ? '#10b981' : '#94a3b8',
                              background: isSubActive ? 'rgba(16, 185, 129, 0.05)' : 'transparent',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '12px',
                              fontSize: '14px',
                              transition: 'all 0.2s'
                            }}
                            onMouseEnter={(e) => {
                              if (!isSubActive) e.currentTarget.style.background = '#1e293b';
                            }}
                            onMouseLeave={(e) => {
                              if (!isSubActive) e.currentTarget.style.background = 'transparent';
                            }}
                          >
                            <SubIcon size={16} />
                            <span>{subitem.label}</span>
                            {subitem.badge && (
                              <span style={{
                                background: subitem.badge === 'NEW' ? '#3b82f6' : '#8b5cf6',
                                color: 'white',
                                fontSize: '9px',
                                padding: '2px 4px',
                                borderRadius: '3px',
                                fontWeight: 'bold',
                                marginLeft: 'auto'
                              }}>
                                {subitem.badge}
                              </span>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Mobile Overlay */}
      {isMenuOpen && window.innerWidth < 1024 && (
        <div
          onClick={onMenuToggle}
          style={{
            position: 'fixed',
            top: '64px',
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            zIndex: 998
          }}
        />
      )}
    </>
  );
};

export default Navigation;
