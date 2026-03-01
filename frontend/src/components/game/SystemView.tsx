import React, { forwardRef } from 'react';
import { Log, SystemComponent } from '../../types/game';
import { Server, AlertCircle, CheckCircle, Activity } from 'lucide-react';

interface SystemViewProps {
  logs: Log[];
  components: Record<string, SystemComponent>;
}

export const SystemView = forwardRef<HTMLDivElement, SystemViewProps>(
  ({ logs, components }, ref) => {
    return (
      <div className="h-full flex flex-col pt-8">
        {/* System Components Status */}
        <div className="px-6 pb-4 border-b border-slate-800">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">
            Components
          </div>
          <div className="grid grid-cols-3 gap-3">
            {Object.entries(components).map(([id, comp]) => (
              <div
                key={id}
                className="bg-slate-900/50 border border-slate-800 rounded p-2"
              >
                <div className="flex items-center gap-2 mb-1">
                  <Server className="w-3 h-3 text-slate-500" />
                  <span className="text-xs font-bold text-slate-300">{id}</span>
                </div>
                <div className="flex flex-wrap items-center gap-2 text-[10px]">
                  {comp.monitoring && (
                    <span className="text-blue-400 flex items-center gap-1">
                      <AlertCircle className="w-2 h-2" /> Monitoring
                    </span>
                  )}
                  {comp.hardened && (
                    <span className="text-emerald-400 flex items-center gap-1">
                      <CheckCircle className="w-2 h-2" /> Hardened
                    </span>
                  )}
                  {(comp.signals || []).map((signal) => (
                    <span
                      key={`${id}-${signal}`}
                      className="text-amber-400 flex items-center gap-1"
                    >
                      <Activity className="w-2 h-2" /> {signal}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* System Logs (Partial, Noisy Signals) */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-1 font-mono text-sm">
          {logs.map((log) => (
            <div key={log.id} className="text-slate-300">
              <span className="text-slate-600 mr-2">[{log.timestamp}]</span>
              <span className="text-slate-500 text-xs mr-2">{log.source}:</span>
              <span
                className={
                  log.type === 'error'
                    ? 'text-red-400'
                    : log.type === 'warning'
                    ? 'text-amber-400'
                    : log.type === 'success'
                    ? 'text-emerald-400'
                    : 'text-slate-400'
                }
              >
                {log.message}
              </span>
            </div>
          ))}
          <div ref={ref} />
        </div>
      </div>
    );
  }
);

SystemView.displayName = 'SystemView';
