/**
 * AITrainingDocs Component
 * @version 5.2.0 - Migrated to SSOT architecture
 */
import React, { useState, useEffect, useCallback } from 'react';
import { API_CONFIG } from '@/lib/config';

// Use config for base URL
const API_BASE_URL = API_CONFIG.baseUrl;

const AITrainingDocs = ({ theme = 'dark' }) => {
  const [documents, setDocuments] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [aiStatus, setAiStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [training, setTraining] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Upload form state
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadCategory, setUploadCategory] = useState('general');
  const [uploadDescription, setUploadDescription] = useState('');
  const [newCategory, setNewCategory] = useState('');

  // Theme colors
  const themes = {
    dark: {
      bg: '#0a0a0f',
      cardBg: '#12121a',
      cardBorder: '#1e1e2d',
      text: '#e0e0e0',
      textSecondary: '#8b8b9e',
      accent: '#6366f1',
      accentHover: '#818cf8',
      success: '#22c55e',
      warning: '#f59e0b',
      danger: '#ef4444',
      inputBg: '#1a1a2e'
    },
    light: {
      bg: '#f8fafc',
      cardBg: '#ffffff',
      cardBorder: '#e2e8f0',
      text: '#1e293b',
      textSecondary: '#64748b',
      accent: '#6366f1',
      accentHover: '#818cf8',
      success: '#22c55e',
      warning: '#f59e0b',
      danger: '#ef4444',
      inputBg: '#f1f5f9'
    }
  };

  const currentTheme = themes[theme] || themes.dark;

  // Fetch AI status
  const fetchAiStatus = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/status`);
      const data = await response.json();
      if (data.success) {
        setAiStatus(data);
      }
    } catch (err) {
      console.error('Failed to fetch AI status:', err);
    }
  }, []);

  // Fetch documents
  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/ai/training-docs`);
      const data = await response.json();
      if (data.success) {
        setDocuments(data.documents);
      } else {
        setError(data.error || 'Failed to fetch documents');
      }
    } catch (err) {
      setError('Failed to connect to API');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch categories
  const fetchCategories = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/training-docs/categories`);
      const data = await response.json();
      if (data.success) {
        setCategories(data.categories);
      }
    } catch (err) {
      console.error('Failed to fetch categories:', err);
    }
  }, []);

  useEffect(() => {
    fetchAiStatus();
    fetchDocuments();
    fetchCategories();
  }, [fetchAiStatus, fetchDocuments, fetchCategories]);

  // Upload document
  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) {
      setError('Please select a file to upload');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('category', newCategory || uploadCategory);
      formData.append('description', uploadDescription);
      formData.append('uploaded_by', 'admin');

      const response = await fetch(`${API_BASE_URL}/api/ai/training-docs/upload`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (data.success) {
        setSuccess(`Document "${uploadFile.name}" uploaded successfully!`);
        setUploadFile(null);
        setUploadDescription('');
        setNewCategory('');
        fetchDocuments();
        fetchCategories();
      } else {
        setError(data.error || 'Upload failed');
      }
    } catch (err) {
      setError('Failed to upload document');
      console.error(err);
    } finally {
      setUploading(false);
      setUploadProgress(null);
    }
  };

  // Delete document
  const handleDelete = async (filename) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/training-docs/${encodeURIComponent(filename)}`, {
        method: 'DELETE'
      });

      const data = await response.json();

      if (data.success) {
        setSuccess(`Document deleted successfully`);
        fetchDocuments();
        fetchCategories();
      } else {
        setError(data.error || 'Delete failed');
      }
    } catch (err) {
      setError('Failed to delete document');
      console.error(err);
    }
  };

  // Trigger training
  const handleTrain = async () => {
    if (!window.confirm('Start training the AI model with uploaded documents?')) {
      return;
    }

    setTraining(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/train`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'context',
          categories: selectedCategory === 'all' ? [] : [selectedCategory]
        })
      });

      const data = await response.json();

      if (data.success) {
        setSuccess(`Training completed! Processed ${data.documents_processed} documents.`);
      } else {
        setError(data.error || 'Training failed');
      }
    } catch (err) {
      setError('Failed to start training');
      console.error(err);
    } finally {
      setTraining(false);
    }
  };

  // Format file size
  const formatSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Filter documents by category
  const filteredDocuments = selectedCategory === 'all'
    ? documents
    : documents.filter(doc => doc.name.startsWith(selectedCategory + '/'));

  return (
    <div style={{ padding: '24px', background: currentTheme.bg, minHeight: '100vh' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ color: currentTheme.text, fontSize: '28px', fontWeight: '700', marginBottom: '8px' }}>
          AI Model Training Docs
        </h1>
        <p style={{ color: currentTheme.textSecondary, fontSize: '14px' }}>
          Manage training documents for Vertex AI and Gemini 2.5
        </p>
      </div>

      {/* Status Messages */}
      {error && (
        <div style={{
          padding: '12px 16px',
          background: `${currentTheme.danger}20`,
          border: `1px solid ${currentTheme.danger}`,
          borderRadius: '8px',
          marginBottom: '16px',
          color: currentTheme.danger,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span>{error}</span>
          <button onClick={() => setError(null)} style={{ background: 'none', border: 'none', color: currentTheme.danger, cursor: 'pointer' }}>X</button>
        </div>
      )}

      {success && (
        <div style={{
          padding: '12px 16px',
          background: `${currentTheme.success}20`,
          border: `1px solid ${currentTheme.success}`,
          borderRadius: '8px',
          marginBottom: '16px',
          color: currentTheme.success,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span>{success}</span>
          <button onClick={() => setSuccess(null)} style={{ background: 'none', border: 'none', color: currentTheme.success, cursor: 'pointer' }}>X</button>
        </div>
      )}

      {/* AI Status Card */}
      <div style={{
        background: currentTheme.cardBg,
        border: `1px solid ${currentTheme.cardBorder}`,
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '24px'
      }}>
        <h2 style={{ color: currentTheme.text, fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
          AI Service Status
        </h2>
        {aiStatus ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div style={{ padding: '12px', background: currentTheme.inputBg, borderRadius: '8px' }}>
              <div style={{ color: currentTheme.textSecondary, fontSize: '12px', marginBottom: '4px' }}>Vertex AI</div>
              <div style={{ color: aiStatus.vertex_ai_available ? currentTheme.success : currentTheme.danger, fontWeight: '600' }}>
                {aiStatus.vertex_ai_available ? 'Available' : 'Not Available'}
              </div>
            </div>
            <div style={{ padding: '12px', background: currentTheme.inputBg, borderRadius: '8px' }}>
              <div style={{ color: currentTheme.textSecondary, fontSize: '12px', marginBottom: '4px' }}>Model</div>
              <div style={{ color: currentTheme.text, fontWeight: '600' }}>
                {aiStatus.gemini_model || 'Not configured'}
              </div>
            </div>
            <div style={{ padding: '12px', background: currentTheme.inputBg, borderRadius: '8px' }}>
              <div style={{ color: currentTheme.textSecondary, fontSize: '12px', marginBottom: '4px' }}>Training Bucket</div>
              <div style={{ color: aiStatus.bucket_exists ? currentTheme.success : currentTheme.danger, fontWeight: '600' }}>
                {aiStatus.bucket_exists ? 'Connected' : 'Not Found'}
              </div>
            </div>
            <div style={{ padding: '12px', background: currentTheme.inputBg, borderRadius: '8px' }}>
              <div style={{ color: currentTheme.textSecondary, fontSize: '12px', marginBottom: '4px' }}>Training Documents</div>
              <div style={{ color: currentTheme.text, fontWeight: '600' }}>
                {aiStatus.training_docs_count} files
              </div>
            </div>
          </div>
        ) : (
          <div style={{ color: currentTheme.textSecondary }}>Loading status...</div>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Upload Section */}
        <div style={{
          background: currentTheme.cardBg,
          border: `1px solid ${currentTheme.cardBorder}`,
          borderRadius: '12px',
          padding: '20px'
        }}>
          <h2 style={{ color: currentTheme.text, fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
            Upload Training Document
          </h2>

          <form onSubmit={handleUpload}>
            {/* File Input */}
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', color: currentTheme.textSecondary, fontSize: '14px', marginBottom: '8px' }}>
                Select File
              </label>
              <input
                type="file"
                onChange={(e) => setUploadFile(e.target.files[0])}
                style={{
                  width: '100%',
                  padding: '12px',
                  background: currentTheme.inputBg,
                  border: `1px solid ${currentTheme.cardBorder}`,
                  borderRadius: '8px',
                  color: currentTheme.text
                }}
                accept=".pdf,.doc,.docx,.txt,.csv,.json,.md"
              />
              <div style={{ color: currentTheme.textSecondary, fontSize: '12px', marginTop: '4px' }}>
                Supported: PDF, DOC, DOCX, TXT, CSV, JSON, MD
              </div>
            </div>

            {/* Category Select */}
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', color: currentTheme.textSecondary, fontSize: '14px', marginBottom: '8px' }}>
                Category
              </label>
              <select
                value={uploadCategory}
                onChange={(e) => setUploadCategory(e.target.value)}
                style={{
                  width: '100%',
                  padding: '12px',
                  background: currentTheme.inputBg,
                  border: `1px solid ${currentTheme.cardBorder}`,
                  borderRadius: '8px',
                  color: currentTheme.text
                }}
              >
                <option value="general">General</option>
                <option value="trading-strategies">Trading Strategies</option>
                <option value="technical-analysis">Technical Analysis</option>
                <option value="market-research">Market Research</option>
                <option value="patterns">Chart Patterns</option>
                <option value="indicators">Indicators</option>
                <option value="risk-management">Risk Management</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            {/* New Category */}
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', color: currentTheme.textSecondary, fontSize: '14px', marginBottom: '8px' }}>
                Or Create New Category
              </label>
              <input
                type="text"
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                placeholder="Enter new category name"
                style={{
                  width: '100%',
                  padding: '12px',
                  background: currentTheme.inputBg,
                  border: `1px solid ${currentTheme.cardBorder}`,
                  borderRadius: '8px',
                  color: currentTheme.text
                }}
              />
            </div>

            {/* Description */}
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', color: currentTheme.textSecondary, fontSize: '14px', marginBottom: '8px' }}>
                Description (optional)
              </label>
              <textarea
                value={uploadDescription}
                onChange={(e) => setUploadDescription(e.target.value)}
                placeholder="Brief description of the document"
                rows={3}
                style={{
                  width: '100%',
                  padding: '12px',
                  background: currentTheme.inputBg,
                  border: `1px solid ${currentTheme.cardBorder}`,
                  borderRadius: '8px',
                  color: currentTheme.text,
                  resize: 'vertical'
                }}
              />
            </div>

            {/* Upload Button */}
            <button
              type="submit"
              disabled={uploading || !uploadFile}
              style={{
                width: '100%',
                padding: '14px',
                background: uploading ? currentTheme.cardBorder : currentTheme.accent,
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: uploading ? 'not-allowed' : 'pointer',
                transition: 'background 0.2s'
              }}
            >
              {uploading ? 'Uploading...' : 'Upload Document'}
            </button>
          </form>
        </div>

        {/* Training Section */}
        <div style={{
          background: currentTheme.cardBg,
          border: `1px solid ${currentTheme.cardBorder}`,
          borderRadius: '12px',
          padding: '20px'
        }}>
          <h2 style={{ color: currentTheme.text, fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
            Train AI Model
          </h2>

          <div style={{ marginBottom: '16px' }}>
            <p style={{ color: currentTheme.textSecondary, fontSize: '14px', marginBottom: '16px' }}>
              Train the Gemini 2.5 model with your uploaded documents. The AI will learn from your trading strategies,
              technical analysis guides, and market research to provide better insights.
            </p>

            <div style={{ padding: '16px', background: currentTheme.inputBg, borderRadius: '8px', marginBottom: '16px' }}>
              <div style={{ color: currentTheme.textSecondary, fontSize: '14px', marginBottom: '8px' }}>Training Scope</div>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                style={{
                  width: '100%',
                  padding: '12px',
                  background: currentTheme.cardBg,
                  border: `1px solid ${currentTheme.cardBorder}`,
                  borderRadius: '8px',
                  color: currentTheme.text
                }}
              >
                <option value="all">All Categories</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            <div style={{
              padding: '12px',
              background: `${currentTheme.warning}15`,
              border: `1px solid ${currentTheme.warning}30`,
              borderRadius: '8px',
              marginBottom: '16px'
            }}>
              <div style={{ color: currentTheme.warning, fontSize: '13px' }}>
                Note: Training will process documents and update the AI's context. This may take a few moments.
              </div>
            </div>

            <button
              onClick={handleTrain}
              disabled={training || documents.length === 0}
              style={{
                width: '100%',
                padding: '14px',
                background: training ? currentTheme.cardBorder : currentTheme.success,
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: training ? 'not-allowed' : 'pointer'
              }}
            >
              {training ? 'Training in Progress...' : 'Start Training'}
            </button>
          </div>
        </div>
      </div>

      {/* Documents List */}
      <div style={{
        background: currentTheme.cardBg,
        border: `1px solid ${currentTheme.cardBorder}`,
        borderRadius: '12px',
        padding: '20px',
        marginTop: '24px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 style={{ color: currentTheme.text, fontSize: '18px', fontWeight: '600' }}>
            Training Documents ({filteredDocuments.length})
          </h2>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => setSelectedCategory('all')}
              style={{
                padding: '8px 16px',
                background: selectedCategory === 'all' ? currentTheme.accent : currentTheme.inputBg,
                color: selectedCategory === 'all' ? '#fff' : currentTheme.text,
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '13px'
              }}
            >
              All
            </button>
            {categories.slice(0, 5).map(cat => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                style={{
                  padding: '8px 16px',
                  background: selectedCategory === cat ? currentTheme.accent : currentTheme.inputBg,
                  color: selectedCategory === cat ? '#fff' : currentTheme.text,
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '13px'
                }}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: currentTheme.textSecondary }}>
            Loading documents...
          </div>
        ) : filteredDocuments.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: currentTheme.textSecondary }}>
            No training documents found. Upload some documents to get started.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: `1px solid ${currentTheme.cardBorder}` }}>
                  <th style={{ textAlign: 'left', padding: '12px', color: currentTheme.textSecondary, fontSize: '13px', fontWeight: '500' }}>Name</th>
                  <th style={{ textAlign: 'left', padding: '12px', color: currentTheme.textSecondary, fontSize: '13px', fontWeight: '500' }}>Category</th>
                  <th style={{ textAlign: 'left', padding: '12px', color: currentTheme.textSecondary, fontSize: '13px', fontWeight: '500' }}>Size</th>
                  <th style={{ textAlign: 'left', padding: '12px', color: currentTheme.textSecondary, fontSize: '13px', fontWeight: '500' }}>Type</th>
                  <th style={{ textAlign: 'left', padding: '12px', color: currentTheme.textSecondary, fontSize: '13px', fontWeight: '500' }}>Updated</th>
                  <th style={{ textAlign: 'right', padding: '12px', color: currentTheme.textSecondary, fontSize: '13px', fontWeight: '500' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredDocuments.map((doc, index) => {
                  const parts = doc.name.split('/');
                  const category = parts.length > 1 ? parts[0] : 'uncategorized';
                  const filename = parts[parts.length - 1];

                  return (
                    <tr key={index} style={{ borderBottom: `1px solid ${currentTheme.cardBorder}` }}>
                      <td style={{ padding: '12px', color: currentTheme.text, fontSize: '14px' }}>
                        {filename}
                      </td>
                      <td style={{ padding: '12px' }}>
                        <span style={{
                          padding: '4px 8px',
                          background: currentTheme.inputBg,
                          borderRadius: '4px',
                          color: currentTheme.textSecondary,
                          fontSize: '12px'
                        }}>
                          {category}
                        </span>
                      </td>
                      <td style={{ padding: '12px', color: currentTheme.textSecondary, fontSize: '14px' }}>
                        {formatSize(doc.size)}
                      </td>
                      <td style={{ padding: '12px', color: currentTheme.textSecondary, fontSize: '14px' }}>
                        {doc.content_type || 'unknown'}
                      </td>
                      <td style={{ padding: '12px', color: currentTheme.textSecondary, fontSize: '14px' }}>
                        {doc.updated ? new Date(doc.updated).toLocaleDateString() : '-'}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right' }}>
                        <button
                          onClick={() => handleDelete(doc.name)}
                          style={{
                            padding: '6px 12px',
                            background: `${currentTheme.danger}20`,
                            color: currentTheme.danger,
                            border: `1px solid ${currentTheme.danger}40`,
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '12px'
                          }}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AITrainingDocs;
