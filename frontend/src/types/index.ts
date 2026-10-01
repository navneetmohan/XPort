export type RiskTolerance = 'Conservative' | 'Moderate' | 'Aggressive';

export interface HealthStatus {
  status: string;
  version: string;
  environment: string;
  timestamp: string;
  database: 'connected' | 'unreachable' | 'unknown';
  redis: 'connected' | 'unreachable' | 'unknown';
}

export interface UserProfile {
  userId: string;
  email: string;
  displayName: string;
  avatarUrl?: string;
  createdAt?: string;
}

export interface InvestorProfile {
  profileId: string;
  userId: string;
  riskTolerance: RiskTolerance;
  investmentHorizon: number; // in years
  liquidityRequirements?: string;
  taxBracket?: string;
  preferredUniverse: string[];
  constraints?: Record<string, unknown>;
  updatedAt?: string;
}

export interface PortfolioAllocationItem {
  instrument: string;
  assetClass: 'Stocks' | 'Mutual Funds' | 'Bonds' | 'Gold' | 'Cash';
  weight: number; // 0.0 - 1.0
}

export interface ParetoCandidate {
  candidateId: string;
  expectedReturn: number;
  volatility: number;
  allocations: PortfolioAllocationItem[];
}

export interface PortfolioRecommendation {
  recommendationId: string;
  taskId: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  profileId: string;
  createdAt: string;
  allocations: PortfolioAllocationItem[];
  paretoSet?: ParetoCandidate[];
  explanationId?: string;
}

export interface FeatureAttribution {
  indicator: 'SMA' | 'EMA' | 'RSI' | 'MACD' | string;
  assetTicker: string;
  contributionValue: number;
  description?: string;
}

export interface ExplainabilityResult {
  explanationId: string;
  recommendationId: string;
  baseValue: number;
  featureAttributions: FeatureAttribution[];
  humanReadableExplanation: string;
  generatedAt: string;
}

export interface WhatIfScenario {
  scenarioId: string;
  originalRecommendationId: string;
  modifiedParameters: {
    investmentAmount?: number;
    riskTolerance?: RiskTolerance;
    investmentHorizon?: number;
  };
  scenarioAllocations: PortfolioAllocationItem[];
  comparison?: {
    expectedReturnDelta: number;
    riskDelta: number;
  };
}

export interface NotImplementedError {
  detail: string;
  status_code: number;
  stage_scheduled: string;
  endpoint: string;
}

export interface MarketDataRecord {
  id: number;
  symbol: string;
  asset_class?: string;
  date: string;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  adj_close?: number;
  volume?: number;
}

export interface EngineeredFeatureRecord {
  id: number;
  symbol: string;
  date: string;
  market_data_id?: number;
  sma_20?: number;
  sma_50?: number;
  ema_20?: number;
  ema_50?: number;
  rsi_14?: number;
  macd?: number;
  macd_signal?: number;
  macd_histogram?: number;
  daily_return?: number;
  rolling_volatility?: number;
}

export interface PipelineInstrumentStatus {
  symbol: string;
  name: string;
  asset_class: string;
  is_yahoo_supported: boolean;
  market_data_records: number;
  market_earliest_date?: string;
  market_latest_date?: string;
  features_records: number;
  features_earliest_date?: string;
  features_latest_date?: string;
  has_market_data: boolean;
  has_features: boolean;
}

export interface PipelineStatus {
  status: string;
  total_universe_instruments: number;
  instruments_with_market_data: number;
  instruments_with_features: number;
  total_market_records: number;
  total_feature_records: number;
  instruments: PipelineInstrumentStatus[];
  timestamp: string;
}

export interface PipelineTaskStatus {
  task_id: string;
  status: string;
  ready: boolean;
  successful?: boolean;
  result?: any;
  error?: string;
}

export interface MarketDataRefreshResponse {
  task_id: string;
  status: string;
  message: string;
  symbols_requested: string[];
}

