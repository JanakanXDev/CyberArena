import React, { useState, useEffect } from 'react';
import { Action, Hypothesis } from '../../types/game';
import { Crosshair, Lock, Brain, Check } from 'lucide-react';
import { JargonText } from './JargonText';

interface ActionPanelProps {
  actions: Action[];
  hypotheses: Hypothesis[];
  actionHistory?: Array<{ action_id: string }>;
  onAction: (actionId: string) => void;
}

export const ActionPanel: React.FC<ActionPanelProps> = ({
  actions,
  hypotheses,
  actionHistory = [],
  onAction
}) => {
  const [selectedHypothesis, setSelectedHypothesis] = useState<string | null>(null);
  const [lockedHint, setLockedHint] = useState<string | null>(null);
  const [pulseHypotheses, setPulseHypotheses] = useState(false);
  const [lastActionCount, setLastActionCount] = useState(actionHistory.length);

  // Trigger brief pulse animation on hypotheses when an action completes
  useEffect(() => {
    if (actionHistory.length > lastActionCount) {
      setPulseHypotheses(true);
      const timer = setTimeout(() => setPulseHypotheses(false), 2000);
      setLastActionCount(actionHistory.length);
      return () => clearTimeout(timer);
    }
  }, [actionHistory.length, lastActionCount]);

  const showLockedFeedback = (actionId: string) => {
    // Try to find which hypothesis unlocks this action
    const relatedHyp = hypotheses.find(h => !h.tested && actionId.includes(h.id.toLowerCase()));
    const msg = relatedHyp
      ? `Test the “${relatedHyp.label}” hypothesis first to unlock this action.`
      : 'Validate the required hypothesis first to unlock this action.';
    setLockedHint(msg);
    setTimeout(() => setLockedHint(null), 2500);
  };

  const handleHypothesisSelect = (hypothesisId: string) => {
    setSelectedHypothesis(hypothesisId);
    onAction(`hypothesis:${hypothesisId}`);
  };

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Beginner Guide Tip */}
      {hypotheses.length > 0 && hypotheses.every(h => !h.tested) && (
        <div className="shrink-0 bg-yellow-900/20 border-b border-yellow-700/30 px-4 py-2 flex gap-2 items-start">
          <span className="text-yellow-500 text-lg leading-none mt-0.5">💡</span>
          <p className="text-[10px] text-yellow-300/80 leading-relaxed">
            <strong>Start here:</strong> Click a hypothesis below to test if your belief about the system is correct. Correct beliefs unlock actions.
          </p>
        </div>
      )}

      {/* Locked action hint toast */}
      {lockedHint && (
        <div className="shrink-0 bg-amber-900/30 border-b border-amber-700/40 px-4 py-2 flex gap-2 items-start animate-pulse">
          <span className="text-amber-500 text-sm leading-none mt-0.5">🔒</span>
          <p className="text-[10px] text-amber-300/90 leading-relaxed">{lockedHint}</p>
        </div>
      )}

      {/* Hypotheses Section - Always Visible at Top */}
      {hypotheses.length > 0 && (
        <div className="shrink-0 bg-gradient-to-r from-purple-900/30 to-blue-900/30 border-b-2 border-purple-500/50 px-6 py-4 overflow-y-auto" style={{ maxHeight: '45%' }}>
          <div className="flex items-center gap-2 mb-4">
            <Brain className="w-5 h-5 text-purple-400" />
            <span className="text-sm font-bold text-purple-400 uppercase tracking-widest">
              Form Hypotheses
            </span>
            <span className="text-xs text-slate-500 ml-auto">
              ({hypotheses.filter(h => !h.tested).length} untested)
            </span>
          </div>
          <div className="space-y-3">
            {hypotheses.map((hyp) => (
              <button
                key={hyp.id}
                onClick={() => handleHypothesisSelect(hyp.id)}
                disabled={hyp.tested}
                className={`w-full text-left p-4 rounded-lg border-2 transition-all ${hyp.tested
                  ? hyp.validated === true
                    ? 'bg-emerald-900/30 border-emerald-500/50 text-emerald-300 shadow-lg shadow-emerald-500/20'
                    : hyp.validated === false
                      ? 'bg-red-900/30 border-red-500/50 text-red-300 shadow-lg shadow-red-500/20'
                      : 'bg-slate-900/50 border-slate-800 text-slate-600'
                  : selectedHypothesis === hyp.id
                    ? 'bg-blue-900/30 border-blue-500/70 text-blue-300 shadow-lg shadow-blue-500/30'
                    : `bg-slate-900/70 border-slate-700 hover:border-purple-500/50 hover:bg-slate-800 text-slate-200 cursor-pointer transition-all duration-500 ${pulseHypotheses ? 'ring-2 ring-purple-500 ring-offset-2 ring-offset-[#0f0f10] shadow-[0_0_15px_rgba(168,85,247,0.4)]' : ''}`
                  }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <div className="text-sm font-bold mb-2">{hyp.label}</div>
                    {hyp.description && (
                      <div className="text-xs text-slate-400 leading-relaxed">
                        <JargonText text={hyp.description} maxHighlights={2} />
                      </div>
                    )}
                  </div>
                  {hyp.tested && (
                    <div className={`text-lg font-bold ${hyp.validated === true ? 'text-emerald-400' : 'text-red-400'}`}>
                      {hyp.validated === true ? '✓' : '✗'}
                    </div>
                  )}
                </div>
                {hyp.tested && (
                  <div className={`text-xs mt-2 font-bold ${hyp.validated === true ? 'text-emerald-400' : 'text-red-400'}`}>
                    {hyp.validated === true ? 'Validated' : 'Invalidated'}
                  </div>
                )}
                {!hyp.tested && (
                  <div className="text-xs mt-2 text-purple-400 font-bold">
                    Click to test this hypothesis
                  </div>
                )}

                {/* Post-validation explanation */}
                {hyp.tested && hyp.explanation && (
                  <div
                    className={`mt-3 p-3 rounded-lg border text-xs leading-relaxed ${hyp.validated === true
                      ? 'bg-emerald-950/60 border-emerald-700/40 text-emerald-200'
                      : 'bg-red-950/60 border-red-700/40 text-red-200'
                      }`}
                  >
                    <div className={`font-bold uppercase tracking-widest text-[9px] mb-1 ${hyp.validated === true ? 'text-emerald-400' : 'text-red-400'
                      }`}>
                      {hyp.validated === true ? '🧠 Why this was correct' : '🧠 Why this was wrong'}
                    </div>
                    <JargonText text={hyp.explanation} maxHighlights={2} />
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Actions Section - Scrollable */}
      <div className="flex-1 overflow-y-auto px-6 py-4 min-h-0">
        <div className="flex items-center gap-2 mb-4 sticky top-0 bg-[#161618] pb-2 z-10">
          <Crosshair className="w-4 h-4 text-emerald-400" />
          <span className="text-sm font-bold text-emerald-400 uppercase tracking-widest">
            Available Actions
          </span>
          <span className="text-xs text-slate-500 ml-auto">
            ({actions.filter(a => a.available).length} available)
          </span>
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

              const isCompleted = actionHistory.some(a => a.action_id === action.id);

              if (isLocked) {
                return (
                  <div
                    key={action.id}
                    onClick={() => showLockedFeedback(action.id)}
                    className="w-full text-left border border-slate-800 bg-[#0f0f10] rounded-lg p-4 opacity-60 cursor-pointer hover:opacity-80 hover:border-amber-800/50 transition-all"
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

              if (isCompleted) {
                return (
                  <div
                    key={action.id}
                    className="w-full text-left border border-emerald-900/40 bg-emerald-950/20 rounded-lg p-4 opacity-70 transition-all pointer-events-none"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-bold text-sm text-emerald-400">
                        {action.label}
                      </span>
                      <Check className="w-4 h-4 text-emerald-500" />
                    </div>
                    <p className="text-xs text-slate-400">
                      <JargonText text={action.description} maxHighlights={2} />
                    </p>
                    <div className="mt-2 flex items-center justify-end">
                      <span className="text-[10px] text-emerald-500 uppercase tracking-widest font-bold">
                        ✓ Completed
                      </span>
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
                    onAction(action.id);
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
                  <p className="text-xs text-slate-400">
                    <JargonText text={action.description} maxHighlights={2} />
                  </p>
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
