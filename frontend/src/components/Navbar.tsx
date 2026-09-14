import React, { useEffect, useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import {
  PieChart,
  Activity,
  Layers,
  Sparkles,
  Sliders,
  User,
  RefreshCw,
} from 'lucide-react';
import { fetchHealthStatus } from '../services/healthService';
import { HealthStatus } from '../types';
import { useAuthStore } from '../stores/useAuthStore';

export const Navbar: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const { user, isAuthenticated, logout } = useAuthStore();

  const checkHealth = async () => {
    setLoading(true);
    try {
      const data = await fetchHealthStatus();
      setHealth(data);
    } catch {
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const navLinks = [
    { to: '/', label: 'Dashboard', icon: PieChart },
    { to: '/explainability', label: 'Explainability', icon: Sparkles },
    { to: '/backtesting', label: 'Backtesting', icon: Activity },
    { to: '/whatif', label: 'What-if', icon: Sliders },
    { to: '/profile', label: 'Profile', icon: User },
  ];

  return (
    <header
      style={{
        borderBottom: '1px solid var(--border-color)',
        background: 'rgba(11, 15, 25, 0.85)',
        backdropFilter: 'blur(16px)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      <div
        className="container"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          height: '4rem',
        }}
      >
        {/* Brand */}
        <Link
          to="/"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
          }}
        >
          <div
            style={{
              width: '2rem',
              height: '2rem',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 15px rgba(59, 130, 246, 0.4)',
            }}
          >
            <Layers size={18} color="#FFFFFF" />
          </div>
          <div>
            <span
              style={{
                fontSize: '1.2rem',
                fontWeight: 800,
                letterSpacing: '-0.02em',
                background: 'linear-gradient(to right, #FFFFFF, #93C5FD)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              XPort
            </span>
            <span
              style={{
                fontSize: '0.65rem',
                marginLeft: '0.4rem',
                padding: '0.15rem 0.4rem',
                background: 'rgba(59, 130, 246, 0.2)',
                color: '#60A5FA',
                borderRadius: '4px',
                fontWeight: 600,
              }}
            >
              v0.1 Foundation
            </span>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav style={{ display: 'flex', gap: '0.5rem' }}>
          {navLinks.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                style={({ isActive }) => ({
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  padding: '0.45rem 0.85rem',
                  fontSize: '0.85rem',
                  fontWeight: 500,
                  borderRadius: 'var(--radius-md)',
                  color: isActive ? '#FFFFFF' : 'var(--text-secondary)',
                  background: isActive ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
                  border: isActive
                    ? '1px solid rgba(59, 130, 246, 0.3)'
                    : '1px solid transparent',
                  transition: 'all 0.15s ease',
                })}
              >
                <Icon size={16} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Right Status & Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {/* Backend Status Pill */}
          <div
            onClick={checkHealth}
            title="Click to refresh backend health probe"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              padding: '0.35rem 0.75rem',
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-full)',
              fontSize: '0.75rem',
              cursor: 'pointer',
              userSelect: 'none',
            }}
          >
            <span
              className={`status-dot ${
                health?.status === 'ok' ? 'online' : loading ? 'pending' : 'offline'
              }`}
            />
            <span style={{ color: 'var(--text-secondary)' }}>
              API:{' '}
              {health?.status === 'ok' ? (
                <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>
                  Connected
                </span>
              ) : loading ? (
                <span style={{ color: 'var(--accent-amber)' }}>Checking...</span>
              ) : (
                <span style={{ color: 'var(--accent-rose)', fontWeight: 600 }}>
                  Offline
                </span>
              )}
            </span>
            <RefreshCw
              size={12}
              style={{
                color: 'var(--text-muted)',
                animation: loading ? 'spin 1s linear infinite' : 'none',
              }}
            />
          </div>

          {/* User Profile / Auth Toggle */}
          {isAuthenticated ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <div
                style={{
                  width: '2rem',
                  height: '2rem',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.8rem',
                  fontWeight: 700,
                  color: '#FFFFFF',
                }}
              >
                {user?.displayName ? user.displayName.charAt(0) : 'U'}
              </div>
              <button
                onClick={logout}
                className="btn-secondary"
                style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }}
              >
                Sign Out
              </button>
            </div>
          ) : (
            <Link to="/login" className="btn-primary" style={{ padding: '0.4rem 0.9rem', fontSize: '0.8rem' }}>
              Sign In
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};
