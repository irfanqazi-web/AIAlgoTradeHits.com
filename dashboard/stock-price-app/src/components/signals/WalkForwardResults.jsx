import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Grid, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Chip, Paper,
  FormControl, InputLabel, Select, MenuItem, Slider, Button,
  CircularProgress, Alert, Divider, Tooltip
} from '@mui/material';
import {
  TrendingUp, TrendingDown, CheckCircle, Cancel, Download,
  FilterList, Info
} from '@mui/icons-material';

const API_BASE = 'https://trading-api-1075463475276.us-central1.run.app';

const WalkForwardResults = ({ runId, runData }) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [confidenceFilter, setConfidenceFilter] = useState(0);
  const [directionFilter, setDirectionFilter] = useState('all');

  useEffect(() => {
    if (runId) {
      fetchResults();
    }
  }, [runId, confidenceFilter]);

  const fetchResults = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_BASE}/api/ml/walk-forward/runs/${runId}/results?confidence_min=${confidenceFilter}`
      );
      const data = await response.json();
      setResults(data.results || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatPercent = (val) => {
    if (val === null || val === undefined) return '-';
    return `${(val * 100).toFixed(2)}%`;
  };

  const formatPrice = (val) => {
    if (val === null || val === undefined) return '-';
    return `$${val.toFixed(2)}`;
  };

  const exportCSV = () => {
    const headers = [
      'Date', 'Symbol', 'Predicted', 'Actual', 'Confidence',
      'Correct', 'Return', 'Cumulative Return'
    ];
    const rows = results.map(r => [
      r.prediction_date,
      r.symbol,
      r.predicted_direction,
      r.actual_direction,
      (r.confidence * 100).toFixed(1) + '%',
      r.is_correct ? 'Yes' : 'No',
      (r.actual_return * 100).toFixed(2) + '%',
      (r.cumulative_return * 100).toFixed(2) + '%'
    ]);

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `walk_forward_${runId}_results.csv`;
    a.click();
  };

  const filteredResults = results.filter(r => {
    if (directionFilter !== 'all' && r.predicted_direction !== directionFilter) {
      return false;
    }
    return true;
  });

  // Calculate stats from filtered results
  const stats = {
    total: filteredResults.length,
    correct: filteredResults.filter(r => r.is_correct).length,
    upPredictions: filteredResults.filter(r => r.predicted_direction === 'UP').length,
    upCorrect: filteredResults.filter(r => r.predicted_direction === 'UP' && r.is_correct).length,
    downPredictions: filteredResults.filter(r => r.predicted_direction === 'DOWN').length,
    downCorrect: filteredResults.filter(r => r.predicted_direction === 'DOWN' && r.is_correct).length,
  };

  stats.accuracy = stats.total > 0 ? stats.correct / stats.total : 0;
  stats.upAccuracy = stats.upPredictions > 0 ? stats.upCorrect / stats.upPredictions : 0;
  stats.downAccuracy = stats.downPredictions > 0 ? stats.downCorrect / stats.downPredictions : 0;

  return (
    <Box>
      {/* Run Summary */}
      {runData && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Run Summary: {runId}</Typography>
            <Grid container spacing={3}>
              <Grid item xs={6} sm={3}>
                <Typography variant="overline" color="text.secondary">Overall Accuracy</Typography>
                <Typography variant="h4" color="primary">
                  {formatPercent(runData.overall_accuracy)}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="overline" color="text.secondary">UP Accuracy</Typography>
                <Typography variant="h4" color="success.main">
                  {formatPercent(runData.up_accuracy)}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="overline" color="text.secondary">DOWN Accuracy</Typography>
                <Typography variant="h4" color="error.main">
                  {formatPercent(runData.down_accuracy)}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="overline" color="text.secondary">Total Return</Typography>
                <Typography variant="h4" color={runData.total_return > 0 ? 'success.main' : 'error.main'}>
                  {formatPercent(runData.total_return)}
                </Typography>
              </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />

            <Grid container spacing={2}>
              <Grid item xs={6} sm={2}>
                <Typography variant="body2" color="text.secondary">Symbols</Typography>
                <Typography variant="body1">{runData.symbols}</Typography>
              </Grid>
              <Grid item xs={6} sm={2}>
                <Typography variant="body2" color="text.secondary">Test Period</Typography>
                <Typography variant="body1">{runData.test_start} - {runData.test_end || 'Present'}</Typography>
              </Grid>
              <Grid item xs={6} sm={2}>
                <Typography variant="body2" color="text.secondary">Walk-Forward Days</Typography>
                <Typography variant="body1">{runData.walk_forward_days}</Typography>
              </Grid>
              <Grid item xs={6} sm={2}>
                <Typography variant="body2" color="text.secondary">Retrain Frequency</Typography>
                <Typography variant="body1">{runData.retrain_frequency}</Typography>
              </Grid>
              <Grid item xs={6} sm={2}>
                <Typography variant="body2" color="text.secondary">Features Mode</Typography>
                <Typography variant="body1">{runData.features_mode}</Typography>
              </Grid>
              <Grid item xs={6} sm={2}>
                <Typography variant="body2" color="text.secondary">Total Predictions</Typography>
                <Typography variant="body1">{runData.total_predictions}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, flexWrap: 'wrap' }}>
            <FilterList color="action" />
            <Typography variant="subtitle1">Filters</Typography>

            <Box sx={{ minWidth: 200 }}>
              <Typography variant="body2" gutterBottom>
                Min Confidence: {(confidenceFilter * 100).toFixed(0)}%
              </Typography>
              <Slider
                value={confidenceFilter}
                onChange={(e, v) => setConfidenceFilter(v)}
                min={0}
                max={0.9}
                step={0.1}
                marks
                valueLabelDisplay="auto"
                valueLabelFormat={v => `${(v * 100).toFixed(0)}%`}
              />
            </Box>

            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Direction</InputLabel>
              <Select
                value={directionFilter}
                label="Direction"
                onChange={(e) => setDirectionFilter(e.target.value)}
              >
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="UP">UP Only</MenuItem>
                <MenuItem value="DOWN">DOWN Only</MenuItem>
              </Select>
            </FormControl>

            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={exportCSV}
              disabled={results.length === 0}
            >
              Export CSV
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Filtered Stats */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} sm={4} md={2}>
          <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'primary.dark' }}>
            <Typography variant="overline" color="white">Filtered Results</Typography>
            <Typography variant="h5" color="white">{stats.total}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={6} sm={4} md={2}>
          <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'success.dark' }}>
            <Typography variant="overline" color="white">Accuracy</Typography>
            <Typography variant="h5" color="white">{formatPercent(stats.accuracy)}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={6} sm={4} md={2}>
          <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'info.dark' }}>
            <Typography variant="overline" color="white">UP Accuracy</Typography>
            <Typography variant="h5" color="white">{formatPercent(stats.upAccuracy)}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={6} sm={4} md={2}>
          <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'warning.dark' }}>
            <Typography variant="overline" color="white">DOWN Accuracy</Typography>
            <Typography variant="h5" color="white">{formatPercent(stats.downAccuracy)}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={6} sm={4} md={2}>
          <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'grey.700' }}>
            <Typography variant="overline" color="white">UP Predictions</Typography>
            <Typography variant="h5" color="white">{stats.upPredictions}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={6} sm={4} md={2}>
          <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'grey.700' }}>
            <Typography variant="overline" color="white">DOWN Predictions</Typography>
            <Typography variant="h5" color="white">{stats.downPredictions}</Typography>
          </Paper>
        </Grid>
      </Grid>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
      )}

      {/* Results Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Daily Predictions ({filteredResults.length} results)
          </Typography>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer sx={{ maxHeight: 600 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Symbol</TableCell>
                    <TableCell align="center">Predicted</TableCell>
                    <TableCell align="center">Actual</TableCell>
                    <TableCell align="right">Confidence</TableCell>
                    <TableCell align="center">Result</TableCell>
                    <TableCell align="right">Open</TableCell>
                    <TableCell align="right">Close</TableCell>
                    <TableCell align="right">Return</TableCell>
                    <TableCell align="right">Cumulative</TableCell>
                    <TableCell align="center">Retrained</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredResults.map((result, idx) => (
                    <TableRow
                      key={idx}
                      sx={{
                        bgcolor: result.is_correct ? 'success.dark' : 'error.dark',
                        '&:hover': { opacity: 0.9 }
                      }}
                    >
                      <TableCell sx={{ color: 'white' }}>{result.prediction_date}</TableCell>
                      <TableCell sx={{ color: 'white' }}>{result.symbol}</TableCell>
                      <TableCell align="center">
                        <Chip
                          size="small"
                          label={result.predicted_direction}
                          icon={result.predicted_direction === 'UP' ? <TrendingUp /> : <TrendingDown />}
                          color={result.predicted_direction === 'UP' ? 'success' : 'error'}
                        />
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          size="small"
                          label={result.actual_direction}
                          variant="outlined"
                          sx={{ color: 'white', borderColor: 'white' }}
                        />
                      </TableCell>
                      <TableCell align="right" sx={{ color: 'white' }}>
                        {(result.confidence * 100).toFixed(1)}%
                      </TableCell>
                      <TableCell align="center">
                        {result.is_correct ? (
                          <CheckCircle sx={{ color: 'lightgreen' }} />
                        ) : (
                          <Cancel sx={{ color: '#ff8a80' }} />
                        )}
                      </TableCell>
                      <TableCell align="right" sx={{ color: 'white' }}>
                        {formatPrice(result.open_price)}
                      </TableCell>
                      <TableCell align="right" sx={{ color: 'white' }}>
                        {formatPrice(result.close_price)}
                      </TableCell>
                      <TableCell
                        align="right"
                        sx={{ color: result.actual_return > 0 ? 'lightgreen' : '#ff8a80' }}
                      >
                        {(result.actual_return * 100).toFixed(2)}%
                      </TableCell>
                      <TableCell
                        align="right"
                        sx={{ color: result.cumulative_return > 0 ? 'lightgreen' : '#ff8a80' }}
                      >
                        {(result.cumulative_return * 100).toFixed(2)}%
                      </TableCell>
                      <TableCell align="center" sx={{ color: 'white' }}>
                        {result.retrained ? 'Yes' : '-'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default WalkForwardResults;
