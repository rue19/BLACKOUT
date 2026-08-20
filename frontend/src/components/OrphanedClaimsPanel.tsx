interface Claim {
  id: string;
  text_summary: string;
}

interface Props {
  claims: Claim[];
}

const OrphanedClaimsPanel = ({ claims }: Props) => {
  if (claims.length === 0) {
    return (
      <div className="text-center py-4">
        <p className="text-gray-400 text-sm">No orphaned claims detected.</p>
        <p className="text-gray-500 text-xs mt-1">Run a simulation to see blast radius</p>
      </div>
    );
  }

  return (
    <div className="space-y-2 max-h-64 overflow-y-auto">
      {claims.map((claim) => (
        <div key={claim.id} className="bg-gray-700 rounded p-3 border-l-4 border-red-500">
          <div className="flex justify-between items-start mb-1">
            <span className="text-red-400 text-xs font-mono">{claim.id}</span>
            <span className="bg-red-600 text-white text-xs px-2 py-0.5 rounded">ORPHANED</span>
          </div>
          <div className="text-gray-200 text-sm">{claim.text_summary?.slice(0, 120)}...</div>
        </div>
      ))}
    </div>
  );
};

export default OrphanedClaimsPanel;
