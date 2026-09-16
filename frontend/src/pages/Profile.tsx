import React, { useState } from 'react';
import { User, Save, Shield, Calendar, Globe, Info } from 'lucide-react';
import { useProfileStore } from '../stores/useProfileStore';
import { RiskTolerance } from '../types';
import { request, ApiError } from '../services/apiClient';

export const Profile: React.FC = () => {
  const { profile, setRiskTolerance, setInvestmentHorizon } = useProfileStore();
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setFeedback(null);

    try {
      await request('/profiles', {
        method: 'POST',
        body: JSON.stringify({
          risk_tolerance: profile.riskTolerance,
          investment_horizon: profile.investmentHorizon,
          preferred_universe: profile.preferredUniverse,
        }),
      });
    } catch (err: any) {
      if (err instanceof ApiError) {
        setFeedback(
          `Local state updated. Backend API returned: [Status ${err.status}] ${err.message} (${err.data?.stage_scheduled})`
        );
      } else {
        setFeedback(`Error: ${err.message}`);
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: '680px', margin: '0 auto' }}>
      <div className="glass-panel" style={{ padding: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <div
            style={{
              width: '2.5rem',
              height: '2.5rem',
              borderRadius: '10px',
              background: 'var(--primary-subtle)',
              border: '1px solid var(--border-color)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <User size={20} color="var(--primary)" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)' }}>Investor Profile Setup</h1>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Configure your optimization parameters according to SRS UC-02.
            </p>
          </div>
        </div>

        {feedback && (
          <div
            style={{
              padding: '0.85rem 1.25rem',
              background: 'var(--accent-cyan-subtle)',
              border: '1px solid rgba(2, 132, 199, 0.25)',
              borderRadius: 'var(--radius-md)',
              fontSize: '0.85rem',
              color: 'var(--accent-cyan)',
              marginBottom: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
            }}
          >
            <Info size={18} />
            <span>{feedback}</span>
          </div>
        )}

        <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Risk Tolerance */}
          <div>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              <Shield size={16} color="var(--accent-amber)" />
              <span>Risk Tolerance Level</span>
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem' }}>
              {(['Conservative', 'Moderate', 'Aggressive'] as RiskTolerance[]).map((level) => (
                <button
                  type="button"
                  key={level}
                  onClick={() => setRiskTolerance(level)}
                  style={{
                    padding: '0.75rem',
                    borderRadius: 'var(--radius-md)',
                    background: profile.riskTolerance === level ? 'var(--primary)' : 'var(--bg-subtle)',
                    border: profile.riskTolerance === level ? '1px solid var(--primary)' : '1px solid var(--border-color)',
                    color: profile.riskTolerance === level ? '#FFFFFF' : 'var(--text-secondary)',
                    fontWeight: 600,
                    fontSize: '0.85rem',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          {/* Investment Horizon */}
          <div>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              <Calendar size={16} color="var(--accent-cyan)" />
              <span>Investment Horizon: {profile.investmentHorizon} Years</span>
            </label>
            <input
              type="range"
              min="1"
              max="30"
              value={profile.investmentHorizon}
              onChange={(e) => setInvestmentHorizon(Number(e.target.value))}
              style={{
                width: '100%',
                accentColor: 'var(--primary)',
                height: '6px',
                cursor: 'pointer',
              }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
              <span>1 Year (Short-term)</span>
              <span>15 Years</span>
              <span>30 Years (Long-term)</span>
            </div>
          </div>

          {/* Asset Universe */}
          <div>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              <Globe size={16} color="var(--accent-emerald)" />
              <span>Preferred Asset Universe (Curated)</span>
            </label>
            <div
              style={{
                padding: '0.75rem',
                background: 'var(--bg-subtle)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-color)',
                fontSize: '0.85rem',
                display: 'flex',
                flexWrap: 'wrap',
                gap: '0.5rem',
              }}
            >
              {profile.preferredUniverse.map((ticker) => (
                <span key={ticker} className="badge badge-blue">
                  {ticker}
                </span>
              ))}
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
              Curated exchange-listed instruments according to SRS Section 2.4. Full universe selection unlocks in Stage 5.
            </p>
          </div>

          <button
            type="submit"
            disabled={saving}
            className="btn-primary"
            style={{ marginTop: '0.5rem', padding: '0.85rem' }}
          >
            <Save size={16} />
            <span>{saving ? 'Saving Profile...' : 'Save Profile Preferences'}</span>
          </button>
        </form>
      </div>
    </div>
  );
};
