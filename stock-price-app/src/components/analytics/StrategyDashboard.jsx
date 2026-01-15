import { useState, useEffect, useCallback } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (
  import.meta.env.DEV
    ? 'http://localhost:8080'
    : 'https://trading-api-1075463475276.us-central1.run.app'
);

export default function StrategyDashboard() {
  const [strategies, setStrategies] = useState([]);
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [sectorMomentum, setSectorMomentum] = useState([]);
  const [sectorStocks, setSectorStocks] = useState([]);
  const [selectedSector, setSelectedSector] = useState(null);
  const [riseCycles, setRiseCycles] = useState(null);
  const [paperTrades, setPaperTrades] = useState({ trades: [], summary: [] });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('strategies');
  const [cycleSymbol, setCycleSymbol] = useState('NVDA');
  const [cycleDate, setCycleDate] = useState(new Date().toISOString().split('T')[0]);

  // Fetch strategies
  const fetchStrategies = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/strategies`);
      const data = await response.json();
      if (data.success) {
        setStrategies(data.strategies);
      }
    } catch (error) {
      console.error('Error fetching strategies:', error);
    }
  }, []);

  // Fetch sector momentum
  const fetchSectorMomentum = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/sector-momentum`);
      const data = await response.json();
      if (data.success) {
        setSectorMomentum(data.sectors);
      }
    } catch (error) {
      console.error('Error fetching sector momentum:', error);
    }
  }, []);

  // Fetch stocks for a sector
  const fetchSectorStocks = useCallback(async (sector) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/sector-momentum/${encodeURIComponent(sector)}/stocks?limit=20`);
      const data = await response.json();
      if (data.success) {
        setSectorStocks(data.stocks);
        setSelectedSector(sector);
      }
    } catch (error) {
      console.error('Error fetching sector stocks:', error);
    }
  }, []);

  // Fetch rise cycles
  const fetchRiseCycles = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/rise-cycles/${cycleSymbol}/${cycleDate}`);
      const data = await response.json();
      if (data.success) {
        setRiseCycles(data);
      }
    } catch (error) {
      console.error('Error fetching rise cycles:', error);
    }
  }, [cycleSymbol, cycleDate]);

  // Fetch paper trades
  const fetchPaperTrades = useCallback(async () => {
    try {
      const [tradesRes, summaryRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/paper-trades?limit=50`),
        fetch(`${API_BASE_URL}/api/paper-trades/summary`)
      ]);
      const tradesData = await tradesRes.json();
      const summaryData = await summaryRes.json();

      setPaperTrades({
        trades: tradesData.success ? tradesData.trades : [],
        summary: summaryData.success ? summaryData.summaries : []
      });
    } catch (error) {
      console.error('Error fetching paper trades:', error);
    }
  }, []);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([
        fetchStrategies(),
        fetchSectorMomentum(),
        fetchPaperTrades()
      ]);
      setLoading(false);
    };
    loadData();
  }, [fetchStrategies, fetchSectorMomentum, fetchPaperTrades]);

  // Strategy Card Component
  const StrategyCard = ({ strategy }) => (
    <div
      onClick={() => setSelectedStrategy(strategy)}
      style={{
        background: selectedStrategy?.strategy_id === strategy.strategy_id
          ? 'linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%)'
          : '#1e293b',
        borderRadius: '12px',
        padding: '20px',
        cursor: 'pointer',
        border: selectedStrategy?.strategy_id === strategy.strategy_id
          ? '2px solid #3b82f6'
          : '1px solid #334155',
        transition: 'all 0.2s ease'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
        <div>
          <h3 style={{ color: '#f1f5f9', margin: 0, fontSize: '18px' }}>{strategy.strategy_name}</h3>
          <span style={{
            background: strategy.strategy_type === 'intraday' ? '#22c55e' : '#3b82f6',
            color: 'white',
            padding: '2px 8px',
            borderRadius: '4px',
            fontSize: '11px',
            marginTop: '4px',
            display: 'inline-block'
          }}>
            {strategy.strategy_type?.toUpperCase()}
          </span>
        </div>
        <span style={{
          color: strategy.is_active ? '#22c55e' : '#64748b',
          fontSize: '12px'
        }}>
          {strategy.is_active ? 'Active' : 'Inactive'}
        </span>
      </div>
      <p style={{ color: '#94a3b8', fontSize: '13px', margin: '0 0 12px 0' }}>
        {strategy.description}
      </p>
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        {strategy.asset_types?.map((type, i) => (
          <span key={i} style={{
            background: '#334155',
            color: '#94a3b8',
            padding: '2px 8px',
            borderRadius: '4px',
            fontSize: '11px'
          }}>
            {type}
          </span>
        ))}
      </div>
    </div>
  );

  // Sector Momentum Card
  const SectorCard = ({ sector, rank }) => (
    <div
      onClick={() => fetchSectorStocks(sector.sector)}
      style={{
        background: selectedSector === sector.sector ? '#1e3a5f' : '#1e293b',
        borderRadius: '8px',
        padding: '12px 16px',
        cursor: 'pointer',
        border: selectedSector === sector.sector ? '1px solid #3b82f6' : '1px solid #334155',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}
    >
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{
            background: rank <= 3 ? '#22c55e' : rank <= 6 ? '#f59e0b' : '#64748b',
            color: 'white',
            width: '24px',
            height: '24px',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '12px',
            fontWeight: 'bold'
          }}>
            {rank}
          </span>
          <span style={{ color: '#f1f5f9', fontWeight: '500' }}>{sector.sector}</span>
        </div>
      </div>
      <div style={{
        color: sector.avg_change_pct >= 0 ? '#22c55e' : '#ef4444',
        fontWeight: '600'
      }}>
        {sector.avg_change_pct >= 0 ? '+' : ''}{sector.avg_change_pct?.toFixed(2)}%
      </div>
    </div>
  );

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px', color: '#64748b' }}>
        Loading strategies...
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1400px', margin: '0 auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ color: '#f1f5f9', margin: 0, fontSize: '28px' }}>Trading Strategies</h1>
        <p style={{ color: '#64748b', margin: '8px 0 0 0' }}>
          Manage strategies, analyze rise cycles, and track paper trades
        </p>
      </div>

      {/* Tab Navigation */}
      <div style={{
        display: 'flex',
        gap: '4px',
        marginBottom: '24px',
        background: '#0f172a',
        padding: '4px',
        borderRadius: '8px',
        width: 'fit-content'
      }}>
        {['strategies', 'sectors', 'rise-cycles', 'paper-trades'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              background: activeTab === tab ? '#3b82f6' : 'transparent',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '6px',
              color: activeTab === tab ? 'white' : '#64748b',
              cursor: 'pointer',
              fontWeight: '500'
            }}
          >
            {tab.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
          </button>
        ))}
      </div>

      {/* Strategies Tab */}
      {activeTab === 'strategies' && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '16px' }}>
            {strategies.map(strategy => (
              <StrategyCard key={strategy.strategy_id + strategy.created_at} strategy={strategy} />
            ))}
          </div>

          {/* Strategy Help Panel */}
          {selectedStrategy && (
            <div style={{
              marginTop: '24px',
              background: 'linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%)',
              borderRadius: '16px',
              padding: '24px',
              border: '2px solid #3b82f6'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
                <div>
                  <h2 style={{ color: '#f1f5f9', margin: 0, fontSize: '24px' }}>{selectedStrategy.strategy_name}</h2>
                  <span style={{
                    background: selectedStrategy.strategy_type === 'intraday' ? '#22c55e' : '#3b82f6',
                    color: 'white',
                    padding: '4px 12px',
                    borderRadius: '6px',
                    fontSize: '12px',
                    marginTop: '8px',
                    display: 'inline-block'
                  }}>
                    {selectedStrategy.strategy_type?.toUpperCase()}
                  </span>
                </div>
                <button
                  onClick={() => setSelectedStrategy(null)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#64748b',
                    fontSize: '24px',
                    cursor: 'pointer'
                  }}
                >
                  ×
                </button>
              </div>

              {/* Strategy Description */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{ color: '#3b82f6', margin: '0 0 12px 0', fontSize: '16px' }}>How This Strategy Works</h3>
                <p style={{ color: '#94a3b8', fontSize: '15px', lineHeight: '1.6', margin: 0 }}>
                  {selectedStrategy.description}
                </p>
              </div>

              {/* Detailed Help based on strategy type */}
              {selectedStrategy.strategy_code === 'MTC' && (
                <div style={{ background: '#0f172a', borderRadius: '12px', padding: '20px', marginBottom: '20px' }}>
                  <h4 style={{ color: '#22c55e', margin: '0 0 16px 0' }}>📊 Multi-Timeframe Confirmation Strategy</h4>
                  <div style={{ color: '#d1d5db', fontSize: '14px', lineHeight: '1.8' }}>
                    <p><strong>Goal:</strong> Only enter trades when weekly, daily, and hourly trends all align in the same direction.</p>
                    <p><strong>Entry Rules:</strong></p>
                    <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                      <li>Weekly trend must be UP (price above 20-week SMA)</li>
                      <li>Daily trend must be UP (price above 20-day SMA)</li>
                      <li>Hourly gives entry signal (RSI oversold bounce or MACD crossover)</li>
                    </ul>
                    <p><strong>Exit Rules:</strong></p>
                    <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                      <li>Daily trend turns DOWN or hits target</li>
                      <li>Stop loss: Below recent swing low</li>
                    </ul>
                    <p><strong>Best For:</strong> Swing traders looking for high-probability entries with reduced risk.</p>
                  </div>
                </div>
              )}

              {selectedStrategy.strategy_code === 'SMR' && (
                <div style={{ background: '#0f172a', borderRadius: '12px', padding: '20px', marginBottom: '20px' }}>
                  <h4 style={{ color: '#f59e0b', margin: '0 0 16px 0' }}>🔄 Sector Momentum Rotation Strategy</h4>
                  <div style={{ color: '#d1d5db', fontSize: '14px', lineHeight: '1.8' }}>
                    <p><strong>Goal:</strong> Ride the strongest sectors by rotating into top-performing industries weekly.</p>
                    <p><strong>How It Works:</strong></p>
                    <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                      <li>Every week, rank all 11 sectors by average stock performance</li>
                      <li>Focus on TOP 3 sectors showing positive momentum</li>
                      <li>Within those sectors, find the top 10-20 stocks by weekly % gain</li>
                      <li>Enter positions in leaders, exit when sector loses momentum</li>
                    </ul>
                    <p><strong>Key Metrics:</strong></p>
                    <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                      <li>Avg Change %: Average price change of stocks in sector</li>
                      <li>Momentum Rank: 1-11 ranking (1 = strongest)</li>
                      <li>Volatility: Higher = more opportunity but more risk</li>
                    </ul>
                    <p><strong>Best For:</strong> Position traders who want to be in the hottest sectors each week.</p>
                  </div>
                </div>
              )}

              {selectedStrategy.strategy_code === 'RCD' && (
                <div style={{ background: '#0f172a', borderRadius: '12px', padding: '20px', marginBottom: '20px' }}>
                  <h4 style={{ color: '#ef4444', margin: '0 0 16px 0' }}>🚀 Rise Cycle Detection Strategy</h4>
                  <div style={{ color: '#d1d5db', fontSize: '14px', lineHeight: '1.8' }}>
                    <p><strong>Goal:</strong> Catch intraday momentum surges and exit before they reverse.</p>
                    <p><strong>How It Works:</strong></p>
                    <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                      <li>Monitor 5-minute candles for "rise cycle" start signals</li>
                      <li>Rise cycle starts when: 3+ consecutive green candles OR volume spike + price break</li>
                      <li>Enter at cycle confirmation, ride the momentum</li>
                      <li>Exit when: First red candle, or RSI divergence, or target hit</li>
                    </ul>
                    <p><strong>Risk Management:</strong></p>
                    <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                      <li>Position size: 1-2% of account per trade</li>
                      <li>Stop loss: Below the cycle start low</li>
                      <li>Typical trade duration: 15-90 minutes</li>
                    </ul>
                    <p><strong>Best For:</strong> Day traders who want quick, momentum-based entries and exits.</p>
                  </div>
                </div>
              )}

              {/* Timeframes and Asset Types */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div style={{ background: '#0f172a', borderRadius: '8px', padding: '16px' }}>
                  <div style={{ color: '#64748b', fontSize: '12px', marginBottom: '8px' }}>Timeframes</div>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    {selectedStrategy.timeframes?.map((tf, i) => (
                      <span key={i} style={{
                        background: '#334155',
                        color: '#f1f5f9',
                        padding: '4px 12px',
                        borderRadius: '6px',
                        fontSize: '13px'
                      }}>
                        {tf}
                      </span>
                    ))}
                  </div>
                </div>
                <div style={{ background: '#0f172a', borderRadius: '8px', padding: '16px' }}>
                  <div style={{ color: '#64748b', fontSize: '12px', marginBottom: '8px' }}>Asset Types</div>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    {selectedStrategy.asset_types?.map((type, i) => (
                      <span key={i} style={{
                        background: '#334155',
                        color: '#f1f5f9',
                        padding: '4px 12px',
                        borderRadius: '6px',
                        fontSize: '13px'
                      }}>
                        {type}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Sectors Tab */}
      {activeTab === 'sectors' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
          <div>
            <h3 style={{ color: '#f1f5f9', marginTop: 0 }}>Sector Momentum Rankings</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {sectorMomentum.map((sector, idx) => (
                <SectorCard key={sector.sector} sector={sector} rank={idx + 1} />
              ))}
            </div>
          </div>
          <div>
            <h3 style={{ color: '#f1f5f9', marginTop: 0 }}>
              {selectedSector ? `Top Stocks in ${selectedSector}` : 'Select a Sector'}
            </h3>
            {sectorStocks.length > 0 && (
              <div style={{ background: '#1e293b', borderRadius: '12px', overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ background: '#0f172a' }}>
                      <th style={{ color: '#64748b', padding: '12px', textAlign: 'left' }}>Symbol</th>
                      <th style={{ color: '#64748b', padding: '12px', textAlign: 'right' }}>Price</th>
                      <th style={{ color: '#64748b', padding: '12px', textAlign: 'right' }}>Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sectorStocks.map(stock => (
                      <tr key={stock.symbol} style={{ borderBottom: '1px solid #334155' }}>
                        <td style={{ color: '#f1f5f9', padding: '12px' }}>{stock.symbol}</td>
                        <td style={{ color: '#94a3b8', padding: '12px', textAlign: 'right' }}>${stock.price?.toFixed(2)}</td>
                        <td style={{ color: stock.week_change_pct >= 0 ? '#22c55e' : '#ef4444', padding: '12px', textAlign: 'right', fontWeight: '600' }}>
                          {stock.week_change_pct >= 0 ? '+' : ''}{stock.week_change_pct}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Rise Cycles Tab */}
      {activeTab === 'rise-cycles' && (
        <div style={{ background: '#1e293b', borderRadius: '12px', padding: '20px' }}>
          <h3 style={{ color: '#f1f5f9', marginTop: 0 }}>Rise Cycle Analyzer</h3>
          <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
            <input
              type="text"
              value={cycleSymbol}
              onChange={(e) => setCycleSymbol(e.target.value.toUpperCase())}
              placeholder="Symbol"
              style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '6px', padding: '8px 12px', color: '#f1f5f9', width: '100px' }}
            />
            <input
              type="date"
              value={cycleDate}
              onChange={(e) => setCycleDate(e.target.value)}
              style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '6px', padding: '8px 12px', color: '#f1f5f9' }}
            />
            <button
              onClick={fetchRiseCycles}
              style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)', border: 'none', borderRadius: '6px', padding: '8px 20px', color: 'white', cursor: 'pointer' }}
            >
              Analyze
            </button>
          </div>
          {riseCycles?.summary && (
            <div style={{ background: '#0f172a', borderRadius: '8px', padding: '16px', display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px' }}>
              <div>
                <div style={{ color: '#64748b', fontSize: '12px' }}>Cycles</div>
                <div style={{ color: '#f1f5f9', fontSize: '24px', fontWeight: 'bold' }}>{riseCycles.summary.total_cycles}</div>
              </div>
              <div>
                <div style={{ color: '#64748b', fontSize: '12px' }}>Winning</div>
                <div style={{ color: '#22c55e', fontSize: '24px', fontWeight: 'bold' }}>{riseCycles.summary.winning_cycles}</div>
              </div>
              <div>
                <div style={{ color: '#64748b', fontSize: '12px' }}>Losing</div>
                <div style={{ color: '#ef4444', fontSize: '24px', fontWeight: 'bold' }}>{riseCycles.summary.losing_cycles}</div>
              </div>
              <div>
                <div style={{ color: '#64748b', fontSize: '12px' }}>End Capital</div>
                <div style={{ color: '#f1f5f9', fontSize: '24px', fontWeight: 'bold' }}>${riseCycles.summary.ending_capital?.toLocaleString()}</div>
              </div>
              <div>
                <div style={{ color: '#64748b', fontSize: '12px' }}>Return</div>
                <div style={{ color: riseCycles.summary.total_return_pct >= 0 ? '#22c55e' : '#ef4444', fontSize: '24px', fontWeight: 'bold' }}>
                  {riseCycles.summary.total_return_pct >= 0 ? '+' : ''}{riseCycles.summary.total_return_pct?.toFixed(2)}%
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Paper Trades Tab */}
      {activeTab === 'paper-trades' && (
        <div style={{ background: '#1e293b', borderRadius: '12px', padding: '20px' }}>
          <h3 style={{ color: '#f1f5f9', marginTop: 0 }}>Paper Trading Portfolio</h3>
          {paperTrades.trades.length > 0 ? (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#0f172a' }}>
                  <th style={{ color: '#64748b', padding: '12px', textAlign: 'left' }}>Symbol</th>
                  <th style={{ color: '#64748b', padding: '12px', textAlign: 'left' }}>Type</th>
                  <th style={{ color: '#64748b', padding: '12px', textAlign: 'right' }}>Entry</th>
                  <th style={{ color: '#64748b', padding: '12px', textAlign: 'right' }}>P&L</th>
                  <th style={{ color: '#64748b', padding: '12px', textAlign: 'left' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {paperTrades.trades.map(trade => (
                  <tr key={trade.trade_id} style={{ borderBottom: '1px solid #334155' }}>
                    <td style={{ color: '#f1f5f9', padding: '12px' }}>{trade.symbol}</td>
                    <td style={{ color: trade.trade_type === 'BUY' ? '#22c55e' : '#ef4444', padding: '12px' }}>{trade.trade_type}</td>
                    <td style={{ color: '#94a3b8', padding: '12px', textAlign: 'right' }}>${trade.entry_price?.toFixed(2)}</td>
                    <td style={{ color: (trade.net_pnl || 0) >= 0 ? '#22c55e' : '#ef4444', padding: '12px', textAlign: 'right' }}>
                      {trade.net_pnl ? `$${trade.net_pnl?.toFixed(2)}` : '-'}
                    </td>
                    <td style={{ padding: '12px' }}>
                      <span style={{ background: trade.status === 'open' ? '#f59e0b' : '#22c55e', color: 'white', padding: '2px 8px', borderRadius: '4px', fontSize: '11px' }}>
                        {trade.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div style={{ color: '#64748b', textAlign: 'center', padding: '40px' }}>No paper trades yet</div>
          )}
        </div>
      )}
    </div>
  );
}

