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

  const getNodeColor = useCallback((node: any) => {
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

  const nodeCanvasObject = useCallback((node: any, ctx: CanvasRenderingContext2D) => {
    const size = node.val || 4;
    const color = getNodeColor(node);

    if (isOrphaned(node)) {
      ctx.beginPath();
      ctx.arc(node.x, node.y, size + 4, 0, 2 * Math.PI);
      ctx.fillStyle = 'rgba(220, 38, 38, 0.2)';
      ctx.fill();
    }

    ctx.beginPath();
    ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();
  }, [getNodeColor, isOrphaned]);

  const linkColor = useCallback((link: any) => {
    if (!removedNodeId) return 'rgba(255,255,255,0.15)';
    const srcNode = typeof link.source === 'object' ? link.source : null;
    const tgtNode = typeof link.target === 'object' ? link.target : null;
    const srcId = srcNode ? (srcNode.id || srcNode.string_id) : link.source;
    const tgtId = tgtNode ? (tgtNode.id || tgtNode.string_id) : link.target;
    if (srcId === removedNodeId || tgtId === removedNodeId) return 'rgba(255,255,255,0.05)';
    return 'rgba(255,255,255,0.15)';
  }, [removedNodeId]);

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%', minHeight: '500px' }}>
      <ForceGraph2D
        graphData={graphData}
        nodeColor={getNodeColor}
        nodeVal={(node: any) => node.val || 4}
        nodeLabel={() => ''}
        linkLabel={() => ''}
        linkColor={linkColor}
        linkWidth={1}
        linkDirectionalParticles={2}
        linkDirectionalParticleWidth={1.5}
        linkDirectionalParticleColor={() => 'rgba(99,102,241,0.6)'}
        nodeCanvasObject={nodeCanvasObject}
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
