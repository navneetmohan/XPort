import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  PieChart,
  TrendingUp,
  Sliders,
  Sparkles,
  Activity,
  Info,
  CheckCircle2,
} from 'lucide-react';
import { useProfileStore } from '../stores/useProfileStore';
import { request, ApiError } from '../services/apiClient';

export const Dashboard: React.FC = () => {
  const { profile } = useProfileStore();
  const [loading, setLoading] = useState(false);
  const [apiResponse, setApiResponse] = useState<string | null>(null);

  const handleTriggerRecommendation = async () => {
    setLoading(true);
    setApiResponse(null);
    try {
      await request('/recommendations', {
        method: 'POST',
        body: JSON.stringify({
          profile_id: profile.profileId,
          risk_tolerance: profile.riskTolerance,
          investment_horizon: profile.investmentHorizon,
        }),
      });
    } catch (err: any) {
      if (err instanceof ApiError) {
        setApiResponse(
          `[Status ${err.status}] ${err.message} (Scheduled for: ${
            err.data?.stage_scheduled || 'Stage 7'
          })`
        );
      } else {
        setApiResponse(`Error: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Top Banner */}
      <div
        className="glass-panel"
        style={{
          padding: '1.75rem 2rem',
          background: 'var(--bg-banner)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <span className="badge badge-blue">Foundation Phase 1 (~15%)</span>
            <span className="badge badge-emerald">Interactive Dashboard</span>
          </div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
            Portfolio Optimization Overview
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            Multi-objective trade-off balancing returns, risk, liquidity, and inflation with explainable AI.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            onClick={handleTriggerRecommendation}
            disabled={loading}
            className="btn-primary"
          >
            <TrendingUp size={16} />
            <span>{loading ? 'Submitting to Celery...' : 'Generate Recommendation'}</span>
          </button>
        </div>
      </div>

      {/* API Response Alert Banner if button clicked */}
      {apiResponse && (
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
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-cyan)' }}>
              Backend API Contract Verified
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              {apiResponse}
            </div>
          </div>
          <button
            onClick={() => setApiResponse(null)}
            style={{ background: 'transparent', color: 'var(--text-muted)', fontSize: '0.8rem' }}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Main Grid: Investment Summary, Allocation, Pareto Frontier */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '1.5rem',
        }}
      >
        {/* Card 1: Investment Summary */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Investment Profile</h2>
            <Link to="/profile" style={{ fontSize: '0.8rem', color: 'var(--primary)', fontWeight: 600 }}>
              Edit Profile &rarr;
            </Link>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                padding: '0.75rem',
                background: 'var(--bg-subtle)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-color)',
              }}
            >
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Risk Tolerance</span>
              <span className="badge badge-amber">{profile.riskTolerance}</span>
            </div>

            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                padding: '0.75rem',
                background: 'var(--bg-subtle)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-color)',
              }}
            >
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Time Horizon</span>
              <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{profile.investmentHorizon} Years</span>
            </div>

            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                padding: '0.75rem',
                background: 'var(--bg-subtle)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-color)',
              }}
            >
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Target Universe</span>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {profile.preferredUniverse.slice(0, 4).join(', ')} +3 more
              </span>
            </div>

            <div
              style={{
                marginTop: '0.5rem',
                padding: '0.75rem',
                background: 'var(--accent-emerald-subtle)',
                border: '1px solid rgba(5, 150, 105, 0.25)',
                borderRadius: 'var(--radius-sm)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
              }}
            >
              <CheckCircle2 size={16} color="var(--accent-emerald)" />
              <span style={{ fontSize: '0.8rem', color: 'var(--accent-emerald)', fontWeight: 600 }}>
                Foundation Baseline Profile Active
              </span>
            </div>
          </div>
        </div>

        {/* Card 2: Recommended Portfolio Allocation (Placeholder) */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Portfolio Allocation</h2>
            <span className="badge badge-purple">Stage 7 Target</span>
          </div>

          {/* Allocation Breakdown Placeholder View */}
          <div
            style={{
              height: '180px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--bg-subtle)',
              border: '1px dashed var(--border-color)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.75rem',
              padding: '1rem',
              textAlign: 'center',
            }}
          >
            <PieChart size={36} color="var(--primary)" />
            <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>
              Allocation Visualization Container
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', maxWidth: '280px' }}>
              Shows asset class weights (Stocks, Mutual Funds, Bonds, Gold, Cash) generated via NSGA-II.
            </p>
          </div>

          <div style={{ marginTop: '1.25rem', display: 'flex', justifyContent: 'space-between' }}>
            <Link to="/explainability" className="btn-secondary" style={{ flex: 1, fontSize: '0.8rem' }}>
              <Sparkles size={14} />
              <span>View Explanation</span>
            </Link>
          </div>
        </div>

        {/* Card 3: Pareto Frontier (Placeholder) */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Pareto Frontier</h2>
            <span className="badge badge-blue">NSGA-II Space</span>
          </div>

          <div
            style={{
              height: '180px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--bg-subtle)',
              border: '1px dashed var(--border-color)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.75rem',
              padding: '1rem',
              textAlign: 'center',
            }}
          >
            <Activity size={36} color="var(--accent-cyan)" />
            <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>
              Multi-Objective Trade-off Scatter Plot
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', maxWidth: '280px' }}>
              Interactive non-dominated solutions balancing Expected Return vs. Volatility & Liquidity.
            </p>
          </div>

          <div style={{ marginTop: '1.25rem', display: 'flex', gap: '0.5rem' }}>
            <Link to="/whatif" className="btn-secondary" style={{ flex: 1, fontSize: '0.8rem' }}>
              <Sliders size={14} />
              <span>What-if Simulator</span>
            </Link>
            <Link to="/backtesting" className="btn-secondary" style={{ flex: 1, fontSize: '0.8rem' }}>
              <TrendingUp size={14} />
              <span>Backtest</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Architecture Verification Footer Card */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <h3 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--text-primary)' }}>
          Foundation Infrastructure Pipeline
        </h3>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '1rem',
          }}
        >
          <div style={{ padding: '0.75rem', background: 'var(--bg-subtle)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Edge Gateway</div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, marginTop: '0.2rem' }}>Nginx Reverse Proxy</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--accent-emerald)', marginTop: '0.2rem', fontWeight: 600 }}>Port 80 (Gateway)</div>
          </div>
          <div style={{ padding: '0.75rem', background: 'var(--bg-subtle)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Application Tier</div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, marginTop: '0.2rem' }}>FastAPI REST Service</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--accent-emerald)', marginTop: '0.2rem', fontWeight: 600 }}>Port 8000 (API v1)</div>
          </div>
          <div style={{ padding: '0.75rem', background: 'var(--bg-subtle)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Asynchronous Tasks</div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, marginTop: '0.2rem' }}>Celery Worker + Redis</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--accent-cyan)', marginTop: '0.2rem', fontWeight: 600 }}>Port 6379 (Broker)</div>
          </div>
          <div style={{ padding: '0.75rem', background: 'var(--bg-subtle)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Relational Storage</div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, marginTop: '0.2rem' }}>PostgreSQL 15 + Alembic</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--accent-purple)', marginTop: '0.2rem', fontWeight: 600 }}>Port 5432 (Database)</div>
          </div>
        </div>
      </div>
    </div>
  );
};
