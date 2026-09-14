import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('XPort Frontend Foundation', () => {
  it('renders application brand and navigation links', () => {
    render(<App />);
    expect(screen.getByText('XPort')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Explainability')).toBeInTheDocument();
    expect(screen.getByText('Backtesting')).toBeInTheDocument();
    expect(screen.getByText('What-if')).toBeInTheDocument();
    expect(screen.getByText('Profile')).toBeInTheDocument();
  });

  it('renders ethical decision-support disclaimer banner', () => {
    render(<App />);
    expect(
      screen.getByText(/Ethical AI & Decision-Support Notice:/i)
    ).toBeInTheDocument();
  });
});
