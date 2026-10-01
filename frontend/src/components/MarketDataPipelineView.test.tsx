import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import MarketDataPipelineView from './MarketDataPipelineView';
import * as marketDataService from '../services/marketDataService';

vi.mock('../services/marketDataService', () => ({
  fetchPipelineStatus: vi.fn(),
  fetchUniverseInstruments: vi.fn(),
  triggerMarketDataRefresh: vi.fn(),
  fetchTaskStatus: vi.fn(),
  fetchSymbolMarketData: vi.fn(),
  fetchSymbolFeatures: vi.fn(),
}));

describe('MarketDataPipelineView Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders pipeline title and default metrics', async () => {
    vi.mocked(marketDataService.fetchPipelineStatus).mockResolvedValue({
      status: 'operational',
      total_universe_instruments: 8,
      instruments_with_market_data: 8,
      instruments_with_features: 8,
      total_market_records: 1250,
      total_feature_records: 1250,
      timestamp: '2026-09-30T10:00:00Z',
      instruments: [
        {
          symbol: 'RELIANCE.NS',
          name: 'Reliance Industries Ltd',
          asset_class: 'stocks',
          is_yahoo_supported: true,
          market_data_records: 500,
          market_latest_date: '2026-09-30',
          features_records: 500,
          features_latest_date: '2026-09-30',
          has_market_data: true,
          has_features: true,
        },
      ],
    });

    render(<MarketDataPipelineView />);

    expect(
      screen.getByText('Market Data & Feature Engineering Pipeline')
    ).toBeInTheDocument();
    expect(screen.getByText('Refresh Market Pipeline')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('RELIANCE.NS')).toBeInTheDocument();
      expect(screen.getByText('Reliance Industries Ltd')).toBeInTheDocument();
    });
  });
});
