import { useState } from 'react';
import { LogIn, Mail, Lock, AlertCircle, Eye, EyeOff, User } from 'lucide-react';

// Built-in users for AIAlgoTradeHits
const AUTHORIZED_USERS = {
  'irfan.qazi@aialgotradehits.com': {
    password: 'Trading2024!',
    name: 'Irfan Qazi',
    role: 'admin',
    email: 'irfan.qazi@aialgotradehits.com'
  },
  'saleem.ahmad@aialgotradehits.com': {
    password: 'Trading2024!',
    name: 'Saleem Ahmad',
    role: 'admin',
    email: 'saleem.ahmad@aialgotradehits.com'
  }
};

export default function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Simulate brief loading
    await new Promise(resolve => setTimeout(resolve, 500));

    try {
      const emailLower = email.toLowerCase().trim();
      const user = AUTHORIZED_USERS[emailLower];

      if (user && user.password === password) {
        // Create user session
        const userSession = {
          email: user.email,
          name: user.name,
          role: user.role,
          loginTime: new Date().toISOString()
        };

        // Store in localStorage
        localStorage.setItem('user', JSON.stringify(userSession));
        localStorage.setItem('auth_token', btoa(JSON.stringify({ email: user.email, exp: Date.now() + 86400000 })));

        onLoginSuccess(userSession);
      } else {
        setError('Invalid email or password. Please try again.');
      }
    } catch (err) {
      setError('An error occurred during login. Please try again.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Quick login buttons for easier access
  const quickLogin = (userEmail) => {
    setEmail(userEmail);
    setPassword('Trading2024!');
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%)',
      padding: '20px'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '450px',
        background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        borderRadius: '24px',
        padding: '48px',
        border: '1px solid #334155',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)'
      }}>
        {/* Logo/Header */}
        <div style={{
          textAlign: 'center',
          marginBottom: '40px'
        }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '80px',
            height: '80px',
            background: 'linear-gradient(135deg, #10b981 0%, #3b82f6 100%)',
            borderRadius: '20px',
            marginBottom: '20px'
          }}>
            <LogIn size={40} color="white" />
          </div>
          <h1 style={{
            fontSize: '32px',
            fontWeight: 'bold',
            background: 'linear-gradient(135deg, #10b981 0%, #3b82f6 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            margin: '0 0 8px 0'
          }}>
            AIAlgoTradeHits
          </h1>
          <p style={{
            color: '#94a3b8',
            fontSize: '16px',
            margin: 0
          }}>
            Sign in to your account
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid #ef4444',
            borderRadius: '12px',
            padding: '16px',
            marginBottom: '24px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <AlertCircle size={20} color="#ef4444" />
            <span style={{ color: '#ef4444', fontSize: '14px' }}>{error}</span>
          </div>
        )}

        {/* Quick Login Buttons */}
        <div style={{
          marginBottom: '24px'
        }}>
          <p style={{
            color: '#64748b',
            fontSize: '14px',
            marginBottom: '12px',
            textAlign: 'center'
          }}>
            Quick Login:
          </p>
          <div style={{
            display: 'flex',
            gap: '12px'
          }}>
            <button
              type="button"
              onClick={() => quickLogin('irfan.qazi@aialgotradehits.com')}
              style={{
                flex: 1,
                padding: '12px',
                background: 'rgba(59, 130, 246, 0.1)',
                border: '1px solid #3b82f6',
                borderRadius: '10px',
                color: '#3b82f6',
                fontSize: '13px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => e.target.style.background = 'rgba(59, 130, 246, 0.2)'}
              onMouseOut={(e) => e.target.style.background = 'rgba(59, 130, 246, 0.1)'}
            >
              <User size={16} />
              Irfan Qazi
            </button>
            <button
              type="button"
              onClick={() => quickLogin('saleem.ahmad@aialgotradehits.com')}
              style={{
                flex: 1,
                padding: '12px',
                background: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid #10b981',
                borderRadius: '10px',
                color: '#10b981',
                fontSize: '13px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => e.target.style.background = 'rgba(16, 185, 129, 0.2)'}
              onMouseOut={(e) => e.target.style.background = 'rgba(16, 185, 129, 0.1)'}
            >
              <User size={16} />
              Saleem Ahmad
            </button>
          </div>
        </div>

        {/* Divider */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          margin: '24px 0',
          gap: '16px'
        }}>
          <div style={{
            flex: 1,
            height: '1px',
            background: '#334155'
          }} />
          <span style={{
            color: '#64748b',
            fontSize: '14px'
          }}>
            or enter credentials
          </span>
          <div style={{
            flex: 1,
            height: '1px',
            background: '#334155'
          }} />
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '24px' }}>
            <label style={{
              display: 'block',
              color: '#94a3b8',
              fontSize: '14px',
              fontWeight: '500',
              marginBottom: '8px'
            }}>
              Email Address
            </label>
            <div style={{
              position: 'relative',
              display: 'flex',
              alignItems: 'center'
            }}>
              <Mail
                size={20}
                color="#64748b"
                style={{
                  position: 'absolute',
                  left: '16px',
                  pointerEvents: 'none'
                }}
              />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@aialgotradehits.com"
                style={{
                  width: '100%',
                  padding: '14px 14px 14px 48px',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '12px',
                  color: 'white',
                  fontSize: '16px',
                  outline: 'none',
                  transition: 'all 0.3s'
                }}
                onFocus={(e) => e.target.style.borderColor = '#10b981'}
                onBlur={(e) => e.target.style.borderColor = '#334155'}
              />
            </div>
          </div>

          <div style={{ marginBottom: '32px' }}>
            <label style={{
              display: 'block',
              color: '#94a3b8',
              fontSize: '14px',
              fontWeight: '500',
              marginBottom: '8px'
            }}>
              Password
            </label>
            <div style={{
              position: 'relative',
              display: 'flex',
              alignItems: 'center'
            }}>
              <Lock
                size={20}
                color="#64748b"
                style={{
                  position: 'absolute',
                  left: '16px',
                  pointerEvents: 'none',
                  zIndex: 1
                }}
              />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Enter your password"
                style={{
                  width: '100%',
                  padding: '14px 48px 14px 48px',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '12px',
                  color: 'white',
                  fontSize: '16px',
                  outline: 'none',
                  transition: 'all 0.3s'
                }}
                onFocus={(e) => e.target.style.borderColor = '#10b981'}
                onBlur={(e) => e.target.style.borderColor = '#334155'}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '16px',
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '4px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 1
                }}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? (
                  <EyeOff size={20} color="#64748b" />
                ) : (
                  <Eye size={20} color="#64748b" />
                )}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '16px',
              background: loading
                ? '#64748b'
                : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}
            onMouseOver={(e) => {
              if (!loading) {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 8px 24px rgba(16, 185, 129, 0.3)';
              }
            }}
            onMouseOut={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = 'none';
            }}
          >
            <LogIn size={20} />
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {/* Footer */}
        <div style={{
          marginTop: '32px',
          textAlign: 'center',
          color: '#64748b',
          fontSize: '13px'
        }}>
          <p style={{ margin: 0 }}>
            AIAlgoTradeHits.com Trading Platform
          </p>
          <p style={{ margin: '8px 0 0 0', color: '#475569' }}>
            Authorized users only
          </p>
        </div>
      </div>
    </div>
  );
}
