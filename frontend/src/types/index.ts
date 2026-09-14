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
