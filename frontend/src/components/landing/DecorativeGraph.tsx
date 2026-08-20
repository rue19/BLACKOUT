/**
 * DecorativeGraph — subtle SVG graph decoration elements surrounding the hand artwork.
 * Renders: corner brackets, tiny squares/circles (nodes), dotted lines, plus markers.
 * All elements are faint and purely atmospheric — they suggest a hidden knowledge graph.
 */
export default function DecorativeGraph() {
  return (
    <div
      aria-hidden="true"
      style={{
        position: 'absolute',
        inset: 0,
        pointerEvents: 'none',
        overflow: 'hidden',
      }}
    >
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 1440 860"
        preserveAspectRatio="xMidYMid slice"
        style={{ position: 'absolute', inset: 0 }}
      >
        {/* ── Corner brackets ─────────────────────────────── */}
        {/* Top-left corner */}
        <path d="M 30 30 L 30 70 M 30 30 L 70 30" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" fill="none"/>
        {/* Top-right corner */}
        <path d="M 1410 30 L 1410 70 M 1410 30 L 1370 30" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" fill="none"/>
        {/* Bottom-left corner */}
        <path d="M 30 830 L 30 790 M 30 830 L 70 830" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" fill="none"/>
        {/* Bottom-right corner */}
        <path d="M 1410 830 L 1410 790 M 1410 830 L 1370 830" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" fill="none"/>

        {/* ── Inner corner brackets (closer to center) ────── */}
        {/* Left inner */}
        <path d="M 480 370 L 480 405 M 480 370 L 515 370" stroke="rgba(255,255,255,0.25)" strokeWidth="1" fill="none"/>
        <path d="M 480 495 L 480 460 M 480 495 L 515 495" stroke="rgba(255,255,255,0.25)" strokeWidth="1" fill="none"/>
        {/* Right inner */}
        <path d="M 960 370 L 960 405 M 960 370 L 925 370" stroke="rgba(255,255,255,0.25)" strokeWidth="1" fill="none"/>
        <path d="M 960 495 L 960 460 M 960 495 L 925 495" stroke="rgba(255,255,255,0.25)" strokeWidth="1" fill="none"/>

        {/* ── Square nodes (graph vertices) ───────────────── */}
        {/* Left panel nodes */}
        <rect x="82" y="254" width="8" height="8" stroke="rgba(255,255,255,0.45)" strokeWidth="1" fill="rgba(0,0,0,0.8)"
          style={{ animation: 'blink 3.2s ease-in-out infinite' }}/>
        <rect x="120" y="338" width="8" height="8" stroke="rgba(255,255,255,0.35)" strokeWidth="1" fill="rgba(0,0,0,0.8)"
          style={{ animation: 'blink 4.1s ease-in-out infinite 0.8s' }}/>
        <rect x="140" y="418" width="8" height="8" stroke="rgba(255,255,255,0.35)" strokeWidth="1" fill="rgba(0,0,0,0.8)"
          style={{ animation: 'blink 3.7s ease-in-out infinite 1.6s' }}/>
        {/* Right panel nodes */}
        <rect x="1253" y="254" width="8" height="8" stroke="rgba(255,255,255,0.45)" strokeWidth="1" fill="rgba(0,0,0,0.8)"
          style={{ animation: 'blink 3.2s ease-in-out infinite 0.5s' }}/>
        <rect x="1213" y="338" width="8" height="8" stroke="rgba(255,255,255,0.35)" strokeWidth="1" fill="rgba(0,0,0,0.8)"
          style={{ animation: 'blink 4.1s ease-in-out infinite 1.2s' }}/>
        <rect x="1193" y="418" width="8" height="8" stroke="rgba(255,255,255,0.35)" strokeWidth="1" fill="rgba(0,0,0,0.8)"
          style={{ animation: 'blink 3.7s ease-in-out infinite 2s' }}/>

        {/* ── Small circles ───────────────────────────────── */}
        <circle cx="200" cy="626" r="5" stroke="rgba(255,255,255,0.3)" strokeWidth="1" fill="none"
          style={{ animation: 'pulse-opacity 4s ease-in-out infinite' }}/>
        <circle cx="1238" cy="626" r="5" stroke="rgba(255,255,255,0.3)" strokeWidth="1" fill="none"
          style={{ animation: 'pulse-opacity 4s ease-in-out infinite 2s' }}/>
        <circle cx="720" cy="490" r="3" stroke="rgba(255,255,255,0.4)" strokeWidth="1" fill="rgba(255,255,255,0.1)"
          style={{ animation: 'blink 2.8s ease-in-out infinite' }}/>

        {/* ── Plus / cross markers ────────────────────────── */}
        {/* Scattered + signs */}
        {[
          [212, 218], [420, 400], [930, 400], [1175, 218],
          [260, 462], [1080, 462], [388, 488], [1050, 488],
        ].map(([cx, cy], i) => (
          <g key={i} transform={`translate(${cx}, ${cy})`}
            style={{ animation: `pulse-opacity ${3 + (i * 0.4)}s ease-in-out infinite ${i * 0.3}s` }}>
            <line x1="-5" y1="0" x2="5" y2="0" stroke="rgba(255,255,255,0.35)" strokeWidth="1"/>
            <line x1="0" y1="-5" x2="0" y2="5" stroke="rgba(255,255,255,0.35)" strokeWidth="1"/>
          </g>
        ))}

        {/* ── Dotted connector lines (graph edges) ────────── */}
        {/* Left vertical dotted */}
        <line x1="86" y1="262" x2="124" y2="346" stroke="rgba(255,255,255,0.15)" strokeWidth="1"
          strokeDasharray="2 4"/>
        <line x1="124" y1="346" x2="144" y2="426" stroke="rgba(255,255,255,0.15)" strokeWidth="1"
          strokeDasharray="2 4"/>
        {/* Left to corner bracket */}
        <line x1="148" y1="422" x2="204" y2="510" stroke="rgba(255,255,255,0.1)" strokeWidth="1"
          strokeDasharray="1 5"/>
        <line x1="204" y1="622" x2="204" y2="510" stroke="rgba(255,255,255,0.1)" strokeWidth="1"
          strokeDasharray="1 5"/>

        {/* Right vertical dotted */}
        <line x1="1257" y1="262" x2="1217" y2="346" stroke="rgba(255,255,255,0.15)" strokeWidth="1"
          strokeDasharray="2 4"/>
        <line x1="1217" y1="346" x2="1197" y2="426" stroke="rgba(255,255,255,0.15)" strokeWidth="1"
          strokeDasharray="2 4"/>
        <line x1="1193" y1="422" x2="1237" y2="510" stroke="rgba(255,255,255,0.1)" strokeWidth="1"
          strokeDasharray="1 5"/>
        <line x1="1237" y1="622" x2="1237" y2="510" stroke="rgba(255,255,255,0.1)" strokeWidth="1"
          strokeDasharray="1 5"/>

        {/* ── Short horizontal rule below hero text ────────── */}
        <line x1="680" y1="495" x2="760" y2="495" stroke="rgba(255,255,255,0.3)" strokeWidth="1"/>

        {/* ── Tiny dot grid fragments ──────────────────────── */}
        {/* Left dot cluster */}
        {[0,1,2].map(col => [0,1,2].map(row => (
          <rect
            key={`ld-${col}-${row}`}
            x={278 + col * 8}
            y={325 + row * 8}
            width="2"
            height="2"
            fill="rgba(255,255,255,0.2)"
            style={{ animation: `pulse-opacity ${3.5 + row * 0.5}s ease-in-out infinite ${col * 0.2}s` }}
          />
        )))}
        {/* Right dot cluster */}
        {[0,1,2].map(col => [0,1,2].map(row => (
          <rect
            key={`rd-${col}-${row}`}
            x={1145 + col * 8}
            y={325 + row * 8}
            width="2"
            height="2"
            fill="rgba(255,255,255,0.2)"
            style={{ animation: `pulse-opacity ${3.5 + row * 0.5}s ease-in-out infinite ${col * 0.2 + 1}s` }}
          />
        )))}

        {/* ── Small downward arrow / chevron at very bottom center ── */}
        <path d="M 716 800 L 724 812 L 732 800" stroke="rgba(255,255,255,0.25)" strokeWidth="1" fill="none"
          style={{ animation: 'fade-in-up 3s ease-in-out infinite alternate' }}/>
      </svg>
    </div>
  );
}
