import Navbar from './Navbar';
import HeroArtwork from './HeroArtwork';
import DecorativeGraph from './DecorativeGraph';
import CTAButton from './CTAButton';

/**
 * LandingPage — BLACKOUT hero / landing page.
 *
 * Composition (from the reference image):
 *   ┌────────────────────────────────────┐
 *   │  [NAVBAR]                          │
 *   │                                    │
 *   │    [decorative graph fragments]    │
 *   │                                    │
 *   │         [HAND ARTWORK]             │
 *   │       FIND WHAT                    │
 *   │       DISAPPEARS                   │
 *   │                                    │
 *   │    [decorative graph fragments]    │
 *   │                                    │
 *   │  SIMULATE          EXPLORE GRAPH   │
 *   └────────────────────────────────────┘
 *
 * All elements are layered absolutely within a full-viewport container.
 */
export default function LandingPage() {
  return (
    <div
      style={{
        position: 'relative',
        width: '100vw',
        height: '100vh',
        minHeight: '600px',
        background: '#000',
        overflow: 'hidden',
        fontFamily: 'var(--font-mono)',
      }}
      aria-label="BLACKOUT — Chaos Testing for Enterprise Knowledge"
    >
      {/* ── 1. Navigation bar (fixed overlay) ─────────────── */}
      <Navbar />

      {/* ── 2. Hand artwork (full-page background layer) ──── */}
      <HeroArtwork />

      {/* ── 3. Decorative graph SVG overlay ───────────────── */}
      <DecorativeGraph />

      {/* ── 4. Hero title is embedded in the hand artwork image ── */}

      {/* ── 5. Bottom CTA area ────────────────────────────── */}
      <div
        style={{
          position: 'absolute',
          bottom: '40px',
          left: 0,
          right: 0,
          display: 'flex',
          alignItems: 'flex-end',
          justifyContent: 'space-between',
          padding: '0 36px',
          zIndex: 20,
          pointerEvents: 'none',
        }}
      >
        {/* Left CTA: SIMULATE */}
        <div style={{ pointerEvents: 'all' }}>
          <CTAButton label="SIMULATE" path="/dashboard" position="left" />
        </div>

        {/* Right CTA: EXPLORE GRAPH */}
        <div style={{ pointerEvents: 'all' }}>
          <CTAButton label="EXPLORE GRAPH" path="/dashboard" position="right" />
        </div>
      </div>

      {/* ── 6. Top-left corner frame bracket ─────────────── */}
      <svg
        style={{ position: 'absolute', top: 0, left: 0, zIndex: 5, pointerEvents: 'none' }}
        width="50"
        height="50"
        viewBox="0 0 50 50"
        fill="none"
        aria-hidden="true"
      >
        <path d="M 2 2 L 2 22 M 2 2 L 22 2" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5"/>
      </svg>

      {/* ── 7. Top-right corner frame bracket ────────────── */}
      <svg
        style={{ position: 'absolute', top: 0, right: 0, zIndex: 5, pointerEvents: 'none' }}
        width="50"
        height="50"
        viewBox="0 0 50 50"
        fill="none"
        aria-hidden="true"
      >
        <path d="M 48 2 L 48 22 M 48 2 L 28 2" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5"/>
      </svg>

      {/* ── 8. Bottom-left corner frame bracket ──────────── */}
      <svg
        style={{ position: 'absolute', bottom: 0, left: 0, zIndex: 5, pointerEvents: 'none' }}
        width="50"
        height="50"
        viewBox="0 0 50 50"
        fill="none"
        aria-hidden="true"
      >
        <path d="M 2 48 L 2 28 M 2 48 L 22 48" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5"/>
      </svg>

      {/* ── 9. Bottom-right corner frame bracket ─────────── */}
      <svg
        style={{ position: 'absolute', bottom: 0, right: 0, zIndex: 5, pointerEvents: 'none' }}
        width="50"
        height="50"
        viewBox="0 0 50 50"
        fill="none"
        aria-hidden="true"
      >
        <path d="M 48 48 L 48 28 M 48 48 L 28 48" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5"/>
      </svg>

      {/* ── Mobile layout adjustments ─────────────────────── */}
      <style>{`
        /* On mobile, stack CTAs vertically centered at the bottom */
        @media (max-width: 600px) {
          /* Override bottom CTA flex to column */
          .cta-row {
            flex-direction: column !important;
            align-items: center !important;
            gap: 16px !important;
          }
        }
      `}</style>
    </div>
  );
}
