import { useState } from 'react';

interface Props {
  onSimulate: (targetType: string, targetId: string) => void;
  disabled: boolean;
}

const PEOPLE = [
  { id: 'sam@acme.com', label: 'Sam (Payments Lead)' },
  { id: 'priya@acme.com', label: 'Priya (Product Manager)' },
  { id: 'alex@acme.com', label: 'Alex (Architect)' },
  { id: 'jordan@acme.com', label: 'Jordan (DevOps)' },
];

const SimulateButton = ({ onSimulate, disabled }: Props) => {
  const [customId, setCustomId] = useState('');
  const [mode, setMode] = useState<'quick' | 'custom'>('quick');

  const handleQuickSelect = (id: string) => {
    onSimulate('person', id);
  };

  const handleCustomSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (customId) {
      onSimulate('person', customId);
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex gap-2 mb-2">
        <button
          onClick={() => setMode('quick')}
          className={`flex-1 py-1 text-sm rounded ${mode === 'quick' ? 'bg-red-600' : 'bg-gray-700'}`}
        >
          Quick Select
        </button>
        <button
          onClick={() => setMode('custom')}
          className={`flex-1 py-1 text-sm rounded ${mode === 'custom' ? 'bg-red-600' : 'bg-gray-700'}`}
        >
          Custom
        </button>
      </div>

      {mode === 'quick' ? (
        <div className="space-y-2">
          {PEOPLE.map(person => (
            <button
              key={person.id}
              onClick={() => handleQuickSelect(person.id)}
              disabled={disabled}
              className="w-full text-left bg-gray-700 hover:bg-red-600 disabled:bg-gray-600 text-white py-2 px-3 rounded text-sm transition-colors"
            >
              {person.label}
            </button>
          ))}
        </div>
      ) : (
        <form onSubmit={handleCustomSubmit} className="space-y-2">
          <input
            type="text"
            value={customId}
            onChange={(e) => setCustomId(e.target.value)}
            placeholder="Enter email or ID..."
            className="w-full bg-gray-700 text-white rounded px-3 py-2"
          />
          <button
            type="submit"
            disabled={disabled || !customId}
            className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white font-bold py-2 px-4 rounded"
          >
            {disabled ? 'Simulating...' : 'Simulate Removal'}
          </button>
        </form>
      )}
    </div>
  );
};

export default SimulateButton;
