import React, { useState, useEffect, useRef } from 'react';
import {
  Box, Card, CardContent, Typography, Grid, CircularProgress,
  Alert, ToggleButton, ToggleButtonGroup, Paper
} from '@mui/material';
import {
  ShowChart, TrendingUp, Assessment, Timeline
} from '@mui/icons-material';

const API_BASE = 'https://trading-api-1075463475276.us-central1.run.app';

const WalkForwardCharts = ({ runId }) => {
  const [equityCurve, setEquityCurve] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [chartType, setChartType] = useState('equity');

  const canvasRef = useRef(null);
  const accuracyCanvasRef = useRef(null);
  const drawdownCanvasRef = useRef(null);

  useEffect(() => {
    if (runId) {
      fetchEquityCurve();
    }
  }, [runId]);

  useEffect(() => {
    if (equityCurve.length > 0) {
      drawCharts();
    }
  }, [equityCurve, chartType]);

  const fetchEquityCurve = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/ml/walk-forward/runs/${runId}/equity-curve`);
      const data = await response.json();
      setEquityCurve(data.equity_curve || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const drawCharts = () => {
    // Draw equity curve
    drawEquityCurve();
    // Draw rolling accuracy
    drawRollingAccuracy();
    // Draw drawdown
    drawDrawdown();
  };

  const drawEquityCurve = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const padding = 50;

    // Clear
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, width, height);

    if (equityCurve.length === 0) return;

    // Get data
    const values = equityCurve.map(d => d.equity_value);
    const minVal = Math.min(...values) * 0.98;
    const maxVal = Math.max(...values) * 1.02;
    const range = maxVal - minVal;

    // Scale functions
    const scaleX = (i) => padding + (i / (equityCurve.length - 1)) * (width - 2 * padding);
    const scaleY = (v) => height - padding - ((v - minVal) / range) * (height - 2 * padding);

    // Draw grid
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= 5; i++) {
      const y = padding + (i / 5) * (height - 2 * padding);
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.stroke();

      // Y axis labels
      const val = maxVal - (i / 5) * range;
      ctx.fillStyle = '#888';
      ctx.font = '11px Arial';
      ctx.textAlign = 'right';
      ctx.fillText(`$${val.toFixed(0)}`, padding - 5, y + 4);
    }

    // Draw equity line
    ctx.beginPath();
    ctx.strokeStyle = '#4ade80';
    ctx.lineWidth = 2;

    equityCurve.forEach((point, i) => {
      const x = scaleX(i);
      const y = scaleY(point.equity_value);
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();

    // Fill area under curve
    ctx.lineTo(scaleX(equityCurve.length - 1), height - padding);
    ctx.lineTo(scaleX(0), height - padding);
    ctx.closePath();
    ctx.fillStyle = 'rgba(74, 222, 128, 0.1)';
    ctx.fill();

    // Draw starting line
    ctx.beginPath();
    ctx.strokeStyle = '#666';
    ctx.setLineDash([5, 5]);
    ctx.moveTo(padding, scaleY(10000));
    ctx.lineTo(width - padding, scaleY(10000));
    ctx.stroke();
    ctx.setLineDash([]);

    // Title
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Equity Curve', width / 2, 25);

    // Final value label
    const lastVal = values[values.length - 1];
    ctx.fillStyle = lastVal > 10000 ? '#4ade80' : '#f87171';
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'right';
    ctx.fillText(`$${lastVal.toFixed(2)}`, width - padding, 25);
  };

  const drawRollingAccuracy = () => {
    const canvas = accuracyCanvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const padding = 50;

    // Clear
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, width, height);

    if (equityCurve.length === 0) return;

    const values = equityCurve.map(d => d.rolling_accuracy_30d || d.win_rate_to_date);
    const minVal = 0;
    const maxVal = 1;

    // Scale functions
    const scaleX = (i) => padding + (i / (equityCurve.length - 1)) * (width - 2 * padding);
    const scaleY = (v) => height - padding - ((v - minVal) / (maxVal - minVal)) * (height - 2 * padding);

    // Draw grid
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 0.5;
    const gridLines = [0, 0.25, 0.5, 0.75, 1.0];
    gridLines.forEach(val => {
      const y = scaleY(val);
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.stroke();

      ctx.fillStyle = '#888';
      ctx.font = '11px Arial';
      ctx.textAlign = 'right';
      ctx.fillText(`${(val * 100).toFixed(0)}%`, padding - 5, y + 4);
    });

    // Draw 50% reference line
    ctx.beginPath();
    ctx.strokeStyle = '#f87171';
    ctx.setLineDash([5, 5]);
    ctx.moveTo(padding, scaleY(0.5));
    ctx.lineTo(width - padding, scaleY(0.5));
    ctx.stroke();
    ctx.setLineDash([]);

    // Draw accuracy line
    ctx.beginPath();
    ctx.strokeStyle = '#60a5fa';
    ctx.lineWidth = 2;

    equityCurve.forEach((point, i) => {
      const val = point.rolling_accuracy_30d || point.win_rate_to_date;
      if (val === null || val === undefined) return;

      const x = scaleX(i);
      const y = scaleY(val);
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();

    // Title
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Rolling Accuracy (30-day)', width / 2, 25);

    // Current accuracy
    const lastAcc = values[values.length - 1];
    if (lastAcc !== null && lastAcc !== undefined) {
      ctx.fillStyle = lastAcc > 0.5 ? '#4ade80' : '#f87171';
      ctx.font = 'bold 16px Arial';
      ctx.textAlign = 'right';
      ctx.fillText(`${(lastAcc * 100).toFixed(1)}%`, width - padding, 25);
    }
  };

  const drawDrawdown = () => {
    const canvas = drawdownCanvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const padding = 50;

    // Clear
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, width, height);

    if (equityCurve.length === 0) return;

    // Calculate drawdown from equity values
    const equityValues = equityCurve.map(d => d.equity_value);
    let peak = equityValues[0];
    const drawdowns = equityValues.map((val, i) => {
      peak = Math.max(peak, val);
      return (val - peak) / peak;
    });

    const minDrawdown = Math.min(...drawdowns, -0.01);
    const maxDrawdown = 0;

    // Scale functions
    const scaleX = (i) => padding + (i / (equityCurve.length - 1)) * (width - 2 * padding);
    const scaleY = (v) => padding + ((maxDrawdown - v) / (maxDrawdown - minDrawdown)) * (height - 2 * padding);

    // Draw grid
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 0.5;
    const steps = 5;
    for (let i = 0; i <= steps; i++) {
      const val = minDrawdown + (i / steps) * (maxDrawdown - minDrawdown);
      const y = scaleY(val);
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.stroke();

      ctx.fillStyle = '#888';
      ctx.font = '11px Arial';
      ctx.textAlign = 'right';
      ctx.fillText(`${(val * 100).toFixed(0)}%`, padding - 5, y + 4);
    }

    // Draw drawdown area
    ctx.beginPath();
    ctx.moveTo(scaleX(0), scaleY(0));

    drawdowns.forEach((dd, i) => {
      ctx.lineTo(scaleX(i), scaleY(dd));
    });

    ctx.lineTo(scaleX(drawdowns.length - 1), scaleY(0));
    ctx.closePath();
    ctx.fillStyle = 'rgba(248, 113, 113, 0.3)';
    ctx.fill();

    // Draw drawdown line
    ctx.beginPath();
    ctx.strokeStyle = '#f87171';
    ctx.lineWidth = 2;

    drawdowns.forEach((dd, i) => {
      const x = scaleX(i);
      const y = scaleY(dd);
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();

    // Title
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Drawdown', width / 2, 25);

    // Max drawdown
    const maxDD = Math.min(...drawdowns);
    ctx.fillStyle = '#f87171';
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'right';
    ctx.fillText(`Max: ${(maxDD * 100).toFixed(1)}%`, width - padding, 25);
  };

  // Calculate summary stats
  const stats = equityCurve.length > 0 ? {
    startValue: 10000,
    endValue: equityCurve[equityCurve.length - 1]?.equity_value || 10000,
    totalReturn: equityCurve[equityCurve.length - 1]?.cumulative_return || 0,
    finalAccuracy: equityCurve[equityCurve.length - 1]?.win_rate_to_date || 0,
    totalTrades: equityCurve[equityCurve.length - 1]?.trades_to_date || 0,
    maxDrawdown: (() => {
      let peak = 10000;
      let maxDD = 0;
      equityCurve.forEach(p => {
        peak = Math.max(peak, p.equity_value);
        const dd = (p.equity_value - peak) / peak;
        maxDD = Math.min(maxDD, dd);
      });
      return maxDD;
    })()
  } : null;

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Box>
      {/* Summary Stats */}
      {stats && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={6} sm={4} md={2}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'grey.800' }}>
              <Typography variant="overline" color="text.secondary">Start Value</Typography>
              <Typography variant="h6" color="white">${stats.startValue.toLocaleString()}</Typography>
            </Paper>
          </Grid>
          <Grid item xs={6} sm={4} md={2}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: stats.endValue > stats.startValue ? 'success.dark' : 'error.dark' }}>
              <Typography variant="overline" color="white">End Value</Typography>
              <Typography variant="h6" color="white">${stats.endValue.toLocaleString()}</Typography>
            </Paper>
          </Grid>
          <Grid item xs={6} sm={4} md={2}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: stats.totalReturn > 0 ? 'success.dark' : 'error.dark' }}>
              <Typography variant="overline" color="white">Total Return</Typography>
              <Typography variant="h6" color="white">{(stats.totalReturn * 100).toFixed(2)}%</Typography>
            </Paper>
          </Grid>
          <Grid item xs={6} sm={4} md={2}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: stats.finalAccuracy > 0.5 ? 'info.dark' : 'warning.dark' }}>
              <Typography variant="overline" color="white">Win Rate</Typography>
              <Typography variant="h6" color="white">{(stats.finalAccuracy * 100).toFixed(1)}%</Typography>
            </Paper>
          </Grid>
          <Grid item xs={6} sm={4} md={2}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'error.dark' }}>
              <Typography variant="overline" color="white">Max Drawdown</Typography>
              <Typography variant="h6" color="white">{(stats.maxDrawdown * 100).toFixed(1)}%</Typography>
            </Paper>
          </Grid>
          <Grid item xs={6} sm={4} md={2}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'grey.800' }}>
              <Typography variant="overline" color="text.secondary">Total Trades</Typography>
              <Typography variant="h6" color="white">{stats.totalTrades}</Typography>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <ShowChart /> Equity Curve
              </Typography>
              <Box sx={{ bgcolor: '#1a1a2e', borderRadius: 1, p: 1 }}>
                <canvas
                  ref={canvasRef}
                  width={800}
                  height={300}
                  style={{ width: '100%', height: 'auto' }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Assessment /> Rolling Accuracy
              </Typography>
              <Box sx={{ bgcolor: '#1a1a2e', borderRadius: 1, p: 1 }}>
                <canvas
                  ref={accuracyCanvasRef}
                  width={400}
                  height={250}
                  style={{ width: '100%', height: 'auto' }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingUp /> Drawdown
              </Typography>
              <Box sx={{ bgcolor: '#1a1a2e', borderRadius: 1, p: 1 }}>
                <canvas
                  ref={drawdownCanvasRef}
                  width={400}
                  height={250}
                  style={{ width: '100%', height: 'auto' }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {equityCurve.length === 0 && !loading && (
        <Alert severity="info" sx={{ mt: 2 }}>
          No equity curve data available for this run. Run a validation first to see charts.
        </Alert>
      )}
    </Box>
  );
};

export default WalkForwardCharts;
