import React, { forwardRef } from 'react';
import { Log } from '../../types/game';
import { ArrowRight, AlertCircle, CheckCircle, XCircle, Info, Skull, Shield } from 'lucide-react';
import { JargonText } from './JargonText';

interface EventLogProps {
  logs: Log[];
  actionHistory: Array<{
    action_id: string;
    action_label?: string;
    turn: number;
    timestamp: string;
    actually_failed?: boolean;
  }>;
}

// Detect if a log entry is an AI move (source = "AI Attacker" or "AI Defender")
const isAiLog = (log: Log) =>
  log.source.startsWith('AI ');

const isAiAttacker = (log: Log) => log.source === 'AI Attacker';

export const EventLog = forwardRef<HTMLDivElement, EventLogProps>(
  ({ logs, actionHistory }, ref) => {
    const getIcon = (log: Log) => {
      if (isAiAttacker(log)) return <Skull className="w-3 h-3 text-red-400 flex-shrink-0" />;
      if (isAiLog(log)) return <Shield className="w-3 h-3 text-cyan-400 flex-shrink-0" />;
      switch (log.type) {
        case 'success': return <CheckCircle className="w-3 h-3 text-emerald-400" />;
        case 'error': return <XCircle className="w-3 h-3 text-red-400" />;
        case 'warning': return <AlertCircle className="w-3 h-3 text-amber-400" />;
        default: return <Info className="w-3 h-3 text-blue-400" />;
      }
    };

    const getRowStyle = (log: Log) => {
      if (isAiAttacker(log))
        return 'border-l-2 border-red-600/70 pl-3 py-2 bg-red-950/20 hover:bg-red-950/30 transition-colors';
      if (isAiLog(log))
        return 'border-l-2 border-cyan-600/50 pl-3 py-2 bg-cyan-950/10 hover:bg-cyan-950/20 transition-colors';
      return 'border-l-2 border-slate-700 pl-3 py-2 hover:border-slate-600 transition-colors';
    };

    const getTextStyle = (log: Log) => {
      if (isAiAttacker(log)) return 'text-red-300';
      if (isAiLog(log)) return 'text-cyan-300';
      switch (log.type) {
        case 'error': return 'text-red-400';
        case 'warning': return 'text-amber-400';
        case 'success': return 'text-emerald-400';
        default: return 'text-slate-300';
      }
    };

    return (
      <div className="h-full flex flex-col pt-8">
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-2 font-mono text-sm">
          {logs.map((log) => (
            <div key={log.id} className={`flex gap-3 ${getRowStyle(log)}`}>
              <div className="flex-shrink-0 mt-0.5">{getIcon(log)}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-slate-500 text-xs font-bold">{log.timestamp}</span>
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${isAiAttacker(log)
                      ? 'bg-red-900/50 text-red-400'
                      : isAiLog(log)
                        ? 'bg-cyan-900/30 text-cyan-500'
                        : 'text-slate-600'
                    }`}>
                    {log.source}
                  </span>
                </div>
                <div className={`text-xs ${getTextStyle(log)}`}>
                  {log.message ? <JargonText text={log.message} maxHighlights={1} /> : null}
                </div>
              </div>
            </div>
          ))}

          {/* Action History */}
          {actionHistory.length > 0 && (
            <div className="mt-4 pt-4 border-t border-slate-800">
              <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">
                Action Trace
              </div>
              <div className="space-y-2">
                {actionHistory.slice(-5).map((action, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-xs text-slate-400">
                    <ArrowRight className="w-3 h-3 text-slate-600" />
                    <span className="font-mono">{action.action_label || action.action_id}</span>
                    {action.actually_failed && (
                      <span className="text-red-400 text-[10px]">(Failed)</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div ref={ref} />
        </div>
      </div>
    );
  }
);

EventLog.displayName = 'EventLog';
