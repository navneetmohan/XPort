import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Layers, ShieldCheck, Cpu } from 'lucide-react';
import { useAuthStore } from '../stores/useAuthStore';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const { loginMock } = useAuthStore();

  const handleGoogleSignIn = () => {
    loginMock();
    navigate('/');
  };

  return (
    <div
      className="animate-fade-in"
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '70vh',
      }}
    >
      <div
        className="glass-panel"
        style={{
          maxWidth: '440px',
          width: '100%',
          padding: '2.5rem 2rem',
          textAlign: 'center',
          boxShadow: 'var(--shadow-glow)',
        }}
      >
        {/* Brand Icon */}
        <div
          style={{
            width: '3.5rem',
            height: '3.5rem',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1.25rem',
            boxShadow: '0 0 20px rgba(59, 130, 246, 0.4)',
          }}
        >
          <Layers size={28} color="#FFFFFF" />
        </div>

        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '0.5rem' }}>
          Welcome to XPort
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '2rem' }}>
          Explainable Multi-Objective Portfolio Optimization Framework for Personalized Investment Planning.
        </p>

        {/* Feature Highlights */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', textAlign: 'left', marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            <Cpu size={16} color="var(--primary)" />
            <span>NSGA-II multi-objective genetic optimization</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            <ShieldCheck size={16} color="var(--accent-emerald)" />
            <span>SHAP & rule-based transparent explanations</span>
          </div>
        </div>

        {/* Google OAuth Control (UI-01 Wireframe) */}
        <button
          onClick={handleGoogleSignIn}
          className="btn-secondary"
          style={{
            width: '100%',
            padding: '0.85rem 1rem',
            fontSize: '0.95rem',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.75rem',
            background: '#FFFFFF',
            color: '#1F2937',
            border: 'none',
          }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
            />
          </svg>
          <span>Sign in with Google</span>
        </button>

        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '1.25rem' }}>
          By continuing, you acknowledge that XPort is for educational and research decision support. Full Google OAuth 2.0 integration is scheduled for Stage 5.
        </p>
      </div>
    </div>
  );
};
