import { useState, useCallback, useEffect } from 'react';
import GraphView from '../GraphView';
import SimulateButton from '../SimulateButton';
import ResilienceGauge from '../ResilienceGauge';
import OrphanedClaimsPanel from '../OrphanedClaimsPanel';
import RecoveryPlanList from '../RecoveryPlanList';
import { simulate, recover, getResilience } from '../../api/client';
import Navbar from './Navbar';

export default function DashboardPage() {
  const [resilienceScore, setResilienceScore] = useState(100);
  const [orphanedClaims, setOrphanedClaims] = useState<any[]>([]);
  const [recoveryPlan, setRecoveryPlan] = useState<any[]>([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [lastTarget, setLastTarget] = useState<{ type: string; id: string } | null>(null);
  const [removedNodeId, setRemovedNodeId] = useState<string | null>(null);
  const [graphKey, setGraphKey] = useState(0);

  useEffect(() => {
    getResilience().then(res => setResilienceScore(res.data.score));
  }, []);

  const handleSimulate = useCallback(async (targetType: string, targetId: string) => {
    setIsSimulating(true);
    setRecoveryPlan([]);
    try {
      const result = await simulate({ targetType: targetType as any, targetId });
      setOrphanedClaims(result.data.orphanedClaims);
      setResilienceScore(result.data.resilienceScoreAfter);
      setLastTarget({ type: targetType, id: targetId });
      setRemovedNodeId(targetId);
      setGraphKey(k => k + 1);
    } finally {
      setIsSimulating(false);
    }
  }, []);

  const handleRecover = useCallback(async () => {
    if (!lastTarget) return;
    const result = await recover({ targetType: lastTarget.type as any, targetId: lastTarget.id });
    setRecoveryPlan(result.data.plan);
  }, [lastTarget]);

  const handleReset = useCallback(() => {
    setOrphanedClaims([]);
    setRecoveryPlan([]);
    setRemovedNodeId(null);
    setLastTarget(null);
    setGraphKey(k => k + 1);
    getResilience().then(res => setResilienceScore(res.data.score));
  }, []);

  const orphanedClaimIds = orphanedClaims.map(c => c.id);

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
              position: 'relative',
            }}>
              <GraphView key={graphKey} orphanedClaimIds={orphanedClaimIds} removedNodeId={removedNodeId} />
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
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h2 style={{ fontSize: '12px', letterSpacing: '0.15em', color: 'rgba(255,255,255,0.7)' }}>
                  SIMULATE REMOVAL
                </h2>
                {removedNodeId && (
                  <button
                    onClick={handleReset}
                    style={{
                      border: '1px solid rgba(255,255,255,0.2)',
                      background: 'transparent',
                      color: 'rgba(255,255,255,0.5)',
                      fontFamily: 'var(--font-mono)',
                      fontSize: '9px',
                      letterSpacing: '0.1em',
                      padding: '4px 8px',
                      cursor: 'pointer',
                    }}
                  >
                    RESET
                  </button>
                )}
              </div>
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
                disabled={!lastTarget}
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
                  opacity: lastTarget ? 1 : 0.4,
                }}
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
