/**
 * Environment toggle component - allows Knowledge Stewards to switch between stage and production.
 */
import { useAuthStore } from '@/stores/authStore';

interface EnvironmentToggleProps {
  value: 'stage' | 'production';
  onChange: (env: 'stage' | 'production') => void;
}

export function EnvironmentToggle({ value, onChange }: EnvironmentToggleProps) {
  const user = useAuthStore((state) => state.user);

  // Only show for KNOWLEDGE_STEWARD or ADMIN
  const hasAccess = user?.roles.some((role) =>
    ['KNOWLEDGE_STEWARD', 'ADMIN'].includes(role)
  );

  if (!hasAccess) {
    return null;
  }

  return (
    <div className="flex items-center space-x-2 px-3 py-2 bg-gray-100 rounded-lg">
      <span className="text-sm text-gray-600 font-medium">Environment:</span>
      <div className="flex bg-white rounded-md shadow-sm border border-gray-300">
        <button
          onClick={() => onChange('production')}
          className={`px-3 py-1 text-sm font-medium rounded-l-md transition-colors ${
            value === 'production'
              ? 'bg-green-600 text-white'
              : 'text-gray-700 hover:bg-gray-50'
          }`}
        >
          Production
        </button>
        <button
          onClick={() => onChange('stage')}
          className={`px-3 py-1 text-sm font-medium rounded-r-md border-l border-gray-300 transition-colors ${
            value === 'stage'
              ? 'bg-yellow-600 text-white'
              : 'text-gray-700 hover:bg-gray-50'
          }`}
        >
          Stage
        </button>
      </div>
    </div>
  );
}
