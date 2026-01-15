import React, { useState } from 'react';
import { TrendingUp, TrendingDown, Activity, DollarSign, BarChart3, Settings, History, Clock, Users, Target, Zap, Brain, AlertCircle } from 'lucide-react';

export default function AIAlgoTradeHits() {
  const [activeTab, setActiveTab] = useState('crypto');
  const [autoTrading, setAutoTrading] = useState(false);

  // Mock data for crypto
  const cryptoData = [
    { symbol: 'BTC', name: 'Bitcoin', price: 43250.50, daily: 2.34, hourly: 0.45, monthly: 15.2, trades: 1234, buy: 678, sell: 556, traders: 3421, atLowest: false, sentiment: 73 },
    { symbol: 'ETH', name: 'Ethereum', price: 2280.75, daily: 1.89, hourly: 0.32, monthly: 12.8, trades: 2341, buy: 1203, sell: 1138, traders: 2890, atLowest: true, sentiment: 68 },
    { symbol: 'BNB', name: 'Binance', price: 312.40, daily: 0.92, hourly: -0.15, monthly: 8.5, trades: 876, buy: 445, sell: 431, traders: 1567, atLowest: false, sentiment: 65 },
    { symbol: 'SOL', name: 'Gainer #1', price: 98.35, daily: 8.45, hourly: 2.34, monthly: 45.2, trades: 1567, buy: 989, sell: 578, traders: 2134, atLowest: true, sentiment: 85 },
    { symbol: 'AVAX', name: 'Gainer #2', price: 36.78, daily: 6.23, hourly: 1.87, monthly: 32.1, trades: 892, buy: 567, sell: 325, traders: 1456, atLowest: false, sentiment: 78 },
    { symbol: 'MATIC', name: 'Gainer #3', price: 0.89, daily: 5.67, hourly: 1.23, monthly: 28.4, trades: 1234, buy: 756, sell: 478, traders: 1789, atLowest: true, sentiment: 72 },
    { symbol: 'DOT', name: 'Gainer #4', price: 7.23, daily: 4.91, hourly: 0.98, monthly: 22.6, trades: 678, buy: 401, sell: 277, traders: 987, atLowest: false, sentiment: 70 },
    { symbol: 'ADA', name: 'Loser #1', price: 0.52, daily: -3.21, hourly: -0.87, monthly: -12.3, trades: 1567, buy: 623, sell: 944, traders: 1345, atLowest: false, sentiment: 35 },
    { symbol: 'XRP', name: 'Loser #2', price: 0.61, daily: -2.87, hourly: -0.65, monthly: -8.9, trades: 2345, buy: 891, sell: 1454, traders: 1892, atLowest: false, sentiment: 42 },
    { symbol: 'DOGE', name: 'Loser #3', price: 0.08, daily: -2.34, hourly: -0.43, monthly: -15.6, trades: 3456, buy: 1234, sell: 2222, traders: 2567, atLowest: false, sentiment: 38 },
  ];

  // Mock data for stocks
  const stockData = [
    { symbol: 'SPY', name: 'S&P 500 ETF', price: 445.23, daily: 0.87, hourly: 0.23, monthly: 5.2, trades: 5234, buy: 2878, sell: 2356, traders: 8421, atLowest: false, sentiment: 65 },
    { symbol: 'QQQ', name: 'Nasdaq ETF', price: 378.45, daily: 1.23, hourly: 0.45, monthly: 8.7, trades: 4567, buy: 2534, sell: 2033, traders: 6890, atLowest: false, sentiment: 72 },
    { symbol: 'DIA', name: 'Dow ETF', price: 356.78, daily: 0.56, hourly: 0.12, monthly: 3.4, trades: 2341, buy: 1203, sell: 1138, traders: 4230, atLowest: false, sentiment: 58 },
    { symbol: 'NVDA', name: 'Gainer #1', price: 485.67, daily: 5.34, hourly: 1.87, monthly: 22.3, trades: 6789, buy: 4234, sell: 2555, traders: 9876, atLowest: true, sentiment: 88 },
    { symbol: 'TSLA', name: 'Gainer #2', price: 245.89, daily: 4.23, hourly: 1.34, monthly: 18.9, trades: 8901, buy: 5234, sell: 3667, traders: 12345, atLowest: false, sentiment: 82 },
    { symbol: 'AMD', name: 'Gainer #3', price: 167.34, daily: 3.67, hourly: 1.12, monthly: 15.4, trades: 3456, buy: 2134, sell: 1322, traders: 6543, atLowest: true, sentiment: 76 },
    { symbol: 'AAPL', name: 'Gainer #4', price: 178.23, daily: 2.89, hourly: 0.87, monthly: 12.6, trades: 5678, buy: 3234, sell: 2444, traders: 8765, atLowest: false, sentiment: 74 },
    { symbol: 'META', name: 'Loser #1', price: 387.45, daily: -2.34, hourly: -0.76, monthly: -8.3, trades: 4321, buy: 1876, sell: 2445, traders: 7654, atLowest: false, sentiment: 42 },
    { symbol: 'NFLX', name: 'Loser #2', price: 456.12, daily: -1.87, hourly: -0.54, monthly: -6.7, trades: 2345, buy: 987, sell: 1358, traders: 4567, atLowest: false, sentiment: 38 },
    { symbol: 'DIS', name: 'Loser #3', price: 98.76, daily: -1.45, hourly: -0.43, monthly: -5.2, trades: 3210, buy: 1234, sell: 1976, traders: 5432, atLowest: false, sentiment: 35 },
  ];

  const currentData = activeTab === 'crypto' ? cryptoData : stockData;

  const trumpPost = {
    text: "Great things happening with American innovation and technology! 🚀",
    time: "2 hours ago",
    sentiment: 85,
    impact: "HIGH",
    mentioned: ["BTC", "TSLA", "NVDA"]
  };

  const marketStatus = {
    isOpen: true,
    nextOpen: "Tomorrow at 9:30 AM EST",
    currentTime: "2:45 PM EST"
  };

  return (
    <div className="h-screen flex flex-col bg-slate-950 text-slate-100">
      {/* Header */}
      <header className="bg-gradient-to-r from-slate-900 via-blue-900 to-slate-900 border-b border-blue-800 px-6 py-3">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 via-blue-600 to-purple-600 rounded-lg flex items-center justify-center transform rotate-45">
                <div className="transform -rotate-45">
                  <TrendingUp className="w-7 h-7 text-white" strokeWidth={3} />
                </div>
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full flex items-center justify-center">
                <Target className="w-2.5 h-2.5 text-slate-900" />
              </div>
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                AIAlgoTradeHits.com
              </h1>
              <p className="text-xs text-blue-300">AI-Powered Trading at the Perfect Moment</p>
            </div>
          </div>

          {/* Stats */}
          <div className="flex items-center gap-8">
            <div className="text-right">
              <p className="text-xs text-slate-400">Total Portfolio</p>
              <p className="text-2xl font-bold text-green-400">$25,687.34</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-slate-400">Today's P&L</p>
              <p className="text-lg font-semibold text-green-400">+$567.82 (2.26%)</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-slate-400 flex items-center gap-1">
                <Brain className="w-3 h-3" />
                AI Confidence
              </p>
              <p className="text-lg font-semibold text-yellow-400">87%</p>
            </div>
            <div className="w-10 h-10 bg-slate-800 rounded-full flex items-center justify-center border-2 border-blue-500">
              <Users className="w-5 h-5 text-blue-400" />
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        <aside className="w-56 bg-slate-900 border-r border-slate-800 p-4">
          <nav className="space-y-2">
            <button className="w-full flex items-center gap-3 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg">
              <Activity className="w-4 h-4" />
              <span className="text-sm font-medium">Dashboard</span>
            </button>
            <button className="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-slate-800 text-slate-300">
              <Zap className="w-4 h-4" />
              <span className="text-sm font-medium">Live Trading</span>
            </button>
            <button className="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-slate-800 text-slate-300">
              <History className="w-4 h-4" />
              <span className="text-sm font-medium">Trade History</span>
            </button>
            <button className="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-slate-800 text-slate-300">
              <DollarSign className="w-4 h-4" />
              <span className="text-sm font-medium">Deposits</span>
            </button>
            <button className="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-slate-800 text-slate-300">
              <BarChart3 className="w-4 h-4" />
              <span className="text-sm font-medium">Reports</span>
            </button>
            <button className="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-slate-800 text-slate-300">
              <Settings className="w-4 h-4" />
              <span className="text-sm font-medium">Settings</span>
            </button>
          </nav>

          {/* Quick Stats */}
          <div className="mt-8 p-4 bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg border border-slate-700">
            <p className="text-xs text-slate-400 mb-3 flex items-center gap-1">
              <Target className="w-3 h-3" />
              Today's Stats
            </p>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-xs text-slate-400">Trades</span>
                <span className="text-sm font-bold">38</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-slate-400">Win Rate</span>
                <span className="text-sm font-bold text-green-400">81.6%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-slate-400">Active</span>
                <span className="text-sm font-bold text-blue-400">5</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-slate-400">At Lowest</span>
                <span className="text-sm font-bold text-yellow-400">4</span>
              </div>
            </div>
          </div>

          {/* Market Status (for stocks) */}
          {activeTab === 'stock' && (
            <div className="mt-4 p-3 bg-green-950 border border-green-800 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-xs font-bold text-green-400">MARKET OPEN</span>
              </div>
              <p className="text-xs text-slate-400">{marketStatus.currentTime}</p>
            </div>
          )}
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
          {/* Tab Selector */}
          <div className="bg-slate-900 border-b border-slate-800 px-6 py-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setActiveTab('crypto')}
                className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                  activeTab === 'crypto'
                    ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg scale-105'
                    : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                }`}
              >
                <span className="flex items-center gap-2">
                  <Activity className="w-4 h-4" />
                  CRYPTOCURRENCY
                </span>
              </button>
              <button
                onClick={() => setActiveTab('stock')}
                className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                  activeTab === 'stock'
                    ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg scale-105'
                    : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                }`}
              >
                <span className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  STOCKS
                </span>
              </button>
              <div className="flex-1"></div>
              <div className="text-xs text-slate-400">
                <span className="font-mono">{activeTab === 'crypto' ? '24/7 Trading' : 'Market Hours: Mon-Fri 9:30AM-4PM EST'}</span>
              </div>
            </div>
          </div>

          <div className="p-6">
            {/* Sentiment Analysis Panel */}
            <div className="mb-6 bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg p-5 border border-slate-700 shadow-xl">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold flex items-center gap-2">
                  <Brain className="w-5 h-5 text-purple-400" />
                  AI Sentiment Analysis
                </h3>
                <span className="px-3 py-1 bg-green-600 rounded-full text-xs font-bold">STRONG BUY</span>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-slate-400">Overall Sentiment</span>
                    <span className="text-lg font-bold text-green-400">73% BULLISH</span>
                  </div>
                  <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-green-500 to-green-400" style={{width: '73%'}}></div>
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-slate-400">AI Confidence</span>
                    <span className="text-lg font-bold text-yellow-400">87%</span>
                  </div>
                  <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-yellow-500 to-yellow-400" style={{width: '87%'}}></div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-4 gap-3 mb-4">
                <div className="bg-slate-800 rounded p-3 border border-slate-700">
                  <p className="text-xs text-slate-400 mb-1">{activeTab === 'crypto' ? 'CoinMarketCap' : 'Market News'}</p>
                  <p className="text-sm font-bold text-green-400">68%</p>
                </div>
                <div className="bg-slate-800 rounded p-3 border border-slate-700">
                  <p className="text-xs text-slate-400 mb-1">Trump Posts</p>
                  <p className="text-sm font-bold text-green-400">85%</p>
                </div>
                <div className="bg-slate-800 rounded p-3 border border-slate-700">
                  <p className="text-xs text-slate-400 mb-1">Social Media</p>
                  <p className="text-sm font-bold text-green-400">71%</p>
                </div>
                <div className="bg-slate-800 rounded p-3 border border-slate-700">
                  <p className="text-xs text-slate-400 mb-1">Analyst Ratings</p>
                  <p className="text-sm font-bold text-green-400">76%</p>
                </div>
              </div>

              {/* Trump Post */}
              <div className="bg-blue-950 border border-blue-800 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold">
                    T
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-bold text-sm">@realDonaldTrump</span>
                      <span className="text-xs text-slate-400">{trumpPost.time}</span>
                      <span className="px-2 py-0.5 bg-red-600 rounded text-xs font-bold">HIGH IMPACT</span>
                    </div>
                    <p className="text-sm mb-2">{trumpPost.text}</p>
                    <div className="flex items-center gap-3 text-xs">
                      <span className="text-slate-400">Sentiment: <span className="text-green-400 font-bold">+{trumpPost.sentiment}%</span></span>
                      <span className="text-slate-400">Mentioned: <span className="text-blue-400 font-bold">{trumpPost.mentioned.join(', ')}</span></span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Multi-Timeframe Charts */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              {['Daily', 'Hourly', '5-Minute'].map((timeframe, idx) => (
                <div key={timeframe} className={`bg-slate-900 rounded-lg p-4 border ${idx === 2 ? 'border-green-600 border-2 shadow-lg shadow-green-900/50' : 'border-slate-800'}`}>
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-semibold">{timeframe} Chart</h3>
                    {idx === 2 && <span className="px-2 py-0.5 bg-green-600 text-xs rounded animate-pulse">ACTIVE</span>}
                  </div>
                  <div className="h-40 bg-slate-950 rounded flex items-center justify-center relative overflow-hidden">
                    <div className="absolute inset-0 flex items-end justify-around px-1 py-4">
                      {[...Array(idx === 2 ? 20 : idx === 1 ? 16 : 12)].map((_, i) => {
                        const height = 40 + Math.random() * 60;
                        const isLowest = idx === 2 && (i === 14 || i === 8);
                        return (
                          <div key={i} className="flex flex-col items-center justify-end relative" style={{width: `${100/(idx === 2 ? 20 : idx === 1 ? 16 : 12)}%`}}>
                            <div 
                              className={`w-full ${i % 3 === 0 ? 'bg-green-500' : 'bg-red-500'} ${isLowest ? 'bg-yellow-400 shadow-lg shadow-yellow-500' : ''}`}
                              style={{height: `${height}%`}}
                            ></div>
                            {isLowest && (
                              <div className="absolute -top-6 bg-yellow-400 text-slate-900 text-xs px-2 py-0.5 rounded font-bold whitespace-nowrap">
                                BUY
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                  <div className="grid grid-cols-4 gap-2 mt-3 text-xs">
                    <div><p className="text-slate-400">Vol</p><p className="font-semibold">$2.1B</p></div>
                    <div><p className="text-slate-400">Buy</p><p className="font-semibold text-green-400">1.2K</p></div>
                    <div><p className="text-slate-400">Sell</p><p className="font-semibold text-red-400">987</p></div>
                    <div><p className="text-slate-400">Traders</p><p className="font-semibold">3.4K</p></div>
                  </div>
                </div>
              ))}
            </div>

            {/* Asset Performance Grid */}
            <div className="mb-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Target className="w-5 h-5 text-blue-400" />
                {activeTab === 'crypto' ? 'Cryptocurrency' : 'Stock'} Performance Dashboard
              </h2>
              <div className="grid grid-cols-5 gap-3">
                {currentData.map((asset, index) => (
                  <div 
                    key={asset.symbol} 
                    className={`bg-slate-900 rounded-lg p-3 border transition-all ${
                      asset.atLowest 
                        ? 'border-yellow-500 border-2 shadow-lg shadow-yellow-900/50 bg-gradient-to-br from-slate-900 to-yellow-900/20' 
                        : asset.daily >= 0 
                        ? 'border-slate-800' 
                        : 'border-red-900'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                          asset.atLowest ? 'bg-yellow-500 text-slate-900' : asset.daily >= 0 ? 'bg-green-600' : 'bg-red-600'
                        }`}>
                          {asset.symbol.substring(0, 2)}
                        </div>
                        <div>
                          <p className="text-xs font-bold">{asset.symbol}</p>
                          <p className="text-xs text-slate-400">{asset.name}</p>
                        </div>
                      </div>
                      {asset.atLowest && (
                        <div className="flex flex-col items-center">
                          <TrendingUp className="w-4 h-4 text-yellow-400 animate-bounce" />
                          <span className="text-xs text-yellow-400 font-bold">LOW</span>
                        </div>
                      )}
                    </div>

                    {/* Mini Chart */}
                    <div className="h-10 mb-2 flex items-end justify-around">
                      {[...Array(10)].map((_, i) => (
                        <div 
                          key={i} 
                          className={`w-1 ${asset.daily >= 0 ? 'bg-green-500' : 'bg-red-500'}`}
                          style={{height: `${40 + Math.random() * 60}%`, opacity: 0.7}}
                        ></div>
                      ))}
                    </div>

                    <p className="text-base font-bold mb-1">${asset.price.toLocaleString()}</p>
                    <p className={`text-sm font-semibold mb-2 ${asset.daily >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {asset.daily >= 0 ? '+' : ''}{asset.daily}% (24h)
                    </p>

                    {/* Sentiment Bar */}
                    <div className="mb-2">
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-slate-400">Sentiment</span>
                        <span className={`font-bold ${asset.sentiment > 60 ? 'text-green-400' : asset.sentiment > 40 ? 'text-yellow-400' : 'text-red-400'}`}>
                          {asset.sentiment}%
                        </span>
                      </div>
                      <div className="h-1 bg-slate-700 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${asset.sentiment > 60 ? 'bg-green-500' : asset.sentiment > 40 ? 'bg-yellow-500' : 'bg-red-500'}`}
                          style={{width: `${asset.sentiment}%`}}
                        ></div>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-1 text-xs mb-2 border-t border-slate-800 pt-2">
                      <div className="text-center">
                        <p className="text-slate-500">Day</p>
                        <p className={`font-semibold ${asset.daily >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {asset.daily >= 0 ? '+' : ''}{asset.daily}%
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-slate-500">Hour</p>
                        <p className={`font-semibold ${asset.hourly >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {asset.hourly >= 0 ? '+' : ''}{asset.hourly}%
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-slate-500">Month</p>
                        <p className={`font-semibold ${asset.monthly >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {asset.monthly >= 0 ? '+' : ''}{asset.monthly}%
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-1 text-xs">
                      <div><p className="text-slate-500">Trades</p><p className="font-semibold">{asset.trades}</p></div>
                      <div><p className="text-slate-500">Traders</p><p className="font-semibold">{asset.traders}</p></div>
                      <div><p className="text-slate-500">Buy</p><p className="font-semibold text-green-400">{asset.buy}</p></div>
                      <div><p className="text-slate-500">Sell</p><p className="font-semibold text-red-400">{asset.sell}</p></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </main>

        {/* Right Sidebar */}
        <aside className="w-80 bg-slate-900 border-l border-slate-800 p-4 space-y-4 overflow-y-auto">
          {/* Trade Setup */}
          <div className="bg-gradient-to-br from-slate-950 to-slate-900 rounded-lg p-4 border border-slate-700 shadow-xl">
            <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
              <Zap className="w-4 h-4 text-yellow-400" />
              AI Trade Setup
            </h3>
            
            <div className="space-y-3">
              <div>
                <label className="text-xs text-slate-400 block mb-1">Asset Type</label>
                <div className="grid grid-cols-2 gap-2">
                  <button className={`px-3 py-2 rounded text-xs font-semibold ${activeTab === 'crypto' ? 'bg-blue-600' : 'bg-slate-800'}`}>
                    Crypto
                  </button>
                  <button className={`px-3 py-2 rounded text-xs font-semibold ${activeTab === 'stock' ? 'bg-purple-600' : 'bg-slate-800'}`}>
                    Stock
                  </button>
                </div>
              </div>

              <div>
                <label className="text-xs text-slate-400 block mb-1">Symbol</label>
                <select className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm">
                  {currentData.slice(0, 5).map(asset => (
                    <option key={asset.symbol}>{asset.symbol}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs text-slate-400 block mb-1">Trade Amount (USD)</label>
                <input 
                  type="number" 
                  placeholder="500.00" 
                  className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm"
                  defaultValue="500"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Take Profit %</label>
                  <input 
                    type="number" 
                    className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm"
                    defaultValue="3.00"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Stop Loss %</label>
                  <input 
                    type="number" 
                    className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm"
                    defaultValue="1.50"
                  />
                </div>
              </div>

              <div className="bg-blue-950 border border-blue-800 rounded p-3">
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle className="w-4 h-4 text-blue-400" />
                  <span className="text-xs font-bold text-blue-400">AI Strategy</span>
                </div>
                <div className="space-y-1 text-xs text-slate-300">
                  <div className="flex items-center gap-2">
                    <input type="checkbox" defaultChecked className="rounded" />
                    <span>Only buy at lowest points</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <input type="checkbox" defaultChecked className="rounded" />
                    <span>Wait for positive sentiment</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <input type="checkbox" defaultChecked className="rounded" />
                    <span>Consider Trump announcements</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 bg-slate-800 rounded">
                <span className="text-sm font-medium">Auto-Trading</span>
                <button 
                  onClick={() => setAutoTrading(!autoTrading)}
                  className={`relative w-12 h-6 rounded-full transition-colors ${autoTrading ? 'bg-green-600' : 'bg-slate-700'}`}
                >
                  <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${autoTrading ? 'translate-x-6' : ''}`}></div>
                </button>
              </div>

              <button className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white font-semibold py-2.5 rounded-lg shadow-lg">
                Start AI Trading
              </button>
            </div>
          </div>

          {/* Assets at Lowest Points */}
          <div className="bg-gradient-to-br from-yellow-950 to-slate-900 rounded-lg p-4 border border-yellow-800">
            <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
              <Target className="w-4 h-4 text-yellow-400" />
              <span>At Lowest Points (Buy Zone)</span>
            </h3>
            <div className="space-y-2">
              {currentData.filter(a => a.atLowest).map(asset => (
                <div key={asset.symbol} className="bg-slate-900 rounded p-2 border border-yellow-700">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-sm">{asset.symbol}</span>
                    <span className="text-xs bg-yellow-500 text-slate-900 px-2 py-0.5 rounded font-bold">BUY NOW</span>
                  </div>
                  <div className="text-xs text-slate-400">
                    <p>Price: ${asset.price.toLocaleString()}</p>
                    <p>Sentiment: <span className="text-green-400">{asset.sentiment}%</span></p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Active Positions */}
          <div className="bg-slate-950 rounded-lg p-4 border border-slate-800">
            <h3 className="text-sm font-semibold mb-3">Active Positions (3)</h3>
            <div className="space-y-2">
              {[
                { symbol: activeTab === 'crypto' ? 'BTC' : 'NVDA', entry: activeTab === 'crypto' ? 43100 : 482.50, current: activeTab === 'crypto' ? 43250 : 485.67, pl: activeTab === 'crypto' ? 150 : 3.17 },
                { symbol: activeTab === 'crypto' ? 'ETH' : 'AMD', entry: activeTab === 'crypto' ? 2275 : 165.20, current: activeTab === 'crypto' ? 2281 : 167.34, pl: activeTab === 'crypto' ? 6 : 2.14 },
                { symbol: activeTab === 'crypto' ? 'SOL' : 'TSLA', entry: activeTab === 'crypto' ? 96.5 : 243.20, current: activeTab === 'crypto' ? 98.35 : 245.89, pl: activeTab === 'crypto' ? 1.85 : 2.69 }
              ].map(pos => (
                <div key={pos.symbol} className="bg-slate-900 rounded p-3 border border-green-900">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold">{pos.symbol}</span>
                    <span className="text-xs bg-green-900 px-2 py-0.5 rounded">OPEN</span>
                  </div>
                  <div className="text-xs space-y-1">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Entry</span>
                      <span>${pos.entry}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Current</span>
                      <span>${pos.current}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">P&L</span>
                      <span className="text-green-400 font-semibold">+${pos.pl.toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}