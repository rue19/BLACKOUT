import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface CTAButtonProps {
  label: string;
  path: string;
  position: 'left' | 'right';
}

/**
 * CTAButton — minimalist outlined button with thin-line technical style.
 * Matches the reference image's SIMULATE and EXPLORE GRAPH buttons.
 * On hover: border expands and arrow shifts outward.
 */
export default function CTAButton({ label, path, position }: CTAButtonProps) {
  const navigate = useNavigate();
  const [hovered, setHovered] = useState(false);

  const isLeft = position === 'left';

  return (
    <button
      onClick={() => navigate(path)}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        background: 'transparent',
        border: 'none',
        cursor: 'pointer',
        fontFamily: 'var(--font-mono)',
        padding: 0,
        animation: 'fade-in-up 0.6s ease both',
        animationDelay: isLeft ? '1.5s' : '1.8s',
        opacity: 0,
      }}
      aria-label={label}
    >
      {/* Outer bracket corners */}
      <div
        style={{
          position: 'absolute',
          inset: '-6px -8px',
          pointerEvents: 'none',
        }}
      >
        {/* TL */}
        <span style={{
          position: 'absolute', top: 0, left: 0,
          width: '10px', height: '10px',
          borderTop: `1px solid rgba(255,255,255,${hovered ? 0.7 : 0.4})`,
          borderLeft: `1px solid rgba(255,255,255,${hovered ? 0.7 : 0.4})`,
          transition: 'border-color 0.2s',
        }}/>
        {/* TR */}
        <span style={{
          position: 'absolute', top: 0, right: 0,
          width: '10px', height: '10px',
          borderTop: `1px solid rgba(255,255,255,${hovered ? 0.7 : 0.4})`,
          borderRight: `1px solid rgba(255,255,255,${hovered ? 0.7 : 0.4})`,
          transition: 'border-color 0.2s',
        }}/>
        {/* BL */}
        <span style={{
          position: 'absolute', bottom: 0, left: 0,
          width: '10px', height: '10px',
          borderBottom: `1px solid rgba(255,255,255,${hovered ? 0.7 : 0.4})`,
          borderLeft: `1px solid rgba(255,255,255,${hovered ? 0.7 : 0.4})`,
          transition: 'border-color 0.2s',
        }}/>
        {/* BR */}
        <span style={{
          position: 'absolute', bottom: 0, right: 0,
          width: '10px', height: '10px',
          borderBottom: `1px solid rgba(255,255,255,${hovered ? 0.7 : 0.4})`,
          borderRight: `1px solid rgba(255,255,255,${hovered ? 0.7 : 0.4})`,
          transition: 'border-color 0.2s',
        }}/>
      </div>

      {/* Inner content */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          padding: '10px 18px',
          border: `1px solid rgba(255,255,255,${hovered ? 0.35 : 0.2})`,
          transition: 'border-color 0.2s, background 0.2s',
          background: hovered ? 'rgba(255,255,255,0.04)' : 'transparent',
        }}
      >
        {/* Chevron prefix */}
        <span style={{
          fontSize: '11px',
          color: hovered ? '#fff' : 'rgba(255,255,255,0.5)',
          transition: 'color 0.2s',
        }}>›</span>

        <span style={{
          fontSize: '11px',
          fontWeight: 700,
          color: hovered ? '#fff' : 'rgba(255,255,255,0.75)',
          letterSpacing: '0.2em',
          transition: 'color 0.2s',
        }}>
          {label}
        </span>

        {/* Arrow icon */}
        <svg
          width="14"
          height="14"
          viewBox="0 0 14 14"
          fill="none"
          aria-hidden="true"
          style={{
            transform: hovered ? 'translate(3px, -3px)' : 'translate(0, 0)',
            transition: 'transform 0.2s ease',
          }}
        >
          <line x1="2" y1="12" x2="12" y2="2" stroke={hovered ? '#fff' : 'rgba(255,255,255,0.6)'} strokeWidth="1.5"/>
          <polyline points="7,2 12,2 12,7" stroke={hovered ? '#fff' : 'rgba(255,255,255,0.6)'} strokeWidth="1.5" fill="none"/>
        </svg>

        {/* Right side: grid dots (only on right CTA) */}
        {!isLeft && (
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
            {[0,1,2].map(r => [0,1,2].map(c => (
              <rect key={`${r}-${c}`} x={c*5} y={r*5} width="2" height="2"
                fill={hovered ? 'rgba(255,255,255,0.8)' : 'rgba(255,255,255,0.4)'}
                style={{ transition: 'fill 0.2s' }}
              />
            )))}
          </svg>
        )}
      </div>
    </button>
  );
}
