import React from 'react';
import { AlertTriangle, BookOpen, Layers, Activity } from 'lucide-react';

interface StatusHUDProps {
  pressure: number;
  stability: number;
  userAssumptions: Array<{
    id: string;
    label: string;
    validated: boolean | null;
  }>;
  contradictions: Array<{
    id: string;
    description: string;
    turn: number;
  }>;
  systemConditions?: Record<string, boolean>;
  sessionStatus?: 'active' | 'collapsed';
  reflectionSummary?: {
    initial_assumptions: Array<{ label: string; validated: boolean | null }>;
    what_broke: string[];
    system_adaptations: string[];
    what_finally_worked: string[];
    what_remains_unsafe: string[];
  };
}

const CONDITION_LABELS: Record<string, string> = {
  errors_suppressed: 'Error detail suppressed',
  timing_jitter: 'Timing jitter introduced',
  route_shifted: 'Service routes shifted',
  validation_tightened: 'Input normalization tightened',
  access_restricted: 'Access scope restricted',
  deception_active: 'Deceptive responses active'
};

export const StatusHUD: React.FC<StatusHUDProps> = ({
  pressure,
  stability,
  userAssumptions,
  contradictions,
  systemConditions,
  sessionStatus,
  reflectionSummary
}) => {
  const activeSignals = Object.entries(systemConditions || {})
    .filter(([, active]) => active)
    .map(([key]) => CONDITION_LABELS[key] || key);

  const pressureColor =
    pressure >= 80 ? 'bg-red-500' :
      pressure >= 50 ? 'bg-amber-500' :
        pressure >= 25 ? 'bg-yellow-500' : 'bg-emerald-500';

  const stabilityColor =
    stability <= 20 ? 'bg-red-500' :
      stability <= 50 ? 'bg-amber-500' : 'bg-emerald-500';

  return (
    <div className="h-full flex flex-col pt-8">
      <div className="px-6 space-y-6 overflow-y-auto">

        {/* Live Metrics — Pressure & Stability */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Activity className="w-4 h-4 text-slate-400" />
            <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
              Threat Metrics
            </span>
          </div>
          <div className="space-y-3">
            {/* Pressure */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-[10px] text-slate-500 uppercase tracking-widest">Pressure</span>
                <span className={`text-xs font-bold tabular-nums ${pressure >= 70 ? 'text-red-400' : pressure >= 40 ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {pressure}%
                </span>
              </div>
              <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${pressureColor}`}
                  style={{ width: `${pressure}%` }}
                />
              </div>
            </div>
            {/* Stability */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-[10px] text-slate-500 uppercase tracking-widest">Stability</span>
                <span className={`text-xs font-bold tabular-nums ${stability <= 30 ? 'text-red-400' : stability <= 60 ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {stability}%
                </span>
              </div>
              <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${stabilityColor}`}
                  style={{ width: `${stability}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* System Signals */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Layers className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
              System Signals
            </span>
          </div>
          {activeSignals.length === 0 ? (
            <div className="text-xs text-slate-600">No visible behavioral signals.</div>
          ) : (
            <div className="space-y-2">
              {activeSignals.map((signal) => (
                <div
                  key={signal}
                  className="text-xs p-2 rounded border bg-slate-900/40 border-slate-800 text-slate-300"
                >
                  {signal}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* User Assumptions */}
        {userAssumptions.length > 0 && (
          <div className="pt-4 border-t border-slate-800">
            <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">
              Assumptions
            </div>
            <div className="space-y-2">
              {userAssumptions.slice(-5).map((assumption) => (
                <div
                  key={assumption.id}
                  className={`text-xs p-2 rounded border ${assumption.validated === true
                      ? 'bg-emerald-900/20 border-emerald-500/30 text-emerald-400'
                      : assumption.validated === false
                        ? 'bg-red-900/20 border-red-500/30 text-red-400'
                        : 'bg-slate-900/50 border-slate-800 text-slate-400'
                    }`}
                >
                  {assumption.label}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Contradictions */}
        {contradictions.length > 0 && (
          <div className="pt-4 border-t border-slate-800">
            <div className="text-xs font-bold text-red-400 uppercase tracking-widest mb-3 flex items-center gap-2">
              <AlertTriangle className="w-3 h-3" />
              Contradictions
            </div>
            <div className="space-y-2">
              {contradictions.slice(-3).map((contr) => (
                <div
                  key={contr.id}
                  className="text-xs p-2 rounded border bg-red-900/20 border-red-500/30 text-red-400"
                >
                  {contr.description}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Reflection Summary */}
        {sessionStatus === 'collapsed' && reflectionSummary && (
          <div className="pt-4 border-t border-slate-800">
            <div className="text-xs font-bold text-amber-400 uppercase tracking-widest mb-3 flex items-center gap-2">
              <BookOpen className="w-3 h-3" />
              Reflection Summary
            </div>
            <div className="space-y-3 text-xs text-slate-300">
              <div>
                <div className="text-slate-500 uppercase tracking-widest mb-1">Initial Assumptions</div>
                <div className="space-y-1">
                  {reflectionSummary.initial_assumptions.map((assumption, idx) => (
                    <div key={`${assumption.label}-${idx}`}>
                      {assumption.label} {assumption.validated === true ? '(held)' : assumption.validated === false ? '(broke)' : ''}
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <div className="text-slate-500 uppercase tracking-widest mb-1">What Broke</div>
                <div className="space-y-1">
                  {reflectionSummary.what_broke.map((item, idx) => (
                    <div key={`broke-${idx}`}>{item}</div>
                  ))}
                </div>
              </div>
              <div>
                <div className="text-slate-500 uppercase tracking-widest mb-1">System Adaptations</div>
                <div className="space-y-1">
                  {reflectionSummary.system_adaptations.map((item, idx) => (
                    <div key={`adapt-${idx}`}>{item}</div>
                  ))}
                </div>
              </div>
              <div>
                <div className="text-slate-500 uppercase tracking-widest mb-1">What Finally Worked</div>
                <div className="space-y-1">
                  {reflectionSummary.what_finally_worked.map((item, idx) => (
                    <div key={`worked-${idx}`}>{item}</div>
                  ))}
                </div>
              </div>
              <div>
                <div className="text-slate-500 uppercase tracking-widest mb-1">What Remains Unsafe</div>
                <div className="space-y-1">
                  {reflectionSummary.what_remains_unsafe.map((item, idx) => (
                    <div key={`unsafe-${idx}`}>{item}</div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
