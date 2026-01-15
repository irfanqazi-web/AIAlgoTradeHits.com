/**
 * Unified Platform API Server
 * Serves: KaamyabPakistan.org, YouInvent.Tech, HomeFranchise.Biz, NoCodeAI.Cloud
 *
 * Node.js + Express + BigQuery
 */

require('dotenv').config();

const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const bodyParser = require('body-parser');
const multer = require('multer');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;

// ==================== MIDDLEWARE ====================

app.disable('x-powered-by');

// CORS - Allow all origins for the platforms
app.use(cors({
  origin: [
    'http://localhost:3000',
    'http://localhost:5173',
    'http://localhost:8080',
    'https://kaamyabpakistan.org',
    'https://youinvent.tech',
    'https://homefranchise.biz',
    'https://nocodeai.cloud',
    /\.run\.app$/,  // Allow all Cloud Run URLs
    /\.web\.app$/,  // Allow Firebase hosting
  ],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

app.use(morgan('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

// File upload config
const multerMid = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 50 * 1024 * 1024 }, // 50MB
});
app.use(multerMid.single('file'));

// ==================== ROUTES ====================

// API Routes
const apiRouter = require('./routers/index');
app.use('/api', apiRouter);

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    platforms: ['KaamyabPakistan', 'YouInvent', 'HomeFranchise', 'NoCodeAI']
  });
});

app.get('/test', (req, res) => {
  res.json({
    success: true,
    message: 'Unified Platform API is running',
    version: '1.0.0'
  });
});

// Platform-specific info endpoints
app.get('/api/platform/kaamyabpakistan', (req, res) => {
  res.json({
    name: 'KaamyabPakistan.org',
    description: 'Pakistan Entrepreneurship Platform',
    features: ['Projects', 'Investors', 'Opportunities']
  });
});

app.get('/api/platform/youinvent', (req, res) => {
  res.json({
    name: 'YouInvent.Tech',
    description: 'Inventor Platform',
    features: ['Submit Inventions', 'Connect with Investors', 'Patent Support']
  });
});

app.get('/api/platform/homefranchise', (req, res) => {
  res.json({
    name: 'HomeFranchise.Biz',
    description: 'Franchise Marketplace',
    features: ['List Franchises', 'Find Opportunities', 'Apply Online']
  });
});

app.get('/api/platform/nocodeai', (req, res) => {
  res.json({
    name: 'NoCodeAI.Cloud',
    description: 'AI Consulting Platform',
    features: ['AI Strategy', 'Custom Solutions', 'Expert Consultants']
  });
});

// ==================== STATIC FILES ====================

// Serve static files for each platform
const publicPath = process.env.NODE_ENV === 'production'
  ? path.join(__dirname, 'public')
  : path.join(__dirname, '../public');

app.use(express.static(publicPath));

// ==================== ERROR HANDLING ====================

// 404 handler
app.use((req, res, next) => {
  if (req.path.startsWith('/api/')) {
    return res.status(404).json({
      success: false,
      message: 'API endpoint not found',
      path: req.path
    });
  }
  next();
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Error:', err.message);
  res.status(500).json({
    success: false,
    message: 'Internal server error',
    error: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// ==================== START SERVER ====================

app.listen(PORT, () => {
  console.log('========================================');
  console.log('  Unified Platform API Server');
  console.log('========================================');
  console.log(`  Port: ${PORT}`);
  console.log(`  Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`  BigQuery Project: ${process.env.GCP_PROJECT_ID || 'aialgotradehits'}`);
  console.log('----------------------------------------');
  console.log('  Platforms Served:');
  console.log('    - KaamyabPakistan.org');
  console.log('    - YouInvent.Tech');
  console.log('    - HomeFranchise.Biz');
  console.log('    - NoCodeAI.Cloud');
  console.log('========================================');
});

module.exports = app;
