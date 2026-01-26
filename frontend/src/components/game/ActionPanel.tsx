import React, { useState } from 'react';
import { Action, Hypothesis } from '../../types/game';
import { Crosshair, Lock, Brain } from 'lucide-react';

interface ActionPanelProps {
  actions: Action[];
  hypotheses: Hypothesis[];
  onAction: (actionId: string) => void;
}

export const ActionPanel: React.FC<ActionPanelProps> = ({
  actions,
  hypotheses,
  onAction
}) => {
  console.log('ActionPanel rendering with:', { actionsCount: actions.length, hypothesesCount: hypotheses.length });
  
  const [selectedHypothesis, setSelectedHypothesis] = useState<string | null>(null);

  const handleHypothesisSelect = (hypothesisId: string) => {
    console.log('Hypothesis selected:', hypothesisId);
    setSelectedHypothesis(hypothesisId);
    onAction(`hypothesis:${hypothesisId}`);
  };

  // Debug output
  console.log('ActionPanel render - Actions:', actions.map(a => ({ id: a.id, available: a.available })));
  console.log('ActionPanel render - Hypotheses:', hypotheses.map(h => ({ id: h.id, tested: h.tested, validated: h.validated })));

  return (
    <div className="h-full flex flex-col pt-8">
      {/* Debug indicator */}
      {actions.length === 0 && (
        <div className="px-6 py-2 bg-red-900/20 border border-red-500/30 text-red-400 text-xs">
          DEBUG: No actions received. Check console.
        </div>
      )}
      {actions.length > 0 && (
        <div className="px-6 py-2 bg-blue-900/20 border border-blue-500/30 text-blue-400 text-xs mb-2">
          DEBUG: {actions.length} action(s) available. {actions.filter(a => a.available).length} available, {actions.filter(a => !a.available).length} locked.
        </div>
      )}
      
      {/* Hypotheses Section */}
      {hypotheses.length > 0 && (
        <div className="px-6 pb-4 border-b border-slate-800">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2">
            <Brain className="w-3 h-3" />
            Form Hypotheses
          </div>
          <div className="space-y-2">
            {hypotheses.map((hyp) => (
              <button
                key={hyp.id}
                onClick={() => handleHypothesisSelect(hyp.id)}
                disabled={hyp.tested}
                className={`w-full text-left p-3 rounded border transition-all ${
                  hyp.tested
                    ? hyp.validated === true
                      ? 'bg-emerald-900/20 border-emerald-500/30 text-emerald-400'
                      : hyp.validated === false
                      ? 'bg-red-900/20 border-red-500/30 text-red-400'
                      : 'bg-slate-900/50 border-slate-800 text-slate-600'
                    : selectedHypothesis === hyp.id
                    ? 'bg-blue-900/20 border-blue-500/50 text-blue-400'
                    : 'bg-slate-900/50 border-slate-800 hover:border-slate-700 text-slate-300'
                }`}
              >
                <div className="text-xs font-bold mb-1">{hyp.label}</div>
                {hyp.description && (
                  <div className="text-[10px] text-slate-500">{hyp.description}</div>
                )}
                {hyp.tested && (
                  <div className="text-[10px] mt-1">
                    {hyp.validated === true ? '✓ Validated' : '✗ Invalidated'}
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Actions Section */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">
          Available Actions
        </div>
        <div className="space-y-3">
          {actions.length === 0 ? (
            <div className="text-slate-600 text-sm text-center py-8">
              No actions available. {hypotheses.length > 0 ? 'Form a hypothesis first.' : 'Loading actions...'}
            </div>
          ) : (
            actions.map((action) => {
              const isLocked = !action.available;
              const requiresHypothesis = hypotheses.some(
                (h) => !h.tested && action.id.includes(h.id.toLowerCase())
              );

              if (isLocked) {
                return (
                  <div
                    key={action.id}
                    className="w-full text-left border border-slate-800 bg-[#0f0f10] rounded-lg p-4 opacity-60 cursor-not-allowed"
                  >
                    <div className="flex items-center gap-2 mb-1 text-slate-500">
                      <Lock className="w-3 h-3" />
                      <span className="font-bold text-xs">Locked</span>
                    </div>
                    <div className="text-xs font-bold text-slate-400 mb-1">{action.label}</div>
                    <div className="text-[10px] text-slate-600">
                      {requiresHypothesis
                        ? 'Requires valid hypothesis'
                        : 'Action unavailable'}
                    </div>
                  </div>
                );
              }

              return (
                <button
                  key={action.id}
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('=== ACTION CLICKED ===');
                    console.log('Action ID:', action.id);
                    console.log('Action label:', action.label);
                    console.log('onAction function:', typeof onAction);
                    console.log('Calling onAction with:', action.id);
                    try {
                      onAction(action.id);
                      console.log('onAction called successfully');
                    } catch (error) {
                      console.error('Error calling onAction:', error);
                    }
                  }}
                  onMouseDown={(e) => {
                    console.log('Button mousedown:', action.id);
                  }}
                  className="w-full text-left border-2 border-slate-700 bg-[#1f1f22] hover:bg-[#252529] hover:border-emerald-500 rounded-lg p-4 transition-all group cursor-pointer relative z-10 active:scale-95"
                  style={{ pointerEvents: 'auto', WebkitTapHighlightColor: 'transparent' }}
                  aria-label={`Action: ${action.label}`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-bold text-sm text-slate-200 group-hover:text-emerald-400 transition-colors">
                      {action.label}
                    </span>
                    <Crosshair className="w-4 h-4 text-slate-600 group-hover:text-emerald-500 transition-colors" />
                  </div>
                  <p className="text-xs text-slate-400">{action.description}</p>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-[10px] text-slate-600 uppercase tracking-widest">
                      {action.type}
                    </span>
                    <span className="text-[10px] text-emerald-500">Click to execute</span>
                  </div>
                </button>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
