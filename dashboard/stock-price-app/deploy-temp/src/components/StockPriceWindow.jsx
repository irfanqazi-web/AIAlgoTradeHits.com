import { useState, useEffect } from 'react';
import { ComposedChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const StockPriceWindow = ({ title, interval, refreshRate }) => {
  const [stockData, setStockData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [symbol, setSymbol] = useState('AAPL');

  // Generate OHLC candlestick data
  const generateCandlestickData = () => {
    const dataPoints = 30;
    const basePrice = 150 + Math.random() * 50;
    const data = [];

    for (let i = 0; i < dataPoints; i++) {
      const timeMs = Date.now() - (dataPoints - i - 1) * (
        interval === 'daily' ? 86400000 :
        interval === 'hourly' ? 3600000 :
        60000
      );

      const open = basePrice + (Math.random() - 0.5) * 10;
      const close = open + (Math.random() - 0.5) * 5;
      const high = Math.max(open, close) + Math.random() * 3;
      const low = Math.min(open, close) - Math.random() * 3;

      data.push({
        time: interval === 'daily'
          ? new Date(timeMs).toLocaleDateString([], { month: 'short', day: 'numeric' })
          : interval === 'hourly'
          ? new Date(timeMs).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          : new Date(timeMs).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        open: Number(open.toFixed(2)),
        high: Number(high.toFixed(2)),
        low: Number(low.toFixed(2)),
        close: Number(close.toFixed(2)),
        // For bar chart representation of candlestick
        candleRange: [Math.min(open, close), Math.max(open, close)],
        wickRange: [low, high],
        isUp: close >= open,
      });
    }

    return data;
  };

  // Fetch and update data
  const fetchStockData = async () => {
    setLoading(true);
    setError(null);

    try {
      await new Promise(resolve => setTimeout(resolve, 500));

      const data = generateCandlestickData();
      setStockData(data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch stock data');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStockData();
    const intervalId = setInterval(fetchStockData, refreshRate);

    return () => clearInterval(intervalId);
  }, [symbol, refreshRate]);

  const currentPrice = stockData.length > 0 ? stockData[stockData.length - 1]?.close : 0;

  return (
    <div className="stock-window">
      <div className="window-header">
        <h3>{title}</h3>
        <div className="controls">
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            placeholder="Symbol"
            className="symbol-input"
          />
          <button onClick={fetchStockData} className="refresh-btn">
            ↻
          </button>
        </div>
      </div>

      <div className="window-content">
        {loading && <div className="loading">Loading...</div>}
        {error && <div className="error">{error}</div>}

        {!loading && !error && (
          <>
            <ResponsiveContainer width="100%" height={250}>
              <ComposedChart data={stockData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                <XAxis
                  dataKey="time"
                  tick={{ fontSize: 10 }}
                  angle={-45}
                  textAnchor="end"
                  height={60}
                />
                <YAxis
                  tick={{ fontSize: 10 }}
                  domain={['dataMin - 2', 'dataMax + 2']}
                />
                <Tooltip
                  contentStyle={{ background: '#fff', border: '1px solid #ccc' }}
                  labelStyle={{ color: '#213547' }}
                  formatter={(value, name) => {
                    if (name === 'candleRange') return null;
                    if (name === 'wickRange') return null;
                    return [`$${value}`, name];
                  }}
                />
                {/* Wicks */}
                <Bar dataKey="wickRange" fill="transparent" stroke="#666" strokeWidth={1} />
                {/* Candle bodies */}
                <Bar dataKey="candleRange" barSize={8}>
                  {stockData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.isUp ? '#26a69a' : '#ef5350'} />
                  ))}
                </Bar>
              </ComposedChart>
            </ResponsiveContainer>

            <div className="current-price">
              <span className="price-label">Current Price:</span>
              <span className="price-value">${currentPrice.toFixed(2)}</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default StockPriceWindow;
