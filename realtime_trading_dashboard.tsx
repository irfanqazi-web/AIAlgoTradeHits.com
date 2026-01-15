import React, { useState, useEffect, useCallback } from 'react';
import { TrendingUp, TrendingDown, Activity, Target, AlertTriangle, Bell, Zap, Eye } from 'lucide-react';

const RealTimeTradingDashboard = () => {
  const [symbols] = useState(['BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD']);
  const [selectedSymbol, setSelectedSymbol] = useState('BTC-USD');
  const [minuteData, setMinuteData] = useState({});
  const [currentSignals, setCurrentSignals] = useState([]);
  const [bullRunAlerts, setBullRunAlerts] = useState([]);
  const [sentimentData, setSentimentData] = useState({});
  const [newsItems, setNewsItems] = useState([]);
  const [isMonitoring, setIsMonitoring] = useState(false);
  
  // Simulate real-time data updates with enhanced volume and trade flow data
  useEffect(() => {
    const generateMinuteData = (symbol, prevData) => {
      const lastPrice = prevData?.close || (symbol === 'BTC-USD' ? 43000 : symbol === 'ETH-USD' ? 2600 : symbol === 'SOL-USD' ? 95 : 0.48);
      
      // Simulate bull run probability for realistic patterns
      const bullRunSetup = Math.random() > 0.9; // 10% chance of bull setup
      const change = bullRunSetup ? 
        Math.random() * 0.02 + 0.005 :  // 0.5% to 2.5% for bull setup
        (Math.random() - 0.5) * 0.03;   // ±1.5% for normal
      
      const newPrice = lastPrice * (1 + change);
      
      const volatility = Math.random() * 0.015 + 0.002; // 0.2% to 1.7%
      const high = newPrice * (1 + volatility);
      const low = newPrice * (1 - volatility);
      
      // Enhanced volume simulation
      const prevVolume = prevData?.volume || 500;
      const volumeMultiplier = bullRunSetup ? 
        1.5 + Math.random() * 2.0 :  // 1.5x to 3.5x for bull setup
        0.8 + Math.random() * 0.6;   // 0.8x to 1.4x normal
      
      const volume = prevVolume * volumeMultiplier;
      
      // Trade flow simulation
      const totalTrades = Math.floor(volume / (3 + Math.random() * 5)); // Varying trade sizes
      const buyBias = bullRunSetup ? 
        0.6 + Math.random() * 0.2 :  // 60-80% buy bias for bull setup
        0.45 + Math.random() * 0.1;  // 45-55% normal
      
      const buyCount = Math.floor(totalTrades * buyBias);
      const sellCount = totalTrades - buyCount;
      
      // Trader participation
      const prevTraders = prevData?.traderCount || 800;
      const traderGrowth = bullRunSetup ? 
        1.1 + Math.random() * 0.4 :  // 10-50% growth for bull setup
        0.95 + Math.random() * 0.1;  // ±5% normal
      
      const traderCount = Math.floor(prevTraders * traderGrowth);
      
      // Volume split between buy/sell
      const buyVolume = volume * (buyBias + (Math.random() - 0.5) * 0.1);
      const sellVolume = volume - buyVolume;
      
      // Calculate %Gain
      const percentGain = ((high - low) / low) * 100;
      
      // Simulate CSI and RSI with correlation to volume and trade flow
      const time = Date.now() / 10000;
      const volumeBoost = Math.min((volume / 1000), 0.2); // Volume influence
      const buyPressureBoost = (buyBias - 0.5) * 20; // Buy pressure influence
      
      const csi = 50 + 30 * Math.sin(time * 0.001 + Math.random() * 0.1) + 
                  volumeBoost * 50 + buyPressureBoost + Math.random() * 8 - 4;
      const rsi = 50 + 25 * Math.sin(time * 0.0008 + 0.5 + Math.random() * 0.1) + 
                  buyPressureBoost * 0.5 + Math.random() * 6 - 3;
      
      // Calculate %BB with volatility influence
      const bbBase = 6 + 8 * Math.abs(Math.sin(time * 0.0005)) + (percentGain * 0.3);
      const percentBB = bbBase + Math.random() * 4 - 2;
      
        // Enhanced sentiment analysis with news integration
        const newsSentimentBase = Math.sin(time * 0.0003) + Math.random() * 0.4 - 0.2;
        
        // Simulate Trump influence (occasional spikes)
        const trumpInfluence = Math.random() > 0.95 ? (Math.random() - 0.5) * 2 : 0;
        
        // Simulate regulatory influence (SEC/CFTC)
        const regulatoryInfluence = Math.random() > 0.98 ? (Math.random() - 0.5) * 1.5 : 0;
        
        // BTC correlation for other cryptos
        const btcCorrelationInfluence = symbol !== 'BTC-USD' ? 
          newsSentimentBase * 0.6 + Math.random() * 0.2 - 0.1 : 0;
        
        // Overall sentiment score
        const overallSentiment = Math.max(-1, Math.min(1,
          newsSentimentBase * 0.4 +
          trumpInfluence * 0.3 +
          regulatoryInfluence * 0.2 +
          btcCorrelationInfluence * 0.1
        ));
        
        // News volume simulation
        const newsVolume = Math.floor(Math.random() * 15) + 2;
        
        // Sentiment category
        let sentimentCategory = 'NEUTRAL';
        if (overallSentiment > 0.4) sentimentCategory = 'VERY_POSITIVE';
        else if (overallSentiment > 0.15) sentimentCategory = 'POSITIVE';
        else if (overallSentiment < -0.4) sentimentCategory = 'VERY_NEGATIVE';
        else if (overallSentiment < -0.15) sentimentCategory = 'NEGATIVE';
        
        // Enhanced bull run probability with sentiment integration
        const technicalProb = (volumeFactor * 0.15) + (tradeFactor * 0.15) + 
                              (traderFactor * 0.1) + (volatilityFactor * 0.1);
        
        const sentimentProb = Math.max(0, (overallSentiment + 1) / 2); // Convert -1,1 to 0,1
        
        // Combine technical and sentiment probabilities
        const combinedBullRunProb = Math.max(0, Math.min(1,
          technicalProb * 0.7 +     // Technical factors: 70%
          sentimentProb * 0.2 +     // Sentiment factors: 20%
          ((csi > 55 ? 0.05 : 0)) + // CSI bonus: 5%
          ((rsi > 45 && rsi < 75 ? 0.05 : 0)) // RSI bonus: 5%
        ));
        
        // Trump impact boost/penalty
        let trumpAdjustment = 0;
        if (Math.abs(trumpInfluence) > 0.3) {
          trumpAdjustment = trumpInfluence > 0 ? 0.15 : -0.12;
        }
        
        // Regulatory impact
        let regulatoryAdjustment = 0;
        if (Math.abs(regulatoryInfluence) > 0.4) {
          regulatoryAdjustment = regulatoryInfluence > 0 ? 0.2 : -0.18;
        }
        
        const finalBullRunProb = Math.max(0, Math.min(1,
          combinedBullRunProb + trumpAdjustment + regulatoryAdjustment
        ));
      
      return {
        timestamp: new Date(),
        symbol,
        open: lastPrice,
        high: Math.max(high, newPrice),
        low: Math.min(low, newPrice),
        close: newPrice,
        volume: volume,
        
        // Enhanced trade flow data
        buyCount: buyCount,
        sellCount: sellCount,
        totalTrades: totalTrades,
        traderCount: traderCount,
        buyVolume: buyVolume,
        sellVolume: sellVolume,
        
        // Calculated metrics
        percentGain: percentGain,
        percentBB: percentBB,
        csi: Math.max(0, Math.min(100, csi)),
        rsi: Math.max(0, Math.min(100, rsi)),
        bullRunProbability: finalBullRunProb,
        buySellRatio: buyCount / Math.max(sellCount, 1),
        buyVolumeRatio: buyVolume / Math.max(sellVolume, 1),
        avgTradeSize: volume / Math.max(totalTrades, 1),
        tradesPerTrader: totalTrades / Math.max(traderCount, 1),
        volumePerTrader: volume / Math.max(traderCount, 1),
        
        // Market condition flags
        volumeSurge: volumeMultiplier > 1.5,
        highParticipation: traderGrowth > 1.2,
        strongBuyPressure: buyBias > 0.65,
        institutionalActivity: (volume / Math.max(totalTrades, 1)) > 15,
        
        // Enhanced sentiment data
        overallSentiment: overallSentiment,
        sentimentCategory: sentimentCategory,
        newsSentiment: newsSentimentBase,
        trumpInfluence: trumpInfluence,
        regulatoryInfluence: regulatoryInfluence,
        btcCorrelationInfluence: btcCorrelationInfluence,
        newsVolume: newsVolume,
        sentimentConfidence: Math.random() * 0.4 + 0.6, // 0.6-1.0
        
        // News flags
        recentTrumpTweet: Math.abs(trumpInfluence) > 0.3,
        regulatoryNews: Math.abs(regulatoryInfluence) > 0.4,
        highNewsVolume: newsVolume > 10,
        positiveNewsMomentum: overallSentiment > 0.3,
        negativeNewsMomentum: overallSentiment < -0.3
      };
    };
    
    const detectCrossover = (newData, prevData) => {
      if (!prevData) return null;
      
      const csiAboveRsiNow = newData.csi > newData.rsi;
      const csiAboveRsiPrev = prevData.csi > prevData.rsi;
      
      if (csiAboveRsiNow !== csiAboveRsiPrev) {
        const strength = Math.abs(newData.csi - newData.rsi);
        
        let signalType = 'NEUTRAL';
        let signalColor = 'yellow';
        
        if (csiAboveRsiNow) { // CSI crossed above RSI
          if (newData.csi > 50 && newData.rsi > 40) {
            signalType = newData.csi > 65 ? 'STRONG_BUY' : 'BUY';
            signalColor = newData.csi > 65 ? 'green' : 'lightgreen';
          }
        } else { // CSI crossed below RSI
          if (newData.csi < 50 && newData.rsi < 60) {
            signalType = newData.csi < 35 ? 'STRONG_SELL' : 'SELL';
            signalColor = newData.csi < 35 ? 'red' : 'orange';
          }
        }
        
        // Enhance confidence with sentiment
        let baseConfidence = Math.min(1, (strength / 20 + newData.bullRunProbability * 0.4 + 0.3));
        
        // Sentiment boost to confidence
        if (newData.overallSentiment > 0.3 && signalType.includes('BUY')) {
          baseConfidence *= 1.2;
        } else if (newData.overallSentiment < -0.3 && signalType.includes('SELL')) {
          baseConfidence *= 1.2;
        }
        
        const confidence = Math.min(baseConfidence, 1.0);
        
        return {
          id: Date.now() + Math.random(),
          timestamp: newData.timestamp,
          symbol: newData.symbol,
          signalType,
          signalColor,
          csi: newData.csi,
          rsi: newData.rsi,
          crossoverStrength: strength,
          percentGain: newData.percentGain,
          percentBB: newData.percentBB,
          bullRunProbability: newData.bullRunProbability,
          confidence: confidence,
          entryPrice: newData.close,
          
          // Enhanced with sentiment
          sentimentScore: newData.overallSentiment,
          sentimentCategory: newData.sentimentCategory,
          trumpInfluence: newData.trumpInfluence,
          regulatoryInfluence: newData.regulatoryInfluence
        };
      }
      return null;
    };
    
    const generateNewsItem = (symbol) => {
      const newsTypes = [
        { type: 'trump', weight: 0.05, impact: 'high' },
        { type: 'sec', weight: 0.08, impact: 'high' },
        { type: 'cftc', weight: 0.03, impact: 'medium' },
        { type: 'market', weight: 0.3, impact: 'medium' },
        { type: 'technical', weight: 0.25, impact: 'low' },
        { type: 'adoption', weight: 0.15, impact: 'medium' },
        { type: 'general', weight: 0.14, impact: 'low' }
      ];
      
      // Select news type based on weights
      const rand = Math.random();
      let cumWeight = 0;
      let selectedType = 'general';
      
      for (const newsType of newsTypes) {
        cumWeight += newsType.weight;
        if (rand <= cumWeight) {
          selectedType = newsType.type;
          break;
        }
      }
      
      const headlines = {
        trump: [
          `Trump tweets about ${symbol.split('-')[0]}: "Great potential!"`,
          `Trump criticizes current crypto policies`,
          `Trump announces crypto-friendly stance`,
          `Trump questions Federal Reserve policy`
        ],
        sec: [
          `SEC announces new guidance on crypto regulations`,
          `SEC approves new crypto framework`,
          `SEC issues warning to crypto exchanges`,
          `SEC delays ETF decision for ${symbol.split('-')[0]}`
        ],
        cftc: [
          `CFTC clarifies digital commodity rules`,
          `CFTC approves crypto derivatives trading`,
          `CFTC issues enforcement action`
        ],
        market: [
          `${symbol.split('-')[0]} surges on institutional adoption`,
          `Major institutional investor buys ${symbol.split('-')[0]}`,
          `${symbol.split('-')[0]} breaks resistance level`,
          `Whale movement detected in ${symbol.split('-')[0]}`
        ],
        technical: [
          `${symbol.split('-')[0]} network upgrade completed`,
          `New scaling solution deployed`,
          `Developer activity increases significantly`
        ],
        adoption: [
          `Major company accepts ${symbol.split('-')[0]} payments`,
          `${symbol.split('-')[0]} added to payment platform`,
          `Enterprise adoption grows for ${symbol.split('-')[0]}`
        ],
        general: [
          `Crypto market shows mixed signals`,
          `Analysts predict volatility ahead`,
          `Market consolidation continues`
        ]
      };
      
      const sentiment = selectedType === 'trump' ? (Math.random() - 0.5) * 2 :
                       selectedType === 'sec' ? (Math.random() - 0.3) * 1.5 :
                       selectedType === 'market' ? Math.random() * 0.8 - 0.2 :
                       (Math.random() - 0.5) * 0.8;
      
      return {
        id: Date.now() + Math.random(),
        timestamp: new Date(),
        headline: headlines[selectedType][Math.floor(Math.random() * headlines[selectedType].length)],
        type: selectedType,
        sentiment: sentiment,
        impact: newsTypes.find(n => n.type === selectedType)?.impact || 'low',
        symbol: symbol
      };
    };
    
    let intervalId;
    
    if (isMonitoring) {
      intervalId = setInterval(() => {
        const newMinuteData = {};
        const newSignals = [];
        const newBullAlerts = [];
        const newSentimentData = {};
        const newNewsItems = [];
        
        symbols.forEach(symbol => {
          const prevData = minuteData[symbol]?.[minuteData[symbol].length - 1];
          const newData = generateMinuteData(symbol, prevData);
          
          // Update minute data
          newMinuteData[symbol] = [
            ...(minuteData[symbol] || []).slice(-199), // Keep last 200 minutes
            newData
          ];
          
          // Update sentiment data
          newSentimentData[symbol] = {
            timestamp: newData.timestamp,
            overallSentiment: newData.overallSentiment,
            sentimentCategory: newData.sentimentCategory,
            newsSentiment: newData.newsSentiment,
            trumpInfluence: newData.trumpInfluence,
            regulatoryInfluence: newData.regulatoryInfluence,
            btcCorrelationInfluence: newData.btcCorrelationInfluence,
            newsVolume: newData.newsVolume,
            sentimentConfidence: newData.sentimentConfidence,
            
            // Sentiment flags
            recentTrumpTweet: newData.recentTrumpTweet,
            regulatoryNews: newData.regulatoryNews,
            positiveNewsMomentum: newData.positiveNewsMomentum,
            negativeNewsMomentum: newData.negativeNewsMomentum
          };
          
          // Generate news items occasionally
          if (Math.random() > 0.85) { // 15% chance per update
            const newsItem = generateNewsItem(symbol);
            newNewsItems.push(newsItem);
          }
          
          // Check for crossover signals
          const crossover = detectCrossover(newData, prevData);
          if (crossover) {
            newSignals.push(crossover);
          }
          
          // Enhanced bull run alerts with sentiment
          if (newData.bullRunProbability > 0.75 && newData.percentGain > 1.5) {
            newBullAlerts.push({
              id: Date.now() + Math.random(),
              timestamp: newData.timestamp,
              symbol,
              bullRunProbability: newData.bullRunProbability,
              percentGain: newData.percentGain,
              percentBB: newData.percentBB,
              price: newData.close,
              
              // Enhanced with sentiment
              sentimentScore: newData.overallSentiment,
              sentimentCategory: newData.sentimentCategory,
              trumpInfluence: newData.trumpInfluence,
              regulatoryInfluence: newData.regulatoryInfluence,
              newsVolume: newData.newsVolume,
              
              // Alert enhancements
              sentimentBoost: newData.overallSentiment > 0.3,
              trumpTweetAlert: newData.recentTrumpTweet,
              regulatoryAlert: newData.regulatoryNews
            });
          }
        });
        
        setMinuteData(prev => ({ ...prev, ...newMinuteData }));
        setSentimentData(prev => ({ ...prev, ...newSentimentData }));
        
        if (newNewsItems.length > 0) {
          setNewsItems(prev => [...newNewsItems, ...prev].slice(0, 50)); // Keep last 50 news items
        }
        
        if (newSignals.length > 0) {
          setCurrentSignals(prev => [...newSignals, ...prev].slice(0, 20));
        }
        
        if (newBullAlerts.length > 0) {
          setBullRunAlerts(prev => [...newBullAlerts, ...prev].slice(0, 10));
        }
      }, 3000); // Update every 3 seconds for demo (would be 60 seconds in production)
    }
    
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isMonitoring, symbols, minuteData]);
  
  const currentData = minuteData[selectedSymbol]?.[minuteData[selectedSymbol].length - 1];
  const previousData = minuteData[selectedSymbol]?.[minuteData[selectedSymbol].length - 2];
  
  const getCSIRSISignal = (csi, rsi) => {
    const diff = csi - rsi;
    if (Math.abs(diff) < 3) return { signal: 'CONVERGENCE', color: 'yellow' };
    if (csi > rsi && csi > 55) return { signal: 'BULLISH', color: 'green' };
    if (csi < rsi && csi < 45) return { signal: 'BEARISH', color: 'red' };
    return { signal: 'NEUTRAL', color: 'gray' };
  };
  
  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };
  
  return (
    <div className="p-6 bg-gray-900 text-white min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold mb-2">🚀 Bull Run Detection Center</h1>
            <p className="text-gray-400">Real-time CSI/RSI crossovers & volatility monitoring</p>
          </div>
          <button
            onClick={() => setIsMonitoring(!isMonitoring)}
            className={`px-6 py-3 rounded-lg font-semibold flex items-center space-x-2 ${
              isMonitoring 
                ? 'bg-red-600 hover:bg-red-700' 
                : 'bg-green-600 hover:bg-green-700'
            }`}
          >
            <Eye className="w-5 h-5" />
            <span>{isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}</span>
          </button>
        </div>
        
        {/* Symbol Selector */}
        <div className="mb-6">
          <div className="flex space-x-4">
            {symbols.map(symbol => (
              <button
                key={symbol}
                onClick={() => setSelectedSymbol(symbol)}
                className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                  selectedSymbol === symbol
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {symbol}
              </button>
            ))}
          </div>
        </div>
        
        {/* Real-time Status */}
        {currentData && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            {/* CSI/RSI Crossover Monitor */}
            <div className="lg:col-span-2 bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold">CSI/RSI Crossover Monitor</h3>
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${isMonitoring ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
                  <span className="text-sm text-gray-400">
                    {isMonitoring ? 'LIVE' : 'STOPPED'}
                  </span>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-6">
                {/* CSI */}
                <div className="bg-gray-700 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">CSI (Cumulative Strength)</span>
                    <Zap className="w-4 h-4 text-blue-400" />
                  </div>
                  <div className="text-2xl font-bold text-blue-400">
                    {currentData.csi.toFixed(1)}
                  </div>
                  <div className="flex items-center space-x-2 mt-2">
                    {previousData && (
                      <>
                        {currentData.csi > previousData.csi ? (
                          <TrendingUp className="w-4 h-4 text-green-400" />
                        ) : (
                          <TrendingDown className="w-4 h-4 text-red-400" />
                        )}
                        <span className={`text-sm ${
                          currentData.csi > previousData.csi ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {((currentData.csi - previousData.csi)).toFixed(1)}
                        </span>
                      </>
                    )}
                  </div>
                </div>
                
                {/* RSI */}
                <div className="bg-gray-700 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">RSI (Relative Strength)</span>
                    <Activity className="w-4 h-4 text-purple-400" />
                  </div>
                  <div className={`text-2xl font-bold ${
                    currentData.rsi > 70 ? 'text-red-400' : 
                    currentData.rsi < 30 ? 'text-green-400' : 'text-purple-400'
                  }`}>
                    {currentData.rsi.toFixed(1)}
                  </div>
                  <div className="flex items-center space-x-2 mt-2">
                    {previousData && (
                      <>
                        {currentData.rsi > previousData.rsi ? (
                          <TrendingUp className="w-4 h-4 text-green-400" />
                        ) : (
                          <TrendingDown className="w-4 h-4 text-red-400" />
                        )}
                        <span className={`text-sm ${
                          currentData.rsi > previousData.rsi ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {((currentData.rsi - previousData.rsi)).toFixed(1)}
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>
              
              {/* CSI/RSI Relationship */}
              <div className="mt-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">CSI vs RSI Status</span>
                  {(() => {
                    const { signal, color } = getCSIRSISignal(currentData.csi, currentData.rsi);
                    return (
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold bg-${color}-900 text-${color}-400`}>
                        {signal}
                      </span>
                    );
                  })()}
                </div>
                
                <div className="relative bg-gray-700 rounded-lg h-20 overflow-hidden">
                  {/* CSI Bar */}
                  <div 
                    className="absolute top-2 bg-blue-500 h-6 rounded transition-all duration-300"
                    style={{ width: `${currentData.csi}%` }}
                  >
                    <span className="absolute right-2 top-0.5 text-xs font-bold">CSI</span>
                  </div>
                  
                  {/* RSI Bar */}
                  <div 
                    className="absolute bottom-2 bg-purple-500 h-6 rounded transition-all duration-300"
                    style={{ width: `${currentData.rsi}%` }}
                  >
                    <span className="absolute right-2 top-0.5 text-xs font-bold">RSI</span>
                  </div>
                  
                  {/* Crossover indicator */}
                  {Math.abs(currentData.csi - currentData.rsi) < 5 && (
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                      <div className="w-3 h-3 bg-yellow-400 rounded-full animate-pulse"></div>
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            {/* Bull Run Probability */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Bull Run Probability</h3>
                <Target className="w-5 h-5 text-yellow-400" />
              </div>
              
              <div className="text-center">
                <div className={`text-4xl font-bold mb-2 ${
                  currentData.bullRunProbability > 0.75 ? 'text-green-400' :
                  currentData.bullRunProbability > 0.5 ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {(currentData.bullRunProbability * 100).toFixed(0)}%
                </div>
                
                <div className="w-full bg-gray-700 rounded-full h-4 mb-4">
                  <div 
                    className={`h-4 rounded-full transition-all duration-500 ${
                      currentData.bullRunProbability > 0.75 ? 'bg-gradient-to-r from-green-500 to-green-400' :
                      currentData.bullRunProbability > 0.5 ? 'bg-gradient-to-r from-yellow-500 to-yellow-400' :
                      'bg-gradient-to-r from-red-500 to-red-400'
                    }`}
                    style={{ width: `${currentData.bullRunProbability * 100}%` }}
                  ></div>
                </div>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">%Gain:</span>
                    <span className={`font-bold ${currentData.percentGain > 2 ? 'text-green-400' : 'text-white'}`}>
                      {currentData.percentGain.toFixed(2)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">%BB:</span>
                    <span className={`font-bold ${currentData.percentBB > 8 ? 'text-purple-400' : 'text-white'}`}>
                      {currentData.percentBB.toFixed(2)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Buy/Sell:</span>
                    <span className={`font-bold ${currentData.buySellRatio > 1.1 ? 'text-green-400' : 'text-red-400'}`}>
                      {currentData.buySellRatio.toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Recent Signals */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Trading Signals */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Recent Trading Signals</h3>
              <Bell className="w-5 h-5 text-blue-400" />
            </div>
            
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {currentSignals.length === 0 ? (
                <div className="text-center text-gray-400 py-8">
                  {isMonitoring ? 'Waiting for crossover signals...' : 'Start monitoring to see signals'}
                </div>
              ) : (
                currentSignals.map(signal => (
                  <div key={signal.id} className="bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold">{signal.symbol}</span>
                        <span className={`px-2 py-1 rounded text-xs font-bold bg-${signal.signalColor}-900 text-${signal.signalColor}-300`}>
                          {signal.signalType}
                        </span>
                      </div>
                      <span className="text-xs text-gray-400">{formatTime(signal.timestamp)}</span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-400">CSI/RSI:</span>
                        <span className="ml-2 font-bold">
                          {signal.csi.toFixed(1)}/{signal.rsi.toFixed(1)}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-400">Confidence:</span>
                        <span className="ml-2 font-bold text-green-400">
                          {(signal.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-400">%Gain:</span>
                        <span className="ml-2 font-bold">
                          {signal.percentGain.toFixed(2)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-400">Entry:</span>
                        <span className="ml-2 font-bold">
                          ${signal.entryPrice.toFixed(2)}
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
          
          {/* Bull Run Alerts */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Bull Run Alerts</h3>
              <AlertTriangle className="w-5 h-5 text-yellow-400" />
            </div>
            
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {bullRunAlerts.length === 0 ? (
                <div className="text-center text-gray-400 py-8">
                  {isMonitoring ? 'Monitoring for bull run signals...' : 'Start monitoring to detect bull runs'}
                </div>
              ) : (
                bullRunAlerts.map(alert => (
                  <div key={alert.id} className="bg-gradient-to-r from-yellow-900 to-orange-900 rounded-lg p-4 border border-yellow-600">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <Zap className="w-4 h-4 text-yellow-400" />
                        <span className="font-semibold">{alert.symbol}</span>
                        <span className="px-2 py-1 rounded text-xs font-bold bg-yellow-600 text-yellow-100">
                          BULL RUN
                        </span>
                      </div>
                      <span className="text-xs text-gray-300">{formatTime(alert.timestamp)}</span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-300">Probability:</span>
                        <span className="ml-2 font-bold text-yellow-400">
                          {(alert.bullRunProbability * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-300">Price:</span>
                        <span className="ml-2 font-bold text-white">
                          ${alert.price.toFixed(2)}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-300">%Gain:</span>
                        <span className="ml-2 font-bold text-green-400">
                          {alert.percentGain.toFixed(2)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-300">%BB:</span>
                        <span className="ml-2 font-bold text-purple-400">
                          {alert.percentBB.toFixed(2)}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
        
        {/* Current Market Data */}
        {currentData && (
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold mb-4">Current Market Data - {selectedSymbol}</h3>
            
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              <div className="bg-gray-700 rounded-lg p-3">
                <div className="text-xs text-gray-400 mb-1">Price</div>
                <div className="text-lg font-bold">${currentData.close.toFixed(2)}</div>
              </div>
              
              <div className="bg-gray-700 rounded-lg p-3">
                <div className="text-xs text-gray-400 mb-1">%Gain</div>
                <div className={`text-lg font-bold ${
                  currentData.percentGain > 2 ? 'text-red-400' : 
                  currentData.percentGain > 1 ? 'text-orange-400' : 'text-green-400'
                }`}>
                  {currentData.percentGain.toFixed(2)}%
                </div>
              </div>
              
              <div className="bg-gray-700 rounded-lg p-3">
                <div className="text-xs text-gray-400 mb-1">%BB</div>
                <div className={`text-lg font-bold ${
                  currentData.percentBB > 10 ? 'text-purple-400' : 
                  currentData.percentBB < 4 ? 'text-gray-400' : 'text-blue-400'
                }`}>
                  {currentData.percentBB.toFixed(2)}%
                </div>
              </div>
              
              <div className="bg-gray-700 rounded-lg p-3">
                <div className="text-xs text-gray-400 mb-1">CSI</div>
                <div className="text-lg font-bold text-blue-400">
                  {currentData.csi.toFixed(1)}
                </div>
              </div>
              
              <div className="bg-gray-700 rounded-lg p-3">
                <div className="text-xs text-gray-400 mb-1">RSI</div>
                <div className={`text-lg font-bold ${
                  currentData.rsi > 70 ? 'text-red-400' : 
                  currentData.rsi < 30 ? 'text-green-400' : 'text-purple-400'
                }`}>
                  {currentData.rsi.toFixed(1)}
                </div>
              </div>
              
              <div className="bg-gray-700 rounded-lg p-3">
                <div className="text-xs text-gray-400 mb-1">Volume</div>
                <div className="text-lg font-bold">{currentData.volume.toFixed(0)}</div>
              </div>
            </div>
          </div>
        )}
        
        {/* Enhanced Legend */}
        <div className="mt-6 bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="font-semibold mb-3">Enhanced Signal Guide</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
            <div>
              <div className="font-semibold mb-2 text-green-400">Buy Signals:</div>
              <div className="space-y-1 text-gray-300">
                <div>• CSI crosses above RSI in positive territory</div>
                <div>• High %Gain + %BB expansion</div>
                <div>• Volume surge + strong buy pressure</div>
                <div>• Bull run probability >75%</div>
                <div>• Buy/Sell ratio >1.2 with trader growth</div>
              </div>
            </div>
            <div>
              <div className="font-semibold mb-2 text-red-400">Sell Signals:</div>
              <div className="space-y-1 text-gray-300">
                <div>• CSI crosses below RSI in negative territory</div>
                <div>• RSI >70 with declining volume</div>
                <div>• Volatility contraction after spike</div>
                <div>• Volume divergence (price up, volume down)</div>
                <div>• Sell pressure dominance</div>
              </div>
            </div>
            <div>
              <div className="font-semibold mb-2 text-purple-400">Volume & Flow Indicators:</div>
              <div className="space-y-1 text-gray-300">
                <div>• <span className="text-orange-400">Orange dot:</span> Volume surge detected</div>
                <div>• <span className="text-purple-400">Purple dot:</span> Institutional activity</div>
                <div>• <span className="text-green-400">Green dot:</span> Strong buy pressure</div>
                <div>• <span className="text-blue-400">Blue dot:</span> High trader participation</div>
                <div>• Large avg trade size = institutional presence</div>
              </div>
            </div>
          </div>
          
          <div className="mt-4 pt-4 border-t border-gray-700">
            <div className="font-semibold mb-2 text-yellow-400">Enhanced Bull Run Detection Factors:</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-300">
              <div>
                <div className="font-medium mb-1">Volume Analysis (25% weight):</div>
                <div>• Volume surge vs historical baseline</div>
                <div>• Buy vs sell volume distribution</div>
                <div>• Volume trend acceleration</div>
              </div>
              <div>
                <div className="font-medium mb-1">Trade Flow Analysis (20% weight):</div>
                <div>• Buy/sell trade count ratio</div>
                <div>• Trade size patterns (retail vs institutional)</div>
                <div>• Trader participation growth</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealTimeTradingDashboard;