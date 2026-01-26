import React, { forwardRef } from 'react';
import { Log } from '../../types/game';
import { ArrowRight, AlertCircle, CheckCircle, XCircle, Info } from 'lucide-react';

interface EventLogProps {
  logs: Log[];
  actionHistory: Array<{
    action_id: string;
    turn: number;
    timestamp: string;
    actually_failed?: boolean;
  }>;
}

export const EventLog = forwardRef<HTMLDivElement, EventLogProps>(
  ({ logs, actionHistory }, ref) => {
    const getIcon = (type: string) => {
      switch (type) {
        case 'success':
          return <CheckCircle className="w-3 h-3 text-emerald-400" />;
        case 'error':
          return <XCircle className="w-3 h-3 text-red-400" />;
        case 'warning':
          return <AlertCircle className="w-3 h-3 text-amber-400" />;
        default:
          return <Info className="w-3 h-3 text-blue-400" />;
      }
    };

    return (
      <div className="h-full flex flex-col pt-8">
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3 font-mono text-sm">
          {logs.map((log) => (
            <div
              key={log.id}
              className="flex gap-3 border-l-2 border-slate-700 pl-3 py-2 hover:border-slate-600 transition-colors"
            >
              <div className="flex-shrink-0 mt-0.5">{getIcon(log.type)}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-slate-500 text-xs font-bold">{log.timestamp}</span>
                  <span className="text-slate-600 text-[10px]">{log.source}</span>
                </div>
                <div
                  className={`text-xs ${
                    log.type === 'error'
                      ? 'text-red-400'
                      : log.type === 'warning'
                      ? 'text-amber-400'
                      : log.type === 'success'
                      ? 'text-emerald-400'
                      : 'text-slate-300'
                  }`}
                >
                  {log.message}
                </div>
              </div>
            </div>
          ))}

          {/* Action History with Cause-Effect */}
          {actionHistory.length > 0 && (
            <div className="mt-4 pt-4 border-t border-slate-800">
              <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">
                Action Trace
              </div>
              <div className="space-y-2">
                {actionHistory.slice(-5).map((action, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-2 text-xs text-slate-400"
                  >
                    <ArrowRight className="w-3 h-3 text-slate-600" />
                    <span className="font-mono">{action.action_id}</span>
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
