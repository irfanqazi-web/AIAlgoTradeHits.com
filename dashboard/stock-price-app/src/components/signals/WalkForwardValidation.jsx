import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Grid, Button, TextField,
  Select, MenuItem, FormControl, InputLabel, Slider, Chip,
  CircularProgress, Alert, Paper, Divider, LinearProgress,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Tabs, Tab, IconButton, Tooltip
} from '@mui/material';
import {
  PlayArrow, Stop, Refresh, Download, TrendingUp, TrendingDown,
  CheckCircle, Error, Schedule, Assessment
} from '@mui/icons-material';
import WalkForwardResults from './WalkForwardResults';
import WalkForwardCharts from '../charts/WalkForwardCharts';

const API_BASE = 'https://trading-api-1075463475276.us-central1.run.app';

const WalkForwardValidation = () => {
  // Configuration state
  const [config, setConfig] = useState({
    symbols: 'AAPL',
    assetClass: 'Equity',
    testStart: '2024-01-01',
    walkForwardDays: 252,
    retrainFrequency: 'weekly',
    featuresMode: 'default_16',
    confidenceThreshold: 0.5
  });

  // Data state
  const [runs, setRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [tickers, setTickers] = useState([]);
  const [sectorPerformance, setSectorPerformance] = useState([]);
  const [summary, setSummary] = useState(null);

  // UI state
  const [loading, setLoading] = useState(false);
  const [runningValidation, setRunningValidation] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [progress, setProgress] = useState(0);

  // Load initial data
  useEffect(() => {
    fetchRuns();
    fetchSummary();
    fetchSectorPerformance();
  }, []);

  // Load tickers when asset class changes
  useEffect(() => {
    fetchTickers(config.assetClass);
  }, [config.assetClass]);

  // Fetch functions
  const fetchRuns = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/ml/walk-forward/runs`);
      const data = await response.json();
      setRuns(data.runs || []);
    } catch (err) {
      console.error('Failed to fetch runs:', err);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/ml/walk-forward/summary`);
      const data = await response.json();
      setSummary(data);
    } catch (err) {
      console.error('Failed to fetch summary:', err);
    }
  };

  const fetchTickers = async (assetClass) => {
    try {
      const response = await fetch(`${API_BASE}/api/ml/tickers/${assetClass}`);
      const data = await response.json();
      setTickers(data.tickers || []);
    } catch (err) {
      console.error('Failed to fetch tickers:', err);
    }
  };

  const fetchSectorPerformance = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/ml/sector-performance`);
      const data = await response.json();
      setSectorPerformance(data.sectors || []);
    } catch (err) {
      console.error('Failed to fetch sector performance:', err);
    }
  };

  // Start validation
  const startValidation = async () => {
    setRunningValidation(true);
    setError(null);
    setProgress(0);

    try {
      const response = await fetch(`${API_BASE}/api/ml/walk-forward/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbols: config.symbols,
          asset_class: config.assetClass,
          test_start: config.testStart,
          walk_forward_days: config.walkForwardDays,
          retrain_frequency: config.retrainFrequency,
          features_mode: config.featuresMode,
          confidence_threshold: config.confidenceThreshold
        })
      });

      const data = await response.json();

      if (data.error) {
        setError(data.error);
      } else {
        setSelectedRun(data);
        fetchRuns();
        fetchSummary();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setRunningValidation(false);
    }
  };

  // Cancel validation
  const cancelValidation = async (runId) => {
    try {
      await fetch(`${API_BASE}/api/ml/walk-forward/runs/${runId}`, {
        method: 'DELETE'
      });
      fetchRuns();
    } catch (err) {
      console.error('Failed to cancel:', err);
    }
  };

  // View run details
  const viewRunDetails = async (runId) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/ml/walk-forward/runs/${runId}`);
      const data = await response.json();
      setSelectedRun(data);
      setActiveTab(1);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Format percentage
  const formatPercent = (val) => {
    if (val === null || val === undefined) return '-';
    return `${(val * 100).toFixed(1)}%`;
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'info';
      case 'failed': return 'error';
      case 'cancelled': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Assessment /> Walk-Forward Validation System
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Institutional-grade ML model validation with configurable parameters
      </Typography>

      <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ mb: 3 }}>
        <Tab label="Configuration" />
        <Tab label="Results" />
        <Tab label="Charts" />
        <Tab label="History" />
      </Tabs>

      {/* Summary Cards */}
      {summary && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'primary.dark' }}>
              <CardContent>
                <Typography color="white" variant="overline">Total Runs</Typography>
                <Typography color="white" variant="h4">{summary.statistics?.total_runs || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'success.dark' }}>
              <CardContent>
                <Typography color="white" variant="overline">Avg Accuracy</Typography>
                <Typography color="white" variant="h4">
                  {formatPercent(summary.statistics?.avg_accuracy)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'info.dark' }}>
              <CardContent>
                <Typography color="white" variant="overline">Best Accuracy</Typography>
                <Typography color="white" variant="h4">
                  {formatPercent(summary.statistics?.best_accuracy)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'warning.dark' }}>
              <CardContent>
                <Typography color="white" variant="overline">Best Return</Typography>
                <Typography color="white" variant="h4">
                  {formatPercent(summary.statistics?.best_return)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Tab Content */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {/* Configuration Panel */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Validation Configuration</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Asset Class</InputLabel>
                      <Select
                        value={config.assetClass}
                        label="Asset Class"
                        onChange={(e) => setConfig({...config, assetClass: e.target.value})}
                      >
                        <MenuItem value="Equity">Equity</MenuItem>
                        <MenuItem value="Crypto">Crypto</MenuItem>
                        <MenuItem value="ETF">ETF</MenuItem>
                        <MenuItem value="FX">FX</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      size="small"
                      label="Symbols (comma-separated)"
                      value={config.symbols}
                      onChange={(e) => setConfig({...config, symbols: e.target.value})}
                      placeholder="AAPL,MSFT,GOOGL"
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      size="small"
                      type="date"
                      label="Test Start Date"
                      value={config.testStart}
                      onChange={(e) => setConfig({...config, testStart: e.target.value})}
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Features Mode</InputLabel>
                      <Select
                        value={config.featuresMode}
                        label="Features Mode"
                        onChange={(e) => setConfig({...config, featuresMode: e.target.value})}
                      >
                        <MenuItem value="default_16">16 Validated Features</MenuItem>
                        <MenuItem value="advanced_97">97 Advanced Features</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Retrain Frequency</InputLabel>
                      <Select
                        value={config.retrainFrequency}
                        label="Retrain Frequency"
                        onChange={(e) => setConfig({...config, retrainFrequency: e.target.value})}
                      >
                        <MenuItem value="daily">Daily</MenuItem>
                        <MenuItem value="weekly">Weekly</MenuItem>
                        <MenuItem value="monthly">Monthly</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography gutterBottom>Walk-Forward Days: {config.walkForwardDays}</Typography>
                    <Slider
                      value={config.walkForwardDays}
                      onChange={(e, v) => setConfig({...config, walkForwardDays: v})}
                      min={10}
                      max={500}
                      step={10}
                      marks={[
                        { value: 63, label: '3M' },
                        { value: 126, label: '6M' },
                        { value: 252, label: '1Y' },
                        { value: 500, label: '2Y' }
                      ]}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      Confidence Threshold: {(config.confidenceThreshold * 100).toFixed(0)}%
                    </Typography>
                    <Slider
                      value={config.confidenceThreshold}
                      onChange={(e, v) => setConfig({...config, confidenceThreshold: v})}
                      min={0.5}
                      max={0.9}
                      step={0.05}
                      marks={[
                        { value: 0.5, label: '50%' },
                        { value: 0.6, label: '60%' },
                        { value: 0.7, label: '70%' },
                        { value: 0.8, label: '80%' }
                      ]}
                    />
                  </Grid>
                </Grid>

                <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    size="large"
                    startIcon={runningValidation ? <CircularProgress size={20} /> : <PlayArrow />}
                    onClick={startValidation}
                    disabled={runningValidation}
                  >
                    {runningValidation ? 'Running Validation...' : 'Run Validation'}
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Refresh />}
                    onClick={fetchRuns}
                  >
                    Refresh
                  </Button>
                </Box>

                {runningValidation && (
                  <Box sx={{ mt: 2 }}>
                    <LinearProgress variant="indeterminate" />
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Validation in progress... This may take several minutes for long date ranges.
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Sector Performance Panel */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Sector Model Performance</Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Sector</TableCell>
                        <TableCell align="right">Accuracy</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {sectorPerformance.slice(0, 8).map((sector) => (
                        <TableRow key={sector.sector}>
                          <TableCell>{sector.sector}</TableCell>
                          <TableCell align="right">
                            <Chip
                              size="small"
                              label={formatPercent(sector.accuracy)}
                              color={sector.accuracy > 0.8 ? 'success' : sector.accuracy > 0.6 ? 'warning' : 'error'}
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>

            {/* Available Tickers */}
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Available Tickers ({tickers.length})
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, maxHeight: 200, overflow: 'auto' }}>
                  {tickers.slice(0, 50).map((ticker) => (
                    <Chip
                      key={ticker.symbol}
                      label={ticker.symbol}
                      size="small"
                      onClick={() => setConfig({...config, symbols: ticker.symbol})}
                      sx={{ cursor: 'pointer' }}
                    />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 1 && selectedRun && (
        <WalkForwardResults runId={selectedRun.run_id} runData={selectedRun} />
      )}

      {activeTab === 2 && selectedRun && (
        <WalkForwardCharts runId={selectedRun.run_id} />
      )}

      {activeTab === 3 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Validation History</Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Run ID</TableCell>
                    <TableCell>Symbols</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell align="center">Status</TableCell>
                    <TableCell align="right">Accuracy</TableCell>
                    <TableCell align="right">Return</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {runs.map((run) => (
                    <TableRow key={run.run_id} hover>
                      <TableCell>{run.run_id}</TableCell>
                      <TableCell>{run.symbols}</TableCell>
                      <TableCell>
                        {run.run_timestamp ? new Date(run.run_timestamp).toLocaleDateString() : '-'}
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          size="small"
                          label={run.status}
                          color={getStatusColor(run.status)}
                          icon={
                            run.status === 'completed' ? <CheckCircle /> :
                            run.status === 'running' ? <Schedule /> :
                            run.status === 'failed' ? <Error /> : null
                          }
                        />
                      </TableCell>
                      <TableCell align="right">{formatPercent(run.overall_accuracy)}</TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                          {run.total_return > 0 ? <TrendingUp color="success" /> : <TrendingDown color="error" />}
                          {formatPercent(run.total_return)}
                        </Box>
                      </TableCell>
                      <TableCell align="center">
                        <Tooltip title="View Details">
                          <IconButton size="small" onClick={() => viewRunDetails(run.run_id)}>
                            <Assessment />
                          </IconButton>
                        </Tooltip>
                        {run.status === 'running' && (
                          <Tooltip title="Cancel">
                            <IconButton size="small" color="error" onClick={() => cancelValidation(run.run_id)}>
                              <Stop />
                            </IconButton>
                          </Tooltip>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default WalkForwardValidation;
