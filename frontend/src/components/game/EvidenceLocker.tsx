import React from 'react';
import { Search } from 'lucide-react';
import { GameState } from '../../types/game';

interface EvidenceLockerProps {
  actionHistory: GameState['actionHistory'];
}

export const EvidenceLocker: React.FC<EvidenceLockerProps> = ({ actionHistory }) => {
  // Filter out failures, the fallback action, and duplicates so we just see unique valid evidence
  const uniqueEvidence = actionHistory
    .filter(a => !a.actually_failed && a.action_id !== 'tactical_fallback')
    .filter((a, index, self) => index === self.findIndex((t) => t.action_id === a.action_id))
    .reverse();

  if (uniqueEvidence.length === 0) return null;

  return (
    <div className="bg-[#0c0c0e] border border-slate-800 rounded-lg relative flex flex-col">
      <div className="absolute top-0 left-0 bg-blue-900/30 text-[10px] text-blue-400 font-bold px-3 py-1 uppercase tracking-wider z-10 border-r border-b border-blue-800/40 flex items-center gap-1.5 shadow-sm">
        <Search className="w-3 h-3" />
        Evidence Locker
      </div>
      <div className="pt-8 px-3 pb-3 flex gap-2 flex-wrap items-start">
        {uniqueEvidence.map((ev, idx) => (
          <div key={idx} className="bg-blue-950/40 border border-blue-700/50 rounded flex items-center gap-2 overflow-hidden shadow max-w-[220px]">
            <div className="bg-blue-900/60 px-2 py-1.5 h-full flex items-center justify-center border-r border-blue-800/50 text-[9px] font-bold text-blue-300">
              T{ev.turn}
            </div>
            <div className="px-2 py-1 text-xs font-medium text-blue-200 truncate pr-3" title={ev.action_label}>
              {ev.action_label}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
