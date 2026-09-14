import { create } from 'zustand';
import { UserProfile } from '../types';

interface AuthState {
  isAuthenticated: boolean;
  user: UserProfile | null;
  loginMock: () => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: true, // Default to true in foundation stage for seamless preview of views
  user: {
    userId: 'usr_foundation_demo_01',
    email: 'investor@xport.local',
    displayName: 'Retail Investor (Demo)',
  },
  loginMock: () =>
    set({
      isAuthenticated: true,
      user: {
        userId: 'usr_foundation_demo_01',
        email: 'investor@xport.local',
        displayName: 'Retail Investor (Demo)',
      },
    }),
  logout: () => set({ isAuthenticated: false, user: null }),
}));
