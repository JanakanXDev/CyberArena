import React, { useState, useEffect } from 'react';
import { Action, ExperienceMode, Hypothesis } from '../../types/game';
import { Crosshair, Lock, Brain, Check, ChevronDown, Zap, Search, Eye, Shield } from 'lucide-react';
import { JargonText } from './JargonText';

interface ActionPanelProps {
  actions: Action[];
  hypotheses: Hypothesis[];
  actionHistory?: Array<{ action_id: string }>;
  experienceMode?: ExperienceMode;
  onAction: (actionId: string) => void;
  isProcessing?: boolean;
}

export const ActionPanel: React.FC<ActionPanelProps> = ({
  actions,
  hypotheses,
  actionHistory = [],
  experienceMode = 'advanced',
  onAction,
  isProcessing
}) => {
  const [nlpInput, setNlpInput] = useState('');
  const [lockedHint, setLockedHint] = useState<string | null>(null);
  const [pulseHypotheses, setPulseHypotheses] = useState(false);
  const [lastActionCount, setLastActionCount] = useState(actionHistory.length);
  const [showHypothesisBuilder, setShowHypothesisBuilder] = useState(true);

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

  const completedActions = actionHistory.length;

  const handleNlpSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!nlpInput.trim()) return;
    onAction(`hypothesis_text:${nlpInput.trim()}`);
    setNlpInput('');
  };

  const beginnerSuggestions = [
    'Input validation is active',
    'Timing behavior is inconsistent',
    'Requests are being rate limited',
    'Authentication retries are being restricted'
  ];

  const iconForActionType = (type: string) => {
    const t = (type || '').toLowerCase();
    if (t.includes('probe') || t.includes('inspect')) return Search;
    if (t.includes('monitor')) return Eye;
    if (t.includes('isolate') || t.includes('restrict')) return Shield;
    return Zap;
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Beginner Guide Tip */}
      {completedActions === 0 && (
        <div className="shrink-0 bg-yellow-900/20 border-b border-yellow-700/30 px-4 py-2 flex gap-2 items-start">
          <span className="text-yellow-500 text-lg leading-none mt-0.5">💡</span>
          <p className="text-[10px] text-yellow-300/80 leading-relaxed">
            <strong>Start here:</strong> First, execute an action below to gather evidence. Then, write a theory about what is happening in the system!
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

      {/* Actions Section - PRIMARY INTERACTION */}
      <div className="px-4 py-4 border border-emerald-900/40 rounded-lg bg-gradient-to-r from-emerald-950/25 to-transparent">
        <div className="flex items-center gap-2 mb-3">
          <Crosshair className="w-4 h-4 text-emerald-400" />
          <span className="text-sm font-bold text-emerald-400 uppercase tracking-widest">
            Available Actions
          </span>
          <span className="text-xs text-emerald-200/70 ml-auto">
            ({actions.filter(a => a.available).length} available)
          </span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 2xl:grid-cols-3 gap-3">
          {actions.length === 0 ? (
            <div className="col-span-full text-slate-600 text-sm text-center py-6">
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
                    className="w-full text-left border border-slate-800 bg-[#0f0f10] rounded-lg p-3 opacity-60 cursor-pointer hover:opacity-80 hover:border-amber-800/50 transition-all"
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
                    className="w-full text-left border border-emerald-900/40 bg-emerald-950/20 rounded-lg p-3 opacity-75 transition-all pointer-events-none"
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
                  disabled={isProcessing}
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    if (!isProcessing) {
                      onAction(action.id);
                    }
                  }}
                  className={`w-full text-left border-2 border-emerald-700/70 bg-[#1f1f22] rounded-lg p-3 transition-all group relative z-10 shadow-[0_0_0_1px_rgba(16,185,129,0.15)] ${
                    isProcessing 
                      ? 'opacity-50 cursor-not-allowed' 
                      : 'hover:bg-[#252529] hover:border-emerald-400 hover:shadow-[0_0_16px_rgba(16,185,129,0.22)] cursor-pointer active:scale-95'
                  }`}
                  style={{ pointerEvents: 'auto', WebkitTapHighlightColor: 'transparent' }}
                  aria-label={`Action: ${action.label}`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-bold text-sm text-slate-200 group-hover:text-emerald-400 transition-colors">
                      {action.label}
                    </span>
                    {React.createElement(iconForActionType(action.type), {
                      className: "w-4 h-4 text-slate-500 group-hover:text-emerald-400 transition-colors"
                    })}
                  </div>
                  <p className="text-xs text-slate-400">
                    <JargonText text={action.description} maxHighlights={2} />
                  </p>
                  <div className="mt-2 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-slate-600 uppercase tracking-widest bg-slate-800/50 px-1.5 py-0.5 rounded">
                        {action.type}
                      </span>
                      {action.time_cost && action.time_cost > 1 && (
                        <span className="text-[10px] text-amber-500/80 font-bold uppercase tracking-widest bg-amber-900/20 border border-amber-900/50 px-1.5 py-0.5 rounded flex items-center gap-1">
                          ⏰ {action.time_cost} AP
                        </span>
                      )}
                    </div>
                    <span className="text-[10px] text-emerald-500/80 font-medium group-hover:text-emerald-400">Execute →</span>
                  </div>
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* Hypothesis Builder - SECONDARY / COLLAPSIBLE */}
      <div className="border border-slate-800/80 rounded-lg overflow-hidden">
        <button
          type="button"
          onClick={() => setShowHypothesisBuilder(v => !v)}
          className="w-full px-4 py-2.5 flex items-center justify-between bg-slate-900/65 border-b border-slate-800 hover:bg-slate-800/70 transition-colors"
        >
          <div className="flex items-center gap-2">
            <Brain className="w-4 h-4 text-purple-400" />
            <span className="text-xs font-bold text-purple-300 uppercase tracking-widest">
              Guided Hypothesis Builder
            </span>
          </div>
          <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${showHypothesisBuilder ? 'rotate-180' : ''}`} />
        </button>

        {showHypothesisBuilder && (
          <div className="px-5 py-4 bg-gradient-to-r from-purple-900/20 to-blue-900/10">
            {experienceMode === 'beginner' && (
              <div className="mb-3">
                <p className="text-[11px] text-slate-300 mb-2">The system behavior suggests:</p>
                <div className="flex flex-wrap gap-2">
                  {beginnerSuggestions.map((s) => (
                    <button
                      key={s}
                      type="button"
                      disabled={isProcessing}
                      onClick={() => onAction(`hypothesis_text:${s}`)}
                      className="px-2 py-1 rounded border border-purple-700/40 bg-purple-900/20 hover:bg-purple-800/30 text-xs text-purple-200 disabled:opacity-50"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <form onSubmit={handleNlpSubmit} className="flex gap-2 mb-3 relative z-20">
              <input
                type="text"
                value={nlpInput}
                onChange={(e) => setNlpInput(e.target.value)}
                disabled={isProcessing}
                placeholder={
                  isProcessing
                    ? 'Validating theory...'
                    : experienceMode === 'beginner'
                    ? 'Simple sentence: input validation is active'
                    : experienceMode === 'intermediate'
                    ? 'Describe your reasoning briefly and clearly...'
                    : 'Describe your hypothesis...'
                }
                className="flex-1 bg-[#161618] border border-slate-700 rounded p-2.5 text-sm text-slate-200 outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all font-mono placeholder:text-slate-600 disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={!nlpInput.trim() || isProcessing}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-500 disabled:bg-slate-800 disabled:text-slate-500 text-white font-bold uppercase tracking-widest text-xs rounded transition-colors"
              >
                Submit
              </button>
            </form>

            {hypotheses.filter(h => h.tested).length > 0 && (
              <div className={`space-y-2 border-t border-purple-900/40 pt-3 ${pulseHypotheses ? 'animate-pulse' : ''}`}>
                {hypotheses.filter(h => h.tested).map((hyp) => (
                  <div
                    key={hyp.id}
                    className={`w-full text-left p-2.5 rounded-lg border flex flex-col gap-2 ${
                      hyp.validated === true
                        ? 'bg-emerald-900/20 border-emerald-500/30 text-emerald-300'
                        : 'bg-red-900/20 border-red-500/30 text-red-300'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="text-xs font-bold leading-relaxed">{hyp.label}</div>
                      <div className={`text-base font-bold ${hyp.validated === true ? 'text-emerald-400' : 'text-red-400'}`}>
                        {hyp.validated === true ? '✓' : '✗'}
                      </div>
                    </div>
                    {hyp.explanation && (
                      <div className="text-[10px] text-slate-300">
                        <JargonText text={hyp.explanation} maxHighlights={2} />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
