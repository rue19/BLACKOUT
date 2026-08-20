import { useState, useEffect, useRef, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { getGraph } from '../api/client';

interface Props {
  orphanedClaimIds?: string[];
  removedNodeId?: string | null;
}

const GraphView = ({ orphanedClaimIds = [], removedNodeId = null }: Props) => {
  const [graphData, setGraphData] = useState<any>({ nodes: [], links: [] });
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 580 });
  const fgRef = useRef<any>();

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setDimensions({ width: rect.width, height: rect.height });
      }
    };
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  useEffect(() => {
    getGraph().then(res => {
      const data = res.data;
      setGraphData({
        nodes: data.nodes.map((n: any) => ({
          ...n,
          id: n.id,
          val: n.label === 'Person' ? 8 : n.label === 'Decision' ? 6 : n.label === 'Claim' ? 4 : 3,
        })),
        links: data.edges.map((e: any) => ({ source: e.source, target: e.target, type: e.type })),
      });
    });
  }, []);

  const isOrphaned = useCallback((node: any) => {
    if (node.label !== 'Claim') return false;
    return orphanedClaimIds.includes(node.id) || orphanedClaimIds.includes(node.string_id);
  }, [orphanedClaimIds]);

  const isRemoved = useCallback((node: any) => {
    if (removedNodeId === null) return false;
    return node.id === removedNodeId || node.string_id === removedNodeId;
  }, [removedNodeId]);

  const nodeColor = useCallback((node: any) => {
    if (isRemoved(node)) return '#4b5563';
    if (isOrphaned(node)) return '#dc2626';
    switch (node.label) {
      case 'Person': return '#3b82f6';
      case 'Claim': return '#ef4444';
      case 'Decision': return '#10b981';
      case 'Message': return '#818cf8';
      case 'Document': return '#f59e0b';
      default: return '#6b7280';
    }
  }, [isRemoved, isOrphaned]);

  const prevOrphanedRef = useRef<string[]>([]);

  useEffect(() => {
    const fg = fgRef.current;
    if (!fg) return;

    const changed =
      prevOrphanedRef.current.length !== orphanedClaimIds.length ||
      prevOrphanedRef.current.some((id, i) => id !== orphanedClaimIds[i]) ||
      (prevOrphanedRef.current.length === 0 && orphanedClaimIds.length > 0);
    prevOrphanedRef.current = orphanedClaimIds;

    if (changed && graphData.nodes.length > 0) {
      if (removedNodeId) {
        const node = graphData.nodes.find((n: any) => n.id === removedNodeId || n.string_id === removedNodeId);
        if (node) {
          node.fx = null;
          node.fy = null;
          node.vx = (Math.random() - 0.5) * 20;
          node.vy = (Math.random() - 0.5) * 20;
        }
      }
      graphData.nodes.forEach((n: any) => {
        if (orphanedClaimIds.includes(n.id) || orphanedClaimIds.includes(n.string_id)) {
          n.vx = (Math.random() - 0.5) * 15;
          n.vy = (Math.random() - 0.5) * 15;
        }
      });
      fg.d3ReheatSimulation();
    }

    if (!removedNodeId && orphanedClaimIds.length === 0 && graphData.nodes.length > 0) {
      fg.d3ReheatSimulation();
    }
  }, [orphanedClaimIds, removedNodeId, graphData]);

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%', minHeight: '500px' }}>
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        nodeColor={nodeColor}
        nodeVal={(node: any) => node.val || 4}
        nodeLabel={(node: any) => {
          const name = node.name || node.string_id || node.id;
          return `<div style="background:rgba(0,0,0,0.9);color:#fff;padding:6px 10px;border-radius:4px;font-family:monospace;font-size:11px;border:1px solid rgba(255,255,255,0.2);max-width:250px;">
            <div style="color:${nodeColor(node)};font-weight:bold;margin-bottom:2px;">${node.label}</div>
            <div>${name}</div>
            ${node.text_summary ? `<div style="color:#9ca3af;font-size:10px;margin-top:4px;">${node.text_summary.slice(0, 100)}...</div>` : ''}
          </div>`;
        }}
        linkLabel={(link: any) => `<div style="background:rgba(0,0,0,0.9);color:#818cf8;padding:4px 8px;border-radius:3px;font-family:monospace;font-size:10px;">${link.type}</div>`}
        linkColor={() => 'rgba(255,255,255,0.12)'}
        linkWidth={1}
        linkDirectionalParticles={2}
        linkDirectionalParticleWidth={1.5}
        linkDirectionalParticleColor={() => 'rgba(99,102,241,0.6)'}
        nodePointerAreaPaint={(node: any, color: string, ctx: CanvasRenderingContext2D) => {
          const size = (node.val || 4) + 4;
          ctx.beginPath();
          ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
          ctx.fillStyle = color;
          ctx.fill();
        }}
        width={dimensions.width}
        height={dimensions.height}
        d3VelocityDecay={0.3}
        d3AlphaDecay={0.02}
        warmupTicks={50}
        cooldownTicks={100}
        backgroundColor="#000000"
      />
    </div>
  );
};

export default GraphView;
