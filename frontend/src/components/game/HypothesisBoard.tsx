import React from 'react';
import { BookOpen, CheckCircle } from 'lucide-react';

interface Hypothesis {
  id: string;
  label: string;
}

interface HypothesisBoardProps {
  theories: Hypothesis[];
  onCommit: (id: string) => void;
  committedTheoryId: string | null;
}

export const HypothesisBoard: React.FC<HypothesisBoardProps> = ({ theories, onCommit, committedTheoryId }) => {
  if (!theories || theories.length === 0) return null;

  return (
    <div className="bg-[#111] border-l border-slate-800 p-6 flex flex-col h-full">
      <div className="flex items-center gap-2 mb-4 text-emerald-500">
        <BookOpen className="w-5 h-5" />
        <h3 className="font-bold uppercase tracking-widest text-xs">Investigator's Notebook</h3>
      </div>
      
      <p className="text-slate-500 text-xs mb-6 leading-relaxed">
        Select a working theory to unlock corresponding action paths.
      </p>

      <div className="space-y-3">
        {theories.map((theory) => {
          const isSelected = committedTheoryId === theory.id;
          return (
            <button
              key={theory.id}
              onClick={() => onCommit(theory.id)}
              // 🔥 REMOVED THE DISABLED PROP SO YOU CAN SWITCH
              className={`w-full text-left p-4 rounded border transition-all relative ${
                isSelected 
                  ? 'bg-emerald-900/20 border-emerald-500 text-white' 
                  : 'bg-[#1a1a1c] border-slate-700 text-slate-400 hover:border-slate-500 hover:text-slate-200'
              }`}
            >
              <div className="text-sm font-bold pr-6">{theory.label}</div>
              {isSelected && <CheckCircle className="absolute top-4 right-4 w-4 h-4 text-emerald-500" />}
            </button>
          );
        })}
      </div>
    </div>
  );
};