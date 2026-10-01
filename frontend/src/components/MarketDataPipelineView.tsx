import React, { useEffect, useState } from 'react';
import {
  Database,
  RefreshCw,
  CheckCircle2,
  Clock,
  ChevronRight,
  TrendingUp,
  X,
  AlertCircle,
} from 'lucide-react';
import { useMarketDataStore } from '../stores/useMarketDataStore';

export const MarketDataPipelineView: React.FC = () => {
  const {
    pipelineStatus,
    activeTask,
    isRefreshing,
    error,
    selectedSymbol,
    symbolMarketData,
    symbolFeatures,
    loadPipelineStatus,
    triggerRefresh,
    pollTask,
    selectSymbol,
    clearSelectedSymbol,
  } = useMarketDataStore();

  const [activeTab, setActiveTab] = useState<'market' | 'features'>('market');

  useEffect(() => {
    loadPipelineStatus();
  }, [loadPipelineStatus]);

  // Poll active task if in progress
  useEffect(() => {
    if (!activeTask || activeTask.ready) return;

    const interval = setInterval(async () => {
      await pollTask(activeTask.task_id);
    }, 2000);

    return () => clearInterval(interval);
  }, [activeTask, pollTask]);

  const handleRefresh = async () => {
    await triggerRefresh();
  };

  const getAssetClassBadge = (ac: string) => {
    switch (ac.toLowerCase()) {
      case 'stocks':
        return <span className="badge badge-blue">Stock</span>;
      case 'mutual_funds':
        return <span className="badge badge-purple">Mutual Fund / ETF</span>;
      case 'gold':
        return <span className="badge badge-amber">Gold</span>;
      case 'bonds':
        return <span className="badge badge-emerald">Bond / Gilt</span>;
      case 'cash':
        return <span className="badge badge-blue">Cash / Overnight</span>;
      default:
        return <span className="badge">{ac}</span>;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Pipeline Status Summary Card */}
      <div className="glass-panel" style={{ padding: '1.5rem 2rem' }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '1rem',
            marginBottom: '1.25rem',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
              <Database size={20} color="var(--primary)" />
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Market Data & Feature Engineering Pipeline
              </h2>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Curated multi-asset universe with automated OHLCV acquisition, data cleaning, and technical indicators.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <button
              onClick={handleRefresh}
              disabled={Boolean(isRefreshing || (activeTask && !activeTask.ready))}
              className="btn-primary"
              style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
            >
              <RefreshCw
                size={15}
                className={isRefreshing || (activeTask && !activeTask.ready) ? 'animate-spin' : ''}
              />
              <span>
                {isRefreshing
                  ? 'Dispatching...'
                  : activeTask && !activeTask.ready
                  ? 'Syncing Pipeline...'
                  : 'Refresh Market Pipeline'}
              </span>
            </button>
          </div>
        </div>

        {error && (
          <div
            style={{
              padding: '0.75rem 1rem',
              borderRadius: '8px',
              backgroundColor: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid var(--accent-rose)',
              color: 'var(--accent-rose)',
              fontSize: '0.875rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              marginBottom: '1rem',
            }}
          >
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {/* Metric Summary Counters */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '1rem',
          }}
        >
          <div style={{ padding: '1rem', borderRadius: '8px', background: 'var(--bg-card)', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Universe Tickers
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.25rem' }}>
              {pipelineStatus?.total_universe_instruments ?? '—'}
            </div>
          </div>

          <div style={{ padding: '1rem', borderRadius: '8px', background: 'var(--bg-card)', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Market Data Ready
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-emerald)', marginTop: '0.25rem' }}>
              {pipelineStatus?.instruments_with_market_data ?? '—'}
              <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: 400 }}>
                /{pipelineStatus?.total_universe_instruments ?? 0}
              </span>
            </div>
          </div>

          <div style={{ padding: '1rem', borderRadius: '8px', background: 'var(--bg-card)', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Features Ready (SMA, EMA, RSI, MACD)
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--primary)', marginTop: '0.25rem' }}>
              {pipelineStatus?.instruments_with_features ?? '—'}
              <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: 400 }}>
                /{pipelineStatus?.total_universe_instruments ?? 0}
              </span>
            </div>
          </div>

          <div style={{ padding: '1rem', borderRadius: '8px', background: 'var(--bg-card)', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Total Stored Records
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.25rem' }}>
              {pipelineStatus ? pipelineStatus.total_market_records.toLocaleString() : '—'}
            </div>
          </div>
        </div>

        {/* Active Task Banner if polling */}
        {activeTask && (
          <div
            style={{
              marginTop: '1.25rem',
              padding: '0.85rem 1.25rem',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              background: 'var(--bg-card)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '0.5rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
              <Clock size={16} color="var(--primary)" />
              <span style={{ color: 'var(--text-secondary)' }}>Celery Task ID:</span>
              <code style={{ color: 'var(--primary)', fontWeight: 600 }}>{activeTask.task_id}</code>
              <span className={`badge ${activeTask.status === 'SUCCESS' ? 'badge-emerald' : activeTask.status === 'FAILURE' ? 'badge-rose' : 'badge-blue'}`}>
                {activeTask.status}
              </span>
            </div>
            {activeTask.result && (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                Fetched: <strong>{activeTask.result.rows_fetched ?? activeTask.result.market_data?.rows_fetched ?? 0}</strong> |
                Persisted: <strong>{activeTask.result.rows_inserted_updated ?? activeTask.result.market_data?.rows_inserted_updated ?? 0}</strong>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Curated Instruments Table */}
      <div className="glass-panel" style={{ padding: '1.5rem 2rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '1rem' }}>
          Configured Instrument Universe & Feature Availability
        </h3>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
                <th style={{ padding: '0.75rem 0.5rem' }}>Symbol</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Asset Class</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Provider</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Market Data</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Date Coverage</th>
                <th style={{ padding: '0.75rem 0.5rem' }}>Features</th>
                <th style={{ padding: '0.75rem 0.5rem', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {pipelineStatus?.instruments?.map((inst) => (
                <tr
                  key={inst.symbol}
                  style={{
                    borderBottom: '1px solid var(--border-color)',
                    transition: 'background-color 0.15s ease',
                  }}
                >
                  <td style={{ padding: '0.75rem 0.5rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    <div>{inst.symbol}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 400 }}>
                      {inst.name}
                    </div>
                  </td>
                  <td style={{ padding: '0.75rem 0.5rem' }}>
                    {getAssetClassBadge(inst.asset_class)}
                  </td>
                  <td style={{ padding: '0.75rem 0.5rem', color: 'var(--text-secondary)' }}>
                    {inst.is_yahoo_supported ? (
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-primary)' }}>Yahoo Finance</span>
                    ) : (
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Fixed Benchmark</span>
                    )}
                  </td>
                  <td style={{ padding: '0.75rem 0.5rem' }}>
                    {inst.has_market_data ? (
                      <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>
                        {inst.market_data_records} bars
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-secondary)' }}>Pending Sync</span>
                    )}
                  </td>
                  <td style={{ padding: '0.75rem 0.5rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    {inst.market_earliest_date && inst.market_latest_date
                      ? `${inst.market_earliest_date} → ${inst.market_latest_date}`
                      : '—'}
                  </td>
                  <td style={{ padding: '0.75rem 0.5rem' }}>
                    {inst.has_features ? (
                      <span className="badge badge-emerald" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        <CheckCircle2 size={12} />
                        {inst.features_records} rows
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>Not Computed</span>
                    )}
                  </td>
                  <td style={{ padding: '0.75rem 0.5rem', textAlign: 'right' }}>
                    <button
                      onClick={() => selectSymbol(inst.symbol)}
                      className="btn-secondary"
                      style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }}
                    >
                      <span>Inspect</span>
                      <ChevronRight size={13} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Selected Instrument Inspection Modal/Drawer */}
      {selectedSymbol && (
        <div className="glass-panel" style={{ padding: '1.5rem 2rem', position: 'relative' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <TrendingUp size={20} color="var(--primary)" />
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Inspect Instrument: <span style={{ color: 'var(--primary)' }}>{selectedSymbol}</span>
              </h3>
            </div>
            <button
              onClick={clearSelectedSymbol}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)' }}
            >
              <X size={20} />
            </button>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
            <button
              onClick={() => setActiveTab('market')}
              style={{
                padding: '0.4rem 0.85rem',
                borderRadius: '6px',
                border: 'none',
                cursor: 'pointer',
                background: activeTab === 'market' ? 'var(--primary)' : 'transparent',
                color: activeTab === 'market' ? '#fff' : 'var(--text-secondary)',
                fontWeight: 600,
                fontSize: '0.85rem',
              }}
            >
              Recent Raw OHLCV Data
            </button>
            <button
              onClick={() => setActiveTab('features')}
              style={{
                padding: '0.4rem 0.85rem',
                borderRadius: '6px',
                border: 'none',
                cursor: 'pointer',
                background: activeTab === 'features' ? 'var(--primary)' : 'transparent',
                color: activeTab === 'features' ? '#fff' : 'var(--text-secondary)',
                fontWeight: 600,
                fontSize: '0.85rem',
              }}
            >
              Engineered Features (SMA, EMA, RSI, MACD)
            </button>
          </div>

          {activeTab === 'market' ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.8rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
                    <th style={{ padding: '0.5rem' }}>Date</th>
                    <th style={{ padding: '0.5rem' }}>Open</th>
                    <th style={{ padding: '0.5rem' }}>High</th>
                    <th style={{ padding: '0.5rem' }}>Low</th>
                    <th style={{ padding: '0.5rem' }}>Close</th>
                    <th style={{ padding: '0.5rem' }}>Adj Close</th>
                    <th style={{ padding: '0.5rem' }}>Volume</th>
                  </tr>
                </thead>
                <tbody>
                  {symbolMarketData && symbolMarketData.length > 0 ? (
                    symbolMarketData.map((m) => (
                      <tr key={m.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td style={{ padding: '0.5rem', fontWeight: 600 }}>{m.date}</td>
                        <td style={{ padding: '0.5rem' }}>{m.open?.toFixed(2)}</td>
                        <td style={{ padding: '0.5rem' }}>{m.high?.toFixed(2)}</td>
                        <td style={{ padding: '0.5rem' }}>{m.low?.toFixed(2)}</td>
                        <td style={{ padding: '0.5rem', fontWeight: 600, color: 'var(--text-primary)' }}>{m.close?.toFixed(2)}</td>
                        <td style={{ padding: '0.5rem' }}>{m.adj_close?.toFixed(2)}</td>
                        <td style={{ padding: '0.5rem' }}>{m.volume?.toLocaleString()}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={7} style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                        No raw market data bars found. Click "Refresh Market Pipeline" to sync.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.8rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
                    <th style={{ padding: '0.5rem' }}>Date</th>
                    <th style={{ padding: '0.5rem' }}>SMA (20)</th>
                    <th style={{ padding: '0.5rem' }}>SMA (50)</th>
                    <th style={{ padding: '0.5rem' }}>EMA (20)</th>
                    <th style={{ padding: '0.5rem' }}>EMA (50)</th>
                    <th style={{ padding: '0.5rem' }}>RSI (14)</th>
                    <th style={{ padding: '0.5rem' }}>MACD</th>
                    <th style={{ padding: '0.5rem' }}>Signal</th>
                    <th style={{ padding: '0.5rem' }}>Daily Ret</th>
                  </tr>
                </thead>
                <tbody>
                  {symbolFeatures && symbolFeatures.length > 0 ? (
                    symbolFeatures.map((f) => (
                      <tr key={f.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td style={{ padding: '0.5rem', fontWeight: 600 }}>{f.date}</td>
                        <td style={{ padding: '0.5rem' }}>{f.sma_20?.toFixed(2) ?? '—'}</td>
                        <td style={{ padding: '0.5rem' }}>{f.sma_50?.toFixed(2) ?? '—'}</td>
                        <td style={{ padding: '0.5rem' }}>{f.ema_20?.toFixed(2) ?? '—'}</td>
                        <td style={{ padding: '0.5rem' }}>{f.ema_50?.toFixed(2) ?? '—'}</td>
                        <td style={{ padding: '0.5rem', fontWeight: 600, color: (f.rsi_14 ?? 50) > 70 ? 'var(--accent-rose)' : (f.rsi_14 ?? 50) < 30 ? 'var(--accent-emerald)' : 'var(--text-primary)' }}>
                          {f.rsi_14?.toFixed(1) ?? '—'}
                        </td>
                        <td style={{ padding: '0.5rem' }}>{f.macd?.toFixed(3) ?? '—'}</td>
                        <td style={{ padding: '0.5rem' }}>{f.macd_signal?.toFixed(3) ?? '—'}</td>
                        <td style={{ padding: '0.5rem', color: (f.daily_return ?? 0) >= 0 ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
                          {f.daily_return != null ? `${(f.daily_return * 100).toFixed(2)}%` : '—'}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={9} style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                        No engineered features found for this instrument. Click "Refresh Market Pipeline" to compute.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MarketDataPipelineView;
