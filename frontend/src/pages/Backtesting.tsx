import React from 'react';
import { BarChart2 } from 'lucide-react';

export const Backtesting: React.FC = () => {
  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="glass-panel" style={{ padding: '1.75rem 2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <span className="badge badge-emerald">Simulation (UI-05)</span>
          <span className="badge badge-blue">Stage 9 Target</span>
        </div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Historical Backtesting</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
          Evaluate how the recommended portfolio allocation would have performed over historical market cycles.
        </p>
      </div>

      {/* Date Controls & Summary Metrics Placeholder */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '1rem',
        }}
      >
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Annualized Return</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-emerald)', marginTop: '0.25rem' }}>
            8.1%
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            vs Benchmark 6.9%
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Max Drawdown</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-rose)', marginTop: '0.25rem' }}>
            -11.4%
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Conservative resilience
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Sharpe Ratio</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--primary)', marginTop: '0.25rem' }}>
            1.24
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Risk-adjusted performance
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Lookback Period</div>
          <div style={{ fontSize: '1.1rem', fontWeight: 700, marginTop: '0.25rem' }}>
            5 Years
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            2021 – 2026 Historical OHLCV
          </div>
        </div>
      </div>

      {/* Main Chart Canvas Placeholder */}
      <div className="glass-panel" style={{ padding: '2rem', minHeight: '340px', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
        <div
          style={{
            width: '100%',
            height: '240px',
            borderRadius: 'var(--radius-md)',
            border: '1px dashed var(--border-color)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1rem',
          }}
        >
          <BarChart2 size={42} color="var(--primary)" />
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1rem', fontWeight: 700 }}>Historical Cumulative Return Trajectory</div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Time-series equity curve visualization scheduled for implementation in Stage 9.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
