import React, { useState } from 'react';
import { RefreshCw, Info } from 'lucide-react';
import { request, ApiError } from '../services/apiClient';

export const WhatIf: React.FC = () => {
  const [amount, setAmount] = useState(100000);
  const [horizon, setHorizon] = useState(5);
  const [risk, setRisk] = useState<'Conservative' | 'Moderate' | 'Aggressive'>('Moderate');
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const handleSimulate = async () => {
    setLoading(true);
    setFeedback(null);
    try {
      await request('/whatif', {
        method: 'POST',
        body: JSON.stringify({
          recommendation_id: 'rec_foundation_sample_01',
          modified_parameters: {
            investment_amount: amount,
            investment_horizon: horizon,
            risk_tolerance: risk,
          },
        }),
      });
    } catch (err: any) {
      if (err instanceof ApiError) {
        setFeedback(
          `[Status ${err.status}] ${err.message} (${err.data?.stage_scheduled})`
        );
      } else {
        setFeedback(`Error: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="glass-panel" style={{ padding: '1.75rem 2rem', background: 'var(--bg-banner)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <span className="badge badge-amber">Scenario Analysis (UI-05)</span>
          <span className="badge badge-blue">Stage 9 Target</span>
        </div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)' }}>What-if Scenario Simulator</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
          Modify investment parameters to test hypothetical allocations and observe sensitivity trade-offs side-by-side without altering your primary recommendation.
        </p>
      </div>

      {feedback && (
        <div
          className="glass-panel"
          style={{
            padding: '1rem 1.5rem',
            borderLeft: '4px solid var(--accent-cyan)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            background: 'var(--accent-cyan-subtle)',
          }}
        >
          <Info size={20} color="var(--accent-cyan)" />
          <div style={{ flex: 1, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            {feedback}
          </div>
        </div>
      )}

      {/* Grid: Controls and Comparison */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '1.5rem',
        }}
      >
        {/* Scenario Controls Panel */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1.25rem' }}>
            Adjust Scenario Parameters
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.4rem' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Investment Capital</span>
                <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>₹{amount.toLocaleString()}</span>
              </div>
              <input
                type="range"
                min="10000"
                max="1000000"
                step="10000"
                value={amount}
                onChange={(e) => setAmount(Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--primary)' }}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.4rem' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Time Horizon</span>
                <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{horizon} Years</span>
              </div>
              <input
                type="range"
                min="1"
                max="25"
                value={horizon}
                onChange={(e) => setHorizon(Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--primary)' }}
              />
            </div>

            <div>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.4rem' }}>
                Scenario Risk Tolerance
              </span>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem' }}>
                {(['Conservative', 'Moderate', 'Aggressive'] as const).map((lvl) => (
                  <button
                    key={lvl}
                    type="button"
                    onClick={() => setRisk(lvl)}
                    style={{
                      padding: '0.5rem',
                      borderRadius: 'var(--radius-sm)',
                      background: risk === lvl ? 'var(--primary)' : 'var(--bg-subtle)',
                      border: risk === lvl ? '1px solid var(--primary)' : '1px solid var(--border-color)',
                      color: risk === lvl ? '#FFFFFF' : 'var(--text-secondary)',
                      fontSize: '0.8rem',
                      fontWeight: 600,
                      transition: 'all 0.15s ease',
                    }}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handleSimulate}
              disabled={loading}
              className="btn-primary"
              style={{ marginTop: '0.5rem' }}
            >
              <RefreshCw size={16} className={loading ? 'spin' : ''} />
              <span>{loading ? 'Re-optimizing...' : 'Simulate Scenario (Celery)'}</span>
            </button>
          </div>
        </div>

        {/* Side-by-Side Comparison Container Placeholder */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1.25rem' }}>
            Side-by-Side Comparison
          </h2>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '1rem',
              height: '240px',
            }}
          >
            <div
              style={{
                border: '1px dashed var(--border-color)',
                borderRadius: 'var(--radius-md)',
                background: 'var(--bg-subtle)',
                padding: '1rem',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)' }}>
                Baseline Allocation
              </div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, marginTop: '0.5rem', color: 'var(--text-primary)' }}>
                Moderate
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                50% Equities / 50% Debt
              </div>
            </div>

            <div
              style={{
                border: '1px dashed var(--primary)',
                borderRadius: 'var(--radius-md)',
                padding: '1rem',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center',
                background: 'var(--primary-subtle)',
              }}
            >
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--primary)' }}>
                Simulated Allocation
              </div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, marginTop: '0.5rem', color: 'var(--primary)' }}>
                {risk}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Dynamic weights via NSGA-II
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
