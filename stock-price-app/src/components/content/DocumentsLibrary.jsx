import { useState, useEffect } from 'react'
import {
  FileText, Download, Eye, Upload, FolderOpen,
  Search, Filter, Calendar, User, BookOpen
} from 'lucide-react'

const DocumentsLibrary = () => {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [viewMode, setViewMode] = useState('grid') // grid or list
  const [selectedDocument, setSelectedDocument] = useState(null)

  const BUCKET_URL = 'https://storage.googleapis.com/trading-app-documents'
  const MANIFEST_URL = `${BUCKET_URL}/manifest.json`

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      const response = await fetch(MANIFEST_URL)
      const data = await response.json()
      setDocuments(data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching documents:', error)
      setLoading(false)
    }
  }

  const categories = ['All', ...new Set(documents.map(doc => doc.category))]

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.filename.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === 'All' || doc.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const getFileIcon = (type) => {
    if (type === 'pdf') return '📄'
    if (type === 'markdown') return '📝'
    if (type === 'docx') return '📘'
    return '📄'
  }

  const getFileColor = (type) => {
    if (type === 'pdf') return '#ef4444'
    if (type === 'markdown') return '#10b981'
    if (type === 'docx') return '#3b82f6'
    return '#6b7280'
  }

  const openDocument = (doc) => {
    // Determine which URL to open based on document type
    let url = null
    if (doc.html_url) {
      url = doc.html_url
    } else if (doc.pdf_url) {
      url = doc.pdf_url
    } else if (doc.md_url) {
      url = doc.md_url
    } else if (doc.docx_url) {
      url = doc.docx_url
    }

    if (url) {
      window.open(url, '_blank')
    }
  }

  const downloadDocument = (doc) => {
    const url = doc.pdf_url || doc.md_url || doc.docx_url
    if (url) {
      const a = document.createElement('a')
      a.href = url
      a.download = doc.filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    }
  }

  if (loading) {
    return (
      <div style={{
        minHeight: '80vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white'
      }}>
        <div style={{ textAlign: 'center' }}>
          <BookOpen size={48} style={{ color: '#10b981', marginBottom: '16px' }} />
          <div>Loading documents...</div>
        </div>
      </div>
    )
  }

  return (
    <div style={{
      padding: '32px',
      maxWidth: '1400px',
      margin: '0 auto',
      background: 'transparent'
    }}>
      {/* Header */}
      <div style={{
        marginBottom: '32px',
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '16px',
        padding: '24px',
        border: '1px solid #334155'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '16px'
        }}>
          <div>
            <h1 style={{
              color: 'white',
              fontSize: '28px',
              fontWeight: '700',
              margin: '0 0 8px 0',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <BookOpen size={32} style={{ color: '#10b981' }} />
              Documents Library
            </h1>
            <p style={{
              color: '#94a3b8',
              fontSize: '14px',
              margin: 0
            }}>
              Access all project documentation, guides, and implementation plans
            </p>
          </div>
          <div style={{
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            color: 'white',
            padding: '12px 20px',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600'
          }}>
            {filteredDocuments.length} Documents
          </div>
        </div>

        {/* Search and Filter */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr auto',
          gap: '12px',
          marginTop: '20px'
        }}>
          <div style={{ position: 'relative' }}>
            <Search
              size={20}
              style={{
                position: 'absolute',
                left: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: '#64748b'
              }}
            />
            <input
              type="text"
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '12px 12px 12px 40px',
                background: '#0f172a',
                border: '1px solid #334155',
                borderRadius: '8px',
                color: 'white',
                fontSize: '14px',
                outline: 'none'
              }}
            />
          </div>

          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            style={{
              padding: '12px 16px',
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '8px',
              color: 'white',
              fontSize: '14px',
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Document Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
        gap: '20px'
      }}>
        {filteredDocuments.map((doc, index) => (
          <div
            key={index}
            style={{
              background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
              borderRadius: '12px',
              padding: '20px',
              border: '1px solid #334155',
              transition: 'all 0.3s ease',
              cursor: 'pointer',
              position: 'relative'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#10b981'
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 8px 24px rgba(16, 185, 129, 0.15)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#334155'
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            {/* Document Type Badge */}
            <div style={{
              position: 'absolute',
              top: '12px',
              right: '12px',
              background: getFileColor(doc.type),
              color: 'white',
              padding: '4px 8px',
              borderRadius: '4px',
              fontSize: '10px',
              fontWeight: '600',
              textTransform: 'uppercase'
            }}>
              {doc.type}
            </div>

            {/* Icon */}
            <div style={{
              fontSize: '48px',
              marginBottom: '16px'
            }}>
              {getFileIcon(doc.type)}
            </div>

            {/* Title */}
            <h3 style={{
              color: 'white',
              fontSize: '16px',
              fontWeight: '600',
              margin: '0 0 8px 0',
              lineHeight: '1.4',
              minHeight: '44px'
            }}>
              {doc.title}
            </h3>

            {/* Category */}
            <div style={{
              color: '#10b981',
              fontSize: '12px',
              fontWeight: '500',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <FolderOpen size={14} />
              {doc.category}
            </div>

            {/* Actions */}
            <div style={{
              display: 'flex',
              gap: '8px',
              marginTop: '16px',
              paddingTop: '16px',
              borderTop: '1px solid #334155'
            }}>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  openDocument(doc)
                }}
                style={{
                  flex: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  padding: '10px',
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '13px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'scale(1.02)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'scale(1)'
                }}
              >
                <Eye size={16} />
                View
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  downloadDocument(doc)
                }}
                style={{
                  flex: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  padding: '10px',
                  background: '#334155',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '13px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = '#475569'
                  e.currentTarget.style.transform = 'scale(1.02)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = '#334155'
                  e.currentTarget.style.transform = 'scale(1)'
                }}
              >
                <Download size={16} />
                Download
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* No Results */}
      {filteredDocuments.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          color: '#64748b'
        }}>
          <FileText size={64} style={{ marginBottom: '16px', opacity: 0.5 }} />
          <h3 style={{ color: '#94a3b8', marginBottom: '8px' }}>No documents found</h3>
          <p style={{ margin: 0 }}>Try adjusting your search or filter</p>
        </div>
      )}

      {/* Upload Instructions */}
      <div style={{
        marginTop: '40px',
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '12px',
        padding: '24px',
        border: '1px solid #334155'
      }}>
        <h3 style={{
          color: '#10b981',
          fontSize: '18px',
          fontWeight: '600',
          marginBottom: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <Upload size={20} />
          Upload New Documents
        </h3>
        <p style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '16px', lineHeight: '1.6' }}>
          Authorized users can upload documents directly to the Cloud Storage bucket:
        </p>
        <div style={{
          background: '#0f172a',
          borderRadius: '8px',
          padding: '16px',
          border: '1px solid #334155',
          fontFamily: 'monospace',
          fontSize: '13px',
          color: '#10b981',
          marginBottom: '16px'
        }}>
          gsutil cp your-document.pdf gs://trading-app-documents/pdf/
        </div>
        <div style={{ color: '#64748b', fontSize: '12px', marginTop: '12px' }}>
          <div style={{ marginBottom: '8px' }}>
            <strong style={{ color: '#94a3b8' }}>Authorized Users:</strong>
          </div>
          <ul style={{ marginLeft: '20px', lineHeight: '1.8' }}>
            <li>haq.irfanul@gmail.com</li>
            <li>saleem26@gmail.com</li>
          </ul>
          <div style={{ marginTop: '12px' }}>
            Or upload via Cloud Console: <a
              href={`https://console.cloud.google.com/storage/browser/trading-app-documents?project=aialgotradehits`}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: '#10b981', textDecoration: 'none' }}
            >
              Open Cloud Storage
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DocumentsLibrary
