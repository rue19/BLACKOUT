import { useEffect, useState } from 'react';

interface Props {
  score: number;
}

const ResilienceGauge = ({ score }: Props) => {
  const [displayScore, setDisplayScore] = useState(score);

  useEffect(() => {
    setDisplayScore(score);
  }, [score]);

  const getColor = (s: number) => {
    if (s >= 70) return 'text-green-400';
    if (s >= 40) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="text-center">
      <div className={`text-6xl font-bold ${getColor(displayScore)}`}>
        {displayScore.toFixed(1)}
      </div>
      <div className="text-gray-400 mt-2">out of 100</div>
      <div className="mt-4 bg-gray-700 rounded-full h-4 overflow-hidden">
        <div
          className={`h-full transition-all duration-500 ${
            displayScore >= 70 ? 'bg-green-500' : displayScore >= 40 ? 'bg-yellow-500' : 'bg-red-500'
          }`}
          style={{ width: `${displayScore}%` }}
        />
      </div>
    </div>
  );
};

export default ResilienceGauge;
