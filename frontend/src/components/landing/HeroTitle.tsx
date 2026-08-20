import { useEffect, useState } from 'react';

const LINE_1 = 'FIND WHAT';
const LINE_2 = 'DISAPPEARS';

/**
 * HeroTitle — character-reveal text that floats over the hand artwork.
 * Uses a two-pass reveal: first line fades letter by letter, then second line.
 * The text sits at the visual center of the hand composition.
 */
export default function HeroTitle() {
  const [revealed1, setRevealed1] = useState(0);
  const [revealed2, setRevealed2] = useState(0);

  useEffect(() => {
    // Reveal line 1
    let i = 0;
    const t1 = setInterval(() => {
      i++;
      setRevealed1(i);
      if (i >= LINE_1.length) {
        clearInterval(t1);
        // Start revealing line 2 with a delay
        let j = 0;
        const t2 = setInterval(() => {
          j++;
          setRevealed2(j);
          if (j >= LINE_2.length) clearInterval(t2);
        }, 60);
      }
    }, 60);

    return () => clearInterval(t1);
  }, []);

  const textStyle: React.CSSProperties = {
    fontFamily: 'var(--font-mono)',
    fontSize: 'clamp(32px, 5vw, 72px)',
    fontWeight: 700,
    color: '#fff',
    letterSpacing: '0.15em',
    lineHeight: 1.25,
    display: 'block',
    textAlign: 'center',
    textTransform: 'uppercase',
    whiteSpace: 'nowrap',
  };

  const charStyle = (visible: boolean): React.CSSProperties => ({
    opacity: visible ? 1 : 0,
    transition: 'opacity 0.15s ease',
    display: 'inline-block',
  });

  return (
    <div
      style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -35%)',
        zIndex: 10,
        textAlign: 'center',
        pointerEvents: 'none',
        userSelect: 'none',
      }}
      aria-label="Find What Disappears"
      role="heading"
      aria-level={1}
    >
      {/* Very subtle local contrast treatment — thin radial shadow, not a solid rectangle */}
      <div
        style={{
          padding: '12px 24px 8px',
          background: 'radial-gradient(ellipse 80% 100% at 50% 50%, rgba(0,0,0,0.55) 0%, transparent 100%)',
        }}
      >
        <span style={textStyle} aria-hidden="true">
          {LINE_1.split('').map((ch, i) => (
            <span key={i} style={charStyle(i < revealed1)}>
              {ch === ' ' ? '\u00A0' : ch}
            </span>
          ))}
        </span>
        <span style={textStyle} aria-hidden="true">
          {LINE_2.split('').map((ch, i) => (
            <span key={i} style={charStyle(i < revealed2)}>
              {ch === ' ' ? '\u00A0' : ch}
            </span>
          ))}
        </span>
      </div>
    </div>
  );
}
