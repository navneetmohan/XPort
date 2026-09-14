import React from 'react';
import { Navbar } from './Navbar';
import { ShieldAlert } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />

      <main style={{ flex: 1, padding: '2rem 0' }}>
        <div className="container">{children}</div>
      </main>

      {/* Mandatory Disclaimer from SRS Section 9 */}
      <footer
        style={{
          borderTop: '1px solid var(--border-color)',
          background: 'rgba(11, 15, 25, 0.95)',
          padding: '1.25rem 0',
          marginTop: 'auto',
        }}
      >
        <div
          className="container"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '0.8rem',
            color: 'var(--text-muted)',
            flexWrap: 'wrap',
            gap: '0.75rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldAlert size={16} color="#F59E0B" />
            <span>
              <strong>Ethical AI & Decision-Support Notice:</strong> XPort is an academic decision-support framework. Recommendations do not constitute regulated financial advice.
            </span>
          </div>
          <div>
            <span>XPort Foundation Stage 1 (~15%) • Rajagiri School of Engineering & Technology</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
