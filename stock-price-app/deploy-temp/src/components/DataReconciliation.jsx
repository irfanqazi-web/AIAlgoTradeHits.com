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
  Grid
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import RefreshIcon from '@mui/icons-material/Refresh';
import VerifiedIcon from '@mui/icons-material/Verified';
import { API_BASE_URL } from '../services/api';

const DataReconciliation = () => {
  const [loading, setLoading] = useState(false);
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [stockData, setStockData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [error, setError] = useState('');
  const [stats, setStats] = useState(null);
  const [recordLimit, setRecordLimit] = useState(100);

  // Fetch available symbols on component mount
  useEffect(() => {
    fetchSymbols();
  }, []);

  const fetchSymbols = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/stocks/symbols`);
      if (!response.ok) throw new Error('Failed to fetch symbols');
      const data = await response.json();
      setSymbols(data.symbols || []);
    } catch (err) {
      setError('Failed to load stock symbols: ' + err.message);
    }
  };

  const fetchStockData = async () => {
    if (!selectedSymbol) return;

    setLoading(true);
    setError('');

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/stocks/reconciliation/${selectedSymbol}?limit=${recordLimit}`
      );

      if (!response.ok) throw new Error('Failed to fetch stock data');

      const data = await response.json();

      setStockData(data.records || []);
      setColumns(data.columns || []);
      setStats(data.stats || null);

    } catch (err) {
      setError('Failed to load stock data: ' + err.message);
      setStockData([]);
      setColumns([]);
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = () => {
    if (!stockData.length || !columns.length) return;

    // Create CSV content
    const headers = columns.join(',');
    const rows = stockData.map(row =>
      columns.map(col => {
        const value = row[col];
        // Handle values that might contain commas
        if (typeof value === 'string' && value.includes(',')) {
          return `"${value}"`;
        }
        return value ?? '';
      }).join(',')
    );

    const csvContent = [headers, ...rows].join('\n');

    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `${selectedSymbol}_data_reconciliation_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const downloadFullDataset = async () => {
    if (!selectedSymbol) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/stocks/reconciliation/${selectedSymbol}/download`
      );

      if (!response.ok) throw new Error('Failed to download full dataset');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');

      link.href = url;
      link.setAttribute('download', `${selectedSymbol}_complete_dataset_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);

    } catch (err) {
      setError('Failed to download full dataset: ' + err.message);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        <VerifiedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Data Reconciliation Dashboard
      </Typography>

      <Typography variant="body2" color="text.secondary" paragraph>
        Select a stock symbol to view all downloaded fields and verify data authenticity.
        Browse all columns with horizontal scrolling and download CSV for Excel analysis.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Controls */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Select Stock Symbol</InputLabel>
              <Select
                value={selectedSymbol}
                onChange={(e) => setSelectedSymbol(e.target.value)}
                label="Select Stock Symbol"
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

          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              type="number"
              label="Records to Display"
              value={recordLimit}
              onChange={(e) => setRecordLimit(Math.max(1, parseInt(e.target.value) || 100))}
              inputProps={{ min: 1, max: 5000 }}
            />
          </Grid>

          <Grid item xs={12} md={5}>
            <Stack direction="row" spacing={2}>
              <Button
                variant="contained"
                onClick={fetchStockData}
                disabled={!selectedSymbol || loading}
                startIcon={loading ? <CircularProgress size={20} /> : <RefreshIcon />}
                fullWidth
              >
                {loading ? 'Loading...' : 'Load Data'}
              </Button>

              <Button
                variant="outlined"
                onClick={downloadCSV}
                disabled={!stockData.length}
                startIcon={<DownloadIcon />}
                fullWidth
              >
                Download Visible
              </Button>

              <Button
                variant="outlined"
                onClick={downloadFullDataset}
                disabled={!selectedSymbol}
                startIcon={<DownloadIcon />}
                fullWidth
              >
                Download All
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
            <Chip label={`Total Records: ${stats.total_records?.toLocaleString() || 0}`} />
            <Chip label={`Fields: ${stats.total_fields || 0}`} />
            <Chip label={`Date Range: ${stats.date_range?.start || 'N/A'} to ${stats.date_range?.end || 'N/A'}`} />
            <Chip label={`Latest Price: $${stats.latest_price || 'N/A'}`} color="success" />
          </Stack>
        </Paper>
      )}

      {/* Data Table */}
      {stockData.length > 0 && (
        <Paper sx={{ mb: 3 }}>
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h6">
              {selectedSymbol} - Complete Data View
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Showing {stockData.length} records × {columns.length} fields
              (scroll horizontally to view all columns)
            </Typography>
          </Box>

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
                {stockData.map((row, rowIdx) => (
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
                      const isDateTime = col === 'datetime';

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
        </Paper>
      )}

      {/* Empty State */}
      {!loading && !stockData.length && selectedSymbol && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            No data available for {selectedSymbol}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Click "Load Data" to fetch records
          </Typography>
        </Paper>
      )}

      {/* Initial State */}
      {!selectedSymbol && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            Select a stock symbol to begin
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {symbols.length} symbols available
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

export default DataReconciliation;
