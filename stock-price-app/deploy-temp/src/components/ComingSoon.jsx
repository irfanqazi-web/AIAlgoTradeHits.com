import React from 'react';
import { Rocket, Clock, CheckCircle } from 'lucide-react';

const ComingSoon = ({ title, description, features, availableIn, icon: Icon }) => {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%)',
      padding: '100px 20px 40px 20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <div style={{
        maxWidth: '800px',
        width: '100%',
        textAlign: 'center'
      }}>
        {/* Icon */}
        <div style={{
          width: '120px',
          height: '120px',
          margin: '0 auto 30px',
          background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 10px 40px rgba(59, 130, 246, 0.3)'
        }}>
          {Icon ? <Icon size={60} color="white" /> : <Rocket size={60} color="white" />}
        </div>

        {/* Title */}
        <h1 style={{
          fontSize: '48px',
          fontWeight: 'bold',
          background: 'linear-gradient(135deg, #10b981 0%, #3b82f6 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          margin: '0 0 20px 0'
        }}>
          {title}
        </h1>

        {/* Description */}
        <p style={{
          color: '#94a3b8',
          fontSize: '18px',
          lineHeight: '1.6',
          marginBottom: '40px'
        }}>
          {description}
        </p>

        {/* Coming Soon Badge */}
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
          border: '1px solid #334155',
          borderRadius: '12px',
          padding: '12px 24px',
          marginBottom: '40px'
        }}>
          <Clock size={20} color="#10b981" />
          <span style={{ color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
            Coming {availableIn || 'Soon'}
          </span>
        </div>

        {/* Features */}
        {features && features.length > 0 && (
          <div style={{
            background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
            border: '1px solid #334155',
            borderRadius: '16px',
            padding: '40px',
            textAlign: 'left',
            marginBottom: '30px'
          }}>
            <h3 style={{
              color: 'white',
              fontSize: '24px',
              marginBottom: '20px',
              textAlign: 'center'
            }}>
              What to Expect
            </h3>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
              gap: '20px'
            }}>
              {features.map((feature, index) => (
                <div key={index} style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '12px'
                }}>
                  <CheckCircle size={20} color="#10b981" style={{ flexShrink: 0, marginTop: '2px' }} />
                  <span style={{ color: '#94a3b8', fontSize: '15px', lineHeight: '1.5' }}>
                    {feature}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CTA */}
        <div style={{
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          borderRadius: '12px',
          padding: '30px',
          color: 'white'
        }}>
          <h4 style={{ margin: '0 0 10px 0', fontSize: '20px', fontWeight: 'bold' }}>
            Want Early Access?
          </h4>
          <p style={{ margin: '0 0 20px 0', opacity: 0.9, fontSize: '14px' }}>
            Join our PRO tier to get priority access to new features as they launch.
          </p>
          <button style={{
            background: 'white',
            color: '#059669',
            border: 'none',
            padding: '12px 32px',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: 'pointer',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
          }}>
            Upgrade to PRO - $29/month
          </button>
        </div>
      </div>
    </div>
  );
};

export default ComingSoon;
