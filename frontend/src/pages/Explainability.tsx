import React from 'react';
import { HelpCircle, BarChart3, BookOpen } from 'lucide-react';

export const Explainability: React.FC = () => {
  const sampleFeatures = [
    { indicator: 'Momentum (RSI)', asset: 'Equities Basket', value: '+0.34', impact: 'positive' },
    { indicator: 'Trend (EMA 50/200)', asset: 'Growth Sector', value: '+0.22', impact: 'positive' },
    { indicator: 'Trend (SMA 20)', asset: 'Fixed Income', value: '+0.15', impact: 'positive' },
    { indicator: 'MACD Signal Divergence', asset: 'Commodities', value: '-0.10', impact: 'negative' },
    { indicator: 'Short-term Volatility', asset: 'Small Cap', value: '-0.24', impact: 'negative' },
    { indicator: 'Asset Diversification Penalty', asset: 'Portfolio', value: '+0.08', impact: 'positive' },
  ];

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div className="glass-panel" style={{ padding: '1.75rem 2rem', background: 'var(--bg-banner)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <span className="badge badge-purple">XAI Module (UI-04)</span>
          <span className="badge badge-blue">Stage 8 Target</span>
        </div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)' }}>
          Explainability & Feature Contributions
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
          Deconstruct recommendation weights into understandable market indicator attributions using SHAP and rule-based explanations.
        </p>
      </div>

      {/* Grid: SHAP Chart Placeholder and Rule-Based Explanation */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
          gap: '1.5rem',
        }}
      >
        {/* SHAP Feature Contributions Panel */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <BarChart3 size={20} color="var(--accent-purple)" />
              <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>SHAP Feature Attributions</h2>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Wireframe Spec 7.3</span>
          </div>

          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
            Attribution of technical indicators (SMA, EMA, RSI, MACD) to the recommended objective score.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {sampleFeatures.map((item, idx) => (
              <div
                key={idx}
                style={{
                  padding: '0.75rem',
                  background: 'var(--bg-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-color)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{item.indicator}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{item.asset}</div>
                </div>
                <div
                  style={{
                    fontSize: '0.9rem',
                    fontWeight: 700,
                    fontFamily: 'var(--font-mono)',
                    color: item.impact === 'positive' ? 'var(--accent-emerald)' : 'var(--accent-rose)',
                  }}
                >
                  {item.value}
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: '1.5rem', fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center' }}>
            Baseline Model Value: 4.2% &rarr; Predicted Optimization Objective: 8.4%
          </div>
        </div>

        {/* Rule-Based Human-Readable Summary */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
            <BookOpen size={20} color="var(--accent-cyan)" />
            <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Natural Language Justification</h2>
          </div>

          <div
            style={{
              padding: '1rem',
              background: 'var(--accent-cyan-subtle)',
              border: '1px solid rgba(2, 132, 199, 0.2)',
              borderRadius: 'var(--radius-md)',
              lineHeight: 1.6,
              fontSize: '0.875rem',
              color: 'var(--text-primary)',
            }}
          >
            <p style={{ marginBottom: '0.75rem' }}>
              <strong>Rule-Based Explanation Engine (Stage 8):</strong>
            </p>
            <ul style={{ paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', color: 'var(--text-secondary)' }}>
              <li>Momentum (RSI) and long-term trend indicators are strongly positive across large-cap holdings, justifying higher equity allocation.</li>
              <li>Rising short-term volatility dampened exposure to high-beta instruments in accordance with your Moderate risk profile.</li>
              <li>Fixed-income and cash allocations provide sufficient buffer to meet stated liquidity needs.</li>
            </ul>
          </div>

          <div
            style={{
              marginTop: '1.5rem',
              padding: '1rem',
              background: 'var(--bg-subtle)',
              borderRadius: 'var(--radius-md)',
              border: '1px dashed var(--border-color)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <HelpCircle size={16} color="var(--text-muted)" />
              <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                How Explainability Works in XPort
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
              NSGA-II optimizes allocations across return, risk, liquidity, and inflation. SHAP evaluates the contribution of market features toward objective scores, and a rule-based engine translates those scores into human-readable rationale.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
