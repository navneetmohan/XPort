import { request } from './apiClient';
import {
  MarketDataRecord,
  EngineeredFeatureRecord,
  PipelineStatus,
  PipelineTaskStatus,
  MarketDataRefreshResponse,
} from '../types';

export async function fetchPipelineStatus(): Promise<PipelineStatus> {
  return request<PipelineStatus>('/market-data/status');
}

export async function triggerMarketDataRefresh(
  symbols?: string[],
  lookbackDays?: number
): Promise<MarketDataRefreshResponse> {
  return request<MarketDataRefreshResponse>('/market-data/refresh', {
    method: 'POST',
    body: JSON.stringify({
      symbols: symbols && symbols.length > 0 ? symbols : undefined,
      lookback_days: lookbackDays || 365,
    }),
  });
}

export async function fetchTaskStatus(taskId: string): Promise<PipelineTaskStatus> {
  return request<PipelineTaskStatus>(`/market-data/task/${taskId}`);
}

export async function fetchSymbolMarketData(
  symbol: string,
  page: number = 1,
  pageSize: number = 20
): Promise<{ total: number; page: number; pageSize: number; data: MarketDataRecord[] }> {
  return request<{ total: number; page: number; pageSize: number; data: MarketDataRecord[] }>(
    `/market-data/${encodeURIComponent(symbol)}?page=${page}&page_size=${pageSize}`
  );
}

export async function fetchSymbolFeatures(
  symbol: string,
  page: number = 1,
  pageSize: number = 20
): Promise<{ symbol: string; total: number; page: number; pageSize: number; data: EngineeredFeatureRecord[] }> {
  return request<{ symbol: string; total: number; page: number; pageSize: number; data: EngineeredFeatureRecord[] }>(
    `/features/${encodeURIComponent(symbol)}?page=${page}&page_size=${pageSize}`
  );
}
