import { create } from 'zustand';
import { InvestorProfile, RiskTolerance } from '../types';

interface ProfileState {
  profile: InvestorProfile;
  setRiskTolerance: (level: RiskTolerance) => void;
  setInvestmentHorizon: (years: number) => void;
  setPreferredUniverse: (universe: string[]) => void;
}

export const useProfileStore = create<ProfileState>((set) => ({
  profile: {
    profileId: 'prf_foundation_01',
    userId: 'usr_foundation_demo_01',
    riskTolerance: 'Moderate',
    investmentHorizon: 5,
    liquidityRequirements: 'Medium',
    taxBracket: '20%',
    preferredUniverse: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'BND', 'GLD'],
  },
  setRiskTolerance: (level) =>
    set((state) => ({ profile: { ...state.profile, riskTolerance: level } })),
  setInvestmentHorizon: (years) =>
    set((state) => ({ profile: { ...state.profile, investmentHorizon: years } })),
  setPreferredUniverse: (universe) =>
    set((state) => ({ profile: { ...state.profile, preferredUniverse: universe } })),
}));
