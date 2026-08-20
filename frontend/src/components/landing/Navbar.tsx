import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const navItems = [
  { id: '01', label: 'DASHBOARD', path: '/dashboard' },
  { id: '02', label: 'SIMULATE',  path: '/dashboard' },
  { id: '03', label: 'ORPHANS',   path: '/dashboard' },
  { id: '04', label: 'RECOVERY',  path: '/dashboard' },
  { id: '05', label: 'INSIGHTS',  path: '/dashboard' },
  { id: '06', label: 'SETTINGS',  path: '/dashboard' },
];

export default function Navbar() {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        padding: '18px 28px 14px',
        borderBottom: '1px solid rgba(255,255,255,0.12)',
        background: 'rgba(0,0,0,0.85)',
        backdropFilter: 'blur(4px)',
        fontFamily: 'var(--font-mono)',
      }}
      aria-label="Main navigation"
    >
      {/* LEFT: Brand */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '3px', flexShrink: 0 }}>
        {/* Corner bracket top-left */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {/* Mini grid icon */}
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <rect x="2" y="2" width="7" height="7" stroke="rgba(255,255,255,0.5)" strokeWidth="1"/>
            <rect x="11" y="2" width="7" height="7" stroke="rgba(255,255,255,0.5)" strokeWidth="1"/>
            <rect x="2" y="11" width="7" height="7" stroke="rgba(255,255,255,0.5)" strokeWidth="1"/>
            <rect x="11" y="11" width="7" height="7" stroke="rgba(255,255,255,0.5)" strokeWidth="1"/>
          </svg>
          <button
            onClick={() => navigate('/')}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontFamily: 'var(--font-mono)',
              fontSize: '18px',
              fontWeight: 700,
              color: '#fff',
              letterSpacing: '0.12em',
              padding: 0,
              lineHeight: 1,
            }}
            aria-label="BLACKOUT - Go to home"
          >
            BLACKOUT
          </button>
        </div>
        <span style={{
          fontSize: '8px',
          color: 'rgba(255,255,255,0.4)',
          letterSpacing: '0.2em',
          textTransform: 'uppercase',
          paddingLeft: '30px',
        }}>
          CHAOS TESTING FOR ENTERPRISE KNOWLEDGE
        </span>
      </div>

      {/* CENTER: Nav links (desktop) */}
      <div
        className="nav-links"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '28px',
          flexShrink: 0,
        }}
      >
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => navigate(item.path)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontFamily: 'var(--font-mono)',
              fontSize: '10px',
              color: 'rgba(255,255,255,0.55)',
              letterSpacing: '0.15em',
              padding: '4px 0',
              transition: 'color 0.2s ease',
              position: 'relative',
            }}
            onMouseEnter={e => (e.currentTarget.style.color = '#fff')}
            onMouseLeave={e => (e.currentTarget.style.color = 'rgba(255,255,255,0.55)')}
            aria-label={`Navigate to ${item.label}`}
          >
            <span style={{ color: 'rgba(255,255,255,0.3)' }}>[{item.id}]</span>
            {' '}{item.label}
          </button>
        ))}
      </div>

      {/* RIGHT: SYSTEM ONLINE + grid menu */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexShrink: 0 }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '7px',
            border: '1px solid rgba(255,255,255,0.22)',
            padding: '5px 12px',
            fontSize: '9px',
            letterSpacing: '0.18em',
            color: 'rgba(255,255,255,0.75)',
          }}
          aria-label="System status: online"
        >
          <span
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              background: '#fff',
              display: 'inline-block',
              animation: 'blink 2.5s ease-in-out infinite',
            }}
            aria-hidden="true"
          />
          SYSTEM ONLINE
        </div>

        {/* Grid / hamburger icon */}
        <button
          onClick={() => setMenuOpen(o => !o)}
          style={{
            background: 'none',
            border: '1px solid rgba(255,255,255,0.22)',
            cursor: 'pointer',
            padding: '5px 8px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '3px',
          }}
          aria-label="Toggle mobile menu"
          aria-expanded={menuOpen}
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <rect x="0" y="0" width="6" height="6" fill="rgba(255,255,255,0.7)"/>
            <rect x="10" y="0" width="6" height="6" fill="rgba(255,255,255,0.7)"/>
            <rect x="0" y="10" width="6" height="6" fill="rgba(255,255,255,0.7)"/>
            <rect x="10" y="10" width="6" height="6" fill="rgba(255,255,255,0.7)"/>
          </svg>
        </button>
      </div>

      {/* Mobile menu dropdown */}
      {menuOpen && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            background: '#000',
            borderBottom: '1px solid rgba(255,255,255,0.15)',
            padding: '16px 28px',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
            animation: 'fade-in-up 0.2s ease',
          }}
          role="menu"
        >
          {navItems.map(item => (
            <button
              key={item.id}
              onClick={() => { navigate(item.path); setMenuOpen(false); }}
              role="menuitem"
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                color: 'rgba(255,255,255,0.65)',
                letterSpacing: '0.15em',
                textAlign: 'left',
                padding: '4px 0',
              }}
            >
              <span style={{ color: 'rgba(255,255,255,0.3)' }}>[{item.id}]</span>
              {' '}{item.label}
            </button>
          ))}
        </div>
      )}

      <style>{`
        @media (max-width: 900px) {
          .nav-links { display: none !important; }
        }
      `}</style>
    </nav>
  );
}
