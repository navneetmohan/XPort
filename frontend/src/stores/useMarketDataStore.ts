import { create } from 'zustand';
import {
  PipelineStatus,
  PipelineTaskStatus,
  MarketDataRecord,
  EngineeredFeatureRecord,
} from '../types';
import {
  fetchPipelineStatus,
  triggerMarketDataRefresh,
  fetchTaskStatus,
  fetchSymbolMarketData,
  fetchSymbolFeatures,
} from '../services/marketDataService';

interface MarketDataState {
  pipelineStatus: PipelineStatus | null;
  activeTask: PipelineTaskStatus | null;
  isLoading: boolean;
  isRefreshing: boolean;
  error: string | null;
  selectedSymbol: string | null;
  symbolMarketData: MarketDataRecord[] | null;
  symbolFeatures: EngineeredFeatureRecord[] | null;

  loadPipelineStatus: () => Promise<void>;
  triggerRefresh: (symbols?: string[], lookbackDays?: number) => Promise<string | null>;
  pollTask: (taskId: string) => Promise<PipelineTaskStatus | null>;
  selectSymbol: (symbol: string) => Promise<void>;
  clearSelectedSymbol: () => void;
}

export const useMarketDataStore = create<MarketDataState>((set, get) => ({
  pipelineStatus: null,
  activeTask: null,
  isLoading: false,
  isRefreshing: false,
  error: null,
  selectedSymbol: null,
  symbolMarketData: null,
  symbolFeatures: null,

  loadPipelineStatus: async () => {
    set({ isLoading: true, error: null });
    try {
      const status = await fetchPipelineStatus();
      set({ pipelineStatus: status, isLoading: false });
    } catch (err: any) {
      set({ error: err.message || 'Failed to fetch pipeline status', isLoading: false });
    }
  },

  triggerRefresh: async (symbols?: string[], lookbackDays?: number) => {
    set({ isRefreshing: true, error: null });
    try {
      const resp = await triggerMarketDataRefresh(symbols, lookbackDays);
      const initialTask: PipelineTaskStatus = {
        task_id: resp.task_id,
        status: resp.status,
        ready: false,
      };
      set({ activeTask: initialTask, isRefreshing: false });
      return resp.task_id;
    } catch (err: any) {
      set({ error: err.message || 'Failed to trigger refresh task', isRefreshing: false });
      return null;
    }
  },

  pollTask: async (taskId: string) => {
    try {
      const task = await fetchTaskStatus(taskId);
      set({ activeTask: task });
      if (task.ready) {
        // Automatically reload pipeline status on completion
        get().loadPipelineStatus();
      }
      return task;
    } catch (err: any) {
      return null;
    }
  },

  selectSymbol: async (symbol: string) => {
    set({ selectedSymbol: symbol, symbolMarketData: null, symbolFeatures: null });
    try {
      const [mdRes, feRes] = await Promise.allSettled([
        fetchSymbolMarketData(symbol, 1, 10),
        fetchSymbolFeatures(symbol, 1, 10),
      ]);

      set({
        symbolMarketData: mdRes.status === 'fulfilled' ? mdRes.value.data : [],
        symbolFeatures: feRes.status === 'fulfilled' ? feRes.value.data : [],
      });
    } catch (err: any) {
      // Ignored for graceful degradation
    }
  },

  clearSelectedSymbol: () => {
    set({ selectedSymbol: null, symbolMarketData: null, symbolFeatures: null });
  },
}));
