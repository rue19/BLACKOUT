import { useState, useEffect, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { getGraph } from '../api/client';

const GraphView = () => {
  const [graphData, setGraphData] = useState<any>({ nodes: [], links: [] });
  const fgRef = useRef<any>();

  useEffect(() => {
    getGraph().then(res => {
      const data = res.data;
      setGraphData({
        nodes: data.nodes.map((n: any) => ({ ...n, id: n.id })),
        links: data.edges.map((e: any) => ({ source: e.source, target: e.target, type: e.type })),
      });
    });
  }, []);

  const nodeColor = (node: any) => {
    switch (node.label) {
      case 'Person': return '#3b82f6';
      case 'Claim': return '#ef4444';
      case 'Decision': return '#10b981';
      case 'Message': return '#6366f1';
      case 'Document': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  return (
    <ForceGraph2D
      ref={fgRef}
      graphData={graphData}
      nodeColor={nodeColor}
      nodeLabel={(node: any) => `${node.label}: ${node.name || node.id}`}
      linkLabel={(link: any) => link.type}
      width={800}
      height={580}
      d3VelocityDecay={0.3}
    />
  );
};

export default GraphView;
