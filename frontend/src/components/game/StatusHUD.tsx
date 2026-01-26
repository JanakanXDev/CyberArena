import React from 'react';
import { ShieldAlert, Eye, Activity, AlertTriangle } from 'lucide-react';
import { ProgressBar } from '../ui/ProgressBar';

interface StatusHUDProps {
  riskScore: number;
  detectionLevel: number;
  integrity: number;
  aiAggressiveness: number;
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
}

export const StatusHUD: React.FC<StatusHUDProps> = ({
  riskScore,
  detectionLevel,
  integrity,
  aiAggressiveness,
  userAssumptions,
  contradictions
}) => {
  return (
    <div className="h-full flex flex-col pt-8">
      <div className="px-6 space-y-6 overflow-y-auto">
        {/* Risk Score */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-red-400" />
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                Risk Score
              </span>
            </div>
            <span
              className={`text-lg font-bold ${
                riskScore > 70
                  ? 'text-red-400'
                  : riskScore > 40
                  ? 'text-amber-400'
                  : 'text-slate-400'
              }`}
            >
              {riskScore}%
            </span>
          </div>
          <ProgressBar
            value={riskScore}
            max={100}
            color={riskScore > 70 ? 'red' : riskScore > 40 ? 'amber' : 'slate'}
          />
        </div>

        {/* Detection Level */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Eye className="w-4 h-4 text-blue-400" />
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                Detection Level
              </span>
            </div>
            <span
              className={`text-lg font-bold ${
                detectionLevel > 70
                  ? 'text-red-400'
                  : detectionLevel > 40
                  ? 'text-amber-400'
                  : 'text-blue-400'
              }`}
            >
              {detectionLevel}%
            </span>
          </div>
          <ProgressBar
            value={detectionLevel}
            max={100}
            color={detectionLevel > 70 ? 'red' : detectionLevel > 40 ? 'amber' : 'blue'}
          />
        </div>

        {/* Integrity */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                System Integrity
              </span>
            </div>
            <span
              className={`text-lg font-bold ${
                integrity > 80
                  ? 'text-emerald-400'
                  : integrity > 50
                  ? 'text-amber-400'
                  : 'text-red-400'
              }`}
            >
              {integrity}%
            </span>
          </div>
          <ProgressBar
            value={integrity}
            max={100}
            color={integrity > 80 ? 'emerald' : integrity > 50 ? 'amber' : 'red'}
          />
        </div>

        {/* AI Aggressiveness */}
        {aiAggressiveness > 0 && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-purple-400" />
                <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                  AI Aggressiveness
                </span>
              </div>
              <span className="text-lg font-bold text-purple-400">{aiAggressiveness}%</span>
            </div>
            <ProgressBar value={aiAggressiveness} max={100} color="purple" />
          </div>
        )}

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
                  className={`text-xs p-2 rounded border ${
                    assumption.validated === true
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
      </div>
    </div>
  );
};
