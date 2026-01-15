import { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Chip,
  Stack,
  TextField,
  Grid,
  Tabs,
  Tab,
  Card,
  CardContent
} from '@mui/material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart
} from 'recharts';
import DownloadIcon from '@mui/icons-material/Download';
import RefreshIcon from '@mui/icons-material/Refresh';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import TableChartIcon from '@mui/icons-material/TableChart';
import { API_BASE_URL } from '../services/api';

const WeeklyReconciliation = () => {
  const [loading, setLoading] = useState(false);
  const [assetType, setAssetType] = useState('stocks');
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [weeklyData, setWeeklyData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [error, setError] = useState('');
  const [stats, setStats] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [recordLimit, setRecordLimit] = useState(52); // Default to 1 year of weekly data

  // Fetch symbols on asset type change
  useEffect(() => {
    fetchSymbols();
  }, [assetType]);

  const fetchSymbols = async () => {
    try {
      const endpoint = assetType === 'stocks'
        ? '/api/stocks/symbols'
        : '/api/cryptos/symbols';

      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      if (!response.ok) throw new Error('Failed to fetch symbols');

      const data = await response.json();
      setSymbols(data.symbols || []);
      setSelectedSymbol('');
    } catch (err) {
      setError('Failed to load symbols: ' + err.message);
    }
  };

  const fetchWeeklyData = async () => {
    if (!selectedSymbol) return;

    setLoading(true);
    setError('');

    try {
      const endpoint = assetType === 'stocks'
        ? `/api/stocks/weekly/${selectedSymbol}`
        : `/api/cryptos/weekly/${selectedSymbol}`;

      const response = await fetch(
        `${API_BASE_URL}${endpoint}?limit=${recordLimit}`
      );

      if (!response.ok) throw new Error('Failed to fetch weekly data');

      const data = await response.json();

      setWeeklyData(data.records || []);
      setColumns(data.columns || []);
      setStats(data.stats || null);

    } catch (err) {
      setError('Failed to load weekly data: ' + err.message);
      setWeeklyData([]);
      setColumns([]);
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = () => {
    if (!weeklyData.length || !columns.length) return;

    const headers = columns.join(',');
    const rows = weeklyData.map(row =>
      columns.map(col => {
        const value = row[col];
        if (typeof value === 'string' && value.includes(',')) {
          return `"${value}"`;
        }
        return value ?? '';
      }).join(',')
    );

    const csvContent = [headers, ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `${selectedSymbol}_weekly_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Prepare chart data
  const chartData = weeklyData.map(row => ({
    date: row.datetime ? new Date(row.datetime).toLocaleDateString() : '',
    close: row.close || 0,
    volume: row.volume || 0,
    rsi: row.rsi_14 || row.rsi || 0,
    macd: row.macd || 0,
    macd_signal: row.macd_signal || 0,
    sma_20: row.sma_20 || 0,
    sma_50: row.sma_50 || 0,
    bb_upper: row.bb_upper || 0,
    bb_lower: row.bb_lower || 0,
    volatility: row.volatility_20 || row.atr_pct || 0,
    return_1w: row.daily_return_pct || 0
  })).reverse(); // Reverse to show oldest to newest

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        <ShowChartIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Weekly Analysis & Data Reconciliation
      </Typography>

      <Typography variant="body2" color="text.secondary" paragraph>
        Analyze weekly trends with charts and verify all downloaded fields.
        Browse complete dataset with horizontal scrolling and download CSV.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Controls */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Asset Type</InputLabel>
              <Select
                value={assetType}
                onChange={(e) => setAssetType(e.target.value)}
                label="Asset Type"
              >
                <MenuItem value="stocks">Stocks</MenuItem>
                <MenuItem value="cryptos">Cryptos</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Select Symbol</InputLabel>
              <Select
                value={selectedSymbol}
                onChange={(e) => setSelectedSymbol(e.target.value)}
                label="Select Symbol"
              >
                <MenuItem value="">
                  <em>Choose a symbol</em>
                </MenuItem>
                {symbols.map((symbol) => (
                  <MenuItem key={symbol} value={symbol}>
                    {symbol}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={2}>
            <TextField
              fullWidth
              type="number"
              label="Weeks to Display"
              value={recordLimit}
              onChange={(e) => setRecordLimit(Math.max(1, parseInt(e.target.value) || 52))}
              inputProps={{ min: 1, max: 260 }}
            />
          </Grid>

          <Grid item xs={12} md={5}>
            <Stack direction="row" spacing={2}>
              <Button
                variant="contained"
                onClick={fetchWeeklyData}
                disabled={!selectedSymbol || loading}
                startIcon={loading ? <CircularProgress size={20} /> : <RefreshIcon />}
                fullWidth
              >
                {loading ? 'Loading...' : 'Load Data'}
              </Button>

              <Button
                variant="outlined"
                onClick={downloadCSV}
                disabled={!weeklyData.length}
                startIcon={<DownloadIcon />}
                fullWidth
              >
                Download CSV
              </Button>
            </Stack>
          </Grid>
        </Grid>
      </Paper>

      {/* Statistics */}
      {stats && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Stack direction="row" spacing={2} flexWrap="wrap">
            <Chip label={`Symbol: ${stats.symbol}`} color="primary" />
            <Chip label={`Weeks: ${stats.total_records?.toLocaleString() || 0}`} />
            <Chip label={`Fields: ${stats.total_fields || 0}`} />
            <Chip label={`Latest Price: $${stats.latest_price?.toFixed(2) || 'N/A'}`} color="success" />
            <Chip label={`52W High: $${stats.high_52w?.toFixed(2) || 'N/A'}`} color="error" />
            <Chip label={`52W Low: $${stats.low_52w?.toFixed(2) || 'N/A'}`} color="warning" />
          </Stack>
        </Paper>
      )}

      {/* Tabs for Charts and Data */}
      {weeklyData.length > 0 && (
        <Paper sx={{ mb: 3 }}>
          <Tabs
            value={tabValue}
            onChange={(e, newValue) => setTabValue(newValue)}
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab icon={<ShowChartIcon />} label="Charts" />
            <Tab icon={<TableChartIcon />} label="Data Table" />
          </Tabs>

          {/* Charts Tab */}
          {tabValue === 0 && (
            <Box sx={{ p: 3 }}>
              <Grid container spacing={3}>
                {/* Price Chart with Moving Averages */}
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Price & Moving Averages
                      </Typography>
                      <ResponsiveContainer width="100%" height={400}>
                        <ComposedChart data={chartData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis yAxisId="left" />
                          <Tooltip />
                          <Legend />
                          <Area
                            yAxisId="left"
                            type="monotone"
                            dataKey="bb_upper"
                            fill="#e3f2fd"
                            stroke="#2196f3"
                            fillOpacity={0.3}
                            name="BB Upper"
                          />
                          <Area
                            yAxisId="left"
                            type="monotone"
                            dataKey="bb_lower"
                            fill="#e3f2fd"
                            stroke="#2196f3"
                            fillOpacity={0.3}
                            name="BB Lower"
                          />
                          <Line
                            yAxisId="left"
                            type="monotone"
                            dataKey="close"
                            stroke="#4caf50"
                            strokeWidth={2}
                            dot={false}
                            name="Close Price"
                          />
                          <Line
                            yAxisId="left"
                            type="monotone"
                            dataKey="sma_20"
                            stroke="#ff9800"
                            strokeWidth={1.5}
                            dot={false}
                            name="SMA 20"
                          />
                          <Line
                            yAxisId="left"
                            type="monotone"
                            dataKey="sma_50"
                            stroke="#f44336"
                            strokeWidth={1.5}
                            dot={false}
                            name="SMA 50"
                          />
                        </ComposedChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Volume Chart */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Volume
                      </Typography>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={chartData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Bar dataKey="volume" fill="#9c27b0" name="Volume" />
                        </BarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </Grid>

                {/* RSI Chart */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        RSI (Relative Strength Index)
                      </Typography>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={chartData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis domain={[0, 100]} />
                          <Tooltip />
                          <Legend />
                          <Line
                            type="monotone"
                            dataKey="rsi"
                            stroke="#00bcd4"
                            strokeWidth={2}
                            dot={false}
                            name="RSI"
                          />
                          <Line
                            type="monotone"
                            dataKey={() => 70}
                            stroke="#f44336"
                            strokeDasharray="5 5"
                            dot={false}
                            name="Overbought (70)"
                          />
                          <Line
                            type="monotone"
                            dataKey={() => 30}
                            stroke="#4caf50"
                            strokeDasharray="5 5"
                            dot={false}
                            name="Oversold (30)"
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </Grid>

                {/* MACD Chart */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        MACD
                      </Typography>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={chartData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Line
                            type="monotone"
                            dataKey="macd"
                            stroke="#3f51b5"
                            strokeWidth={2}
                            dot={false}
                            name="MACD"
                          />
                          <Line
                            type="monotone"
                            dataKey="macd_signal"
                            stroke="#ff5722"
                            strokeWidth={2}
                            dot={false}
                            name="Signal"
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Volatility Chart */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Volatility
                      </Typography>
                      <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={chartData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Area
                            type="monotone"
                            dataKey="volatility"
                            fill="#ff9800"
                            stroke="#ff9800"
                            fillOpacity={0.6}
                            name="Volatility"
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}

          {/* Data Table Tab */}
          {tabValue === 1 && (
            <Box sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                {selectedSymbol} - Complete Weekly Data
              </Typography>
              <Typography variant="caption" color="text.secondary" paragraph>
                Showing {weeklyData.length} records × {columns.length} fields
                (scroll horizontally to view all columns)
              </Typography>

              <TableContainer sx={{ maxHeight: 600 }}>
                <Table stickyHeader size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell
                        sx={{
                          bgcolor: 'primary.main',
                          color: 'primary.contrastText',
                          fontWeight: 'bold',
                          position: 'sticky',
                          left: 0,
                          zIndex: 3
                        }}
                      >
                        #
                      </TableCell>
                      {columns.map((col, idx) => (
                        <TableCell
                          key={col}
                          sx={{
                            bgcolor: 'primary.main',
                            color: 'primary.contrastText',
                            fontWeight: 'bold',
                            minWidth: col === 'datetime' ? 200 : 120,
                            whiteSpace: 'nowrap'
                          }}
                        >
                          {col}
                          <Typography variant="caption" display="block" sx={{ opacity: 0.8 }}>
                            ({idx + 1}/{columns.length})
                          </Typography>
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {weeklyData.map((row, rowIdx) => (
                      <TableRow
                        key={rowIdx}
                        hover
                        sx={{ '&:nth-of-type(odd)': { bgcolor: 'action.hover' } }}
                      >
                        <TableCell
                          sx={{
                            fontWeight: 'bold',
                            position: 'sticky',
                            left: 0,
                            bgcolor: 'background.paper',
                            zIndex: 1
                          }}
                        >
                          {rowIdx + 1}
                        </TableCell>
                        {columns.map((col) => {
                          const value = row[col];
                          const isNumeric = typeof value === 'number';

                          return (
                            <TableCell
                              key={col}
                              align={isNumeric ? 'right' : 'left'}
                              sx={{
                                fontFamily: isNumeric ? 'monospace' : 'inherit',
                                fontSize: '0.875rem',
                                whiteSpace: 'nowrap'
                              }}
                            >
                              {isNumeric ?
                                (Number.isInteger(value) ? value : value.toFixed(4))
                                : (value ?? 'null')
                              }
                            </TableCell>
                          );
                        })}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </Paper>
      )}

      {/* Empty State */}
      {!loading && !weeklyData.length && selectedSymbol && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            No weekly data available for {selectedSymbol}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Click "Load Data" to fetch weekly records
          </Typography>
        </Paper>
      )}

      {/* Initial State */}
      {!selectedSymbol && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            Select an asset type and symbol to begin
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {symbols.length} {assetType} available
          </Typography>
        </Paper>
      )}

      {/* Field Legend */}
      {columns.length > 0 && (
        <Paper sx={{ p: 2, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Available Fields ({columns.length})
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {columns.map((col, idx) => (
              <Chip
                key={col}
                label={`${idx + 1}. ${col}`}
                size="small"
                variant="outlined"
              />
            ))}
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default WeeklyReconciliation;
