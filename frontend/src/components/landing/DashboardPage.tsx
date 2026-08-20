import { useState, useCallback, useEffect } from 'react';
import GraphView from '../GraphView';
import SimulateButton from '../SimulateButton';
import ResilienceGauge from '../ResilienceGauge';
import OrphanedClaimsPanel from '../OrphanedClaimsPanel';
import RecoveryPlanList from '../RecoveryPlanList';
import { simulate, recover, getResilience } from '../../api/client';
import Navbar from './Navbar';

/**
 * DashboardPage — the existing BLACKOUT dashboard.
 * Wrapped in the new Navbar so navigation remains consistent.
 * All existing dashboard logic is preserved exactly as written.
 */
export default function DashboardPage() {
  const [resilienceScore, setResilienceScore] = useState(100);
  const [orphanedClaims, setOrphanedClaims] = useState<any[]>([]);
  const [recoveryPlan, setRecoveryPlan] = useState<any[]>([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [lastTarget, setLastTarget] = useState<{ type: string; id: string } | null>(null);

  useEffect(() => {
    getResilience().then(res => setResilienceScore(res.data.score));
  }, []);

  const handleSimulate = useCallback(async (targetType: string, targetId: string) => {
    setIsSimulating(true);
    try {
      const result = await simulate({ targetType: targetType as any, targetId });
      setOrphanedClaims(result.data.orphanedClaims);
      setResilienceScore(result.data.resilienceScoreAfter);
      setLastTarget({ type: targetType, id: targetId });
    } finally {
      setIsSimulating(false);
    }
  }, []);

  const handleRecover = useCallback(async () => {
    if (!lastTarget) return;
    const result = await recover({ targetType: lastTarget.type as any, targetId: lastTarget.id });
    setRecoveryPlan(result.data.plan);
  }, [lastTarget]);

  return (
    <div style={{ minHeight: '100vh', background: '#000', color: '#fff', fontFamily: 'var(--font-mono)' }}>
      <Navbar />
      <main style={{ paddingTop: '80px' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr 1fr',
          gridTemplateRows: 'auto auto',
          gap: '16px',
          padding: '16px',
          maxWidth: '1400px',
          margin: '0 auto',
        }}>
          {/* Graph view spans 2 columns, row 1 */}
          <div style={{ gridColumn: '1 / 3', gridRow: '1' }}>
            <div style={{
              border: '1px solid rgba(255,255,255,0.15)',
              padding: '16px',
              height: '600px',
            }}>
              <GraphView />
            </div>
          </div>

          {/* Video panel — bottom-left, spans 2 columns, row 2 */}
          <div style={{ gridColumn: '1 / 3', gridRow: '2' }}>
            <div style={{
              padding: '0',
            }}>
              <h2 style={{
                fontSize: '10px',
                letterSpacing: '0.2em',
                color: 'rgba(255,255,255,0.45)',
                marginBottom: '10px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}>
                <span style={{
                  width: '5px', height: '5px',
                  borderRadius: '50%',
                  background: 'rgba(255,255,255,0.6)',
                  display: 'inline-block',
                  animation: 'blink 2.5s ease-in-out infinite',
                }}/>
                SYSTEM RECORDING
              </h2>
              <video
                src="/demo.webm"
                autoPlay
                loop
                muted
                playsInline
                style={{
                  width: '100%',
                  display: 'block',
                  maxHeight: '340px',
                  objectFit: 'cover',
                  filter: 'brightness(0.92) contrast(1.05)',
                }}
                aria-label="BLACKOUT system demo recording"
              />
            </div>
          </div>

          {/* Right sidebar — spans both rows */}
          <div style={{ gridColumn: '3', gridRow: '1 / 3', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ border: '1px solid rgba(255,255,255,0.15)', padding: '16px' }}>
              <h2 style={{ fontSize: '12px', letterSpacing: '0.15em', marginBottom: '12px', color: 'rgba(255,255,255,0.7)' }}>
                KNOWLEDGE RESILIENCE
              </h2>
              <ResilienceGauge score={resilienceScore} />
            </div>

            <div style={{ border: '1px solid rgba(255,255,255,0.15)', padding: '16px' }}>
              <h2 style={{ fontSize: '12px', letterSpacing: '0.15em', marginBottom: '12px', color: 'rgba(255,255,255,0.7)' }}>
                SIMULATE REMOVAL
              </h2>
              <SimulateButton onSimulate={handleSimulate} disabled={isSimulating} />
            </div>

            <div style={{ border: '1px solid rgba(255,255,255,0.15)', padding: '16px' }}>
              <h2 style={{ fontSize: '12px', letterSpacing: '0.15em', marginBottom: '12px', color: 'rgba(255,255,255,0.7)' }}>
                ORPHANED CLAIMS
              </h2>
              <OrphanedClaimsPanel claims={orphanedClaims} />
            </div>

            <div style={{ border: '1px solid rgba(255,255,255,0.15)', padding: '16px' }}>
              <h2 style={{ fontSize: '12px', letterSpacing: '0.15em', marginBottom: '12px', color: 'rgba(255,255,255,0.7)' }}>
                RECOVERY PLAN
              </h2>
              <button
                onClick={handleRecover}
                style={{
                  width: '100%',
                  border: '1px solid rgba(255,255,255,0.3)',
                  background: 'transparent',
                  color: '#fff',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '11px',
                  letterSpacing: '0.15em',
                  padding: '10px',
                  cursor: 'pointer',
                  marginBottom: '12px',
                }}
                onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.05)')}
                onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
              >
                GENERATE RECOVERY PLAN
              </button>
              <RecoveryPlanList plan={recoveryPlan} />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
