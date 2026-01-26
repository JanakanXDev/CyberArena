import React from 'react';

interface ProgressBarProps {
  value: number;
  max: number;
  color?: 'red' | 'amber' | 'emerald' | 'blue' | 'purple' | 'slate';
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ value, max, color = 'slate' }) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  const colorClasses = {
    red: 'bg-red-500',
    amber: 'bg-amber-500',
    emerald: 'bg-emerald-500',
    blue: 'bg-blue-500',
    purple: 'bg-purple-500',
    slate: 'bg-slate-500'
  };

  return (
    <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
      <div
        className={`h-full transition-all duration-300 ${colorClasses[color]}`}
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
};
