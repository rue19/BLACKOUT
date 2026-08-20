interface RecoveryAction {
  action: string;
  description: string;
  claimsRestored: number;
  claimsCovered: string[];
}

interface Props {
  plan: RecoveryAction[];
}

const RecoveryPlanList = ({ plan }: Props) => {
  if (plan.length === 0) {
    return (
      <div className="text-center py-4">
        <p className="text-gray-400 text-sm">No recovery plan generated yet.</p>
        <p className="text-gray-500 text-xs mt-1">Run a simulation first, then click "Generate Recovery Plan"</p>
      </div>
    );
  }

  return (
    <div className="space-y-2 max-h-80 overflow-y-auto">
      {plan.map((action, i) => (
        <div key={i} className="bg-gray-700 rounded p-3 border-l-4 border-green-500">
          <div className="flex justify-between items-start mb-1">
            <span className="text-green-400 font-semibold text-sm">
              +{action.claimsRestored} claim{action.claimsRestored > 1 ? 's' : ''}
            </span>
            <span className="text-gray-400 text-xs">Priority #{i + 1}</span>
          </div>
          <div className="font-medium text-white text-sm mb-1">{action.action}</div>
          <div className="text-gray-300 text-xs">{action.description}</div>
          {action.claimsCovered && action.claimsCovered.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {action.claimsCovered.map((claimId, j) => (
                <span key={j} className="bg-gray-600 text-xs px-2 py-0.5 rounded">
                  {claimId}
                </span>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default RecoveryPlanList;
