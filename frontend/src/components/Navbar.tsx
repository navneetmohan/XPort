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
  Sun,
  Moon,
} from 'lucide-react';
import { fetchHealthStatus } from '../services/healthService';
import { HealthStatus } from '../types';
import { useAuthStore } from '../stores/useAuthStore';

export const Navbar: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const { user, isAuthenticated, logout } = useAuthStore();

  // Initialize theme from localStorage (defaults to light themed)
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const saved = localStorage.getItem('xport_theme');
    return saved === 'dark' ? 'dark' : 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('xport_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

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
        background: 'var(--bg-navbar)',
        backdropFilter: 'blur(16px)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        transition: 'background-color 0.25s ease, border-color 0.25s ease',
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
              width: '2.1rem',
              height: '2.1rem',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 15px var(--primary-glow)',
            }}
          >
            <Layers size={18} color="#FFFFFF" />
          </div>
          <div>
            <span
              style={{
                fontSize: '1.25rem',
                fontWeight: 800,
                letterSpacing: '-0.02em',
                background: 'linear-gradient(135deg, var(--brand-gradient-start), var(--brand-gradient-end))',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              XPort
            </span>
            <span
              style={{
                fontSize: '0.65rem',
                marginLeft: '0.45rem',
                padding: '0.15rem 0.45rem',
                background: 'var(--primary-subtle)',
                color: 'var(--primary)',
                border: '1px solid var(--border-color)',
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
                  fontWeight: 600,
                  borderRadius: 'var(--radius-md)',
                  color: isActive ? 'var(--primary)' : 'var(--text-secondary)',
                  background: isActive ? 'var(--primary-subtle)' : 'transparent',
                  border: isActive
                    ? '1px solid var(--border-hover)'
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '2.1rem',
              height: '2.1rem',
              borderRadius: 'var(--radius-full)',
              background: 'var(--bg-subtle)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            {theme === 'light' ? <Moon size={16} /> : <Sun size={16} />}
          </button>

          {/* Backend Status Pill */}
          <div
            onClick={checkHealth}
            title="Click to refresh backend health probe"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              padding: '0.35rem 0.75rem',
              background: 'var(--bg-subtle)',
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
              className={loading ? 'spin' : ''}
              style={{
                color: 'var(--text-muted)',
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
