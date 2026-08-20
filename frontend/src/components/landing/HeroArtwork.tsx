import { useEffect, useRef } from 'react';

/**
 * HeroArtwork — the central dithered hand composition.
 * The image is rendered as a full-bleed background layer with a subtle floating animation.
 * mix-blend-mode: screen ensures the black areas are transparent on the black page background,
 * making the hands feel like they dissolve into the void.
 */
export default function HeroArtwork() {
  const imgRef = useRef<HTMLImageElement>(null);

  // Subtle "particle flicker" via random opacity nudges on animation frames
  useEffect(() => {
    let frame: number;
    let t = 0;

    const tick = () => {
      t += 0.008;
      if (imgRef.current) {
        // Very subtle brightness oscillation — simulates pixel flicker
        const brightness = 0.90 + Math.sin(t) * 0.06 + Math.sin(t * 2.3) * 0.02;
        imgRef.current.style.filter = `brightness(${brightness}) contrast(1.05)`;
      }
      frame = requestAnimationFrame(tick);
    };

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, []);

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        pointerEvents: 'none',
      }}
      aria-hidden="true"
    >
      <img
        ref={imgRef}
        src="/hand-artwork.png"
        alt="Dithered hands emerging from darkness — BLACKOUT visual identity"
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          objectPosition: 'center center',
          animation: 'float 7s ease-in-out infinite',
          mixBlendMode: 'screen',
          opacity: 0.95,
          userSelect: 'none',
          WebkitUserDrag: 'none',
        } as React.CSSProperties}
        draggable={false}
      />
    </div>
  );
}
