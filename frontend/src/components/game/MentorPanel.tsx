import React from 'react';
import { MentorGuidance } from '../../types/game';
import { Brain, HelpCircle, AlertTriangle, BookOpen, X } from 'lucide-react';

interface MentorPanelProps {
  guidance: MentorGuidance;
  onClose?: () => void;
}

export const MentorPanel: React.FC<MentorPanelProps> = ({ guidance, onClose }) => {
  return (
    <div className="w-full h-full flex flex-col overflow-hidden">
      <div className="sticky top-0 bg-[#1a1a1c] border-b border-emerald-500/30 p-6 flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-500/20 rounded-lg">
            <Brain className="w-6 h-6 text-emerald-400 animate-pulse" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-emerald-400 uppercase tracking-widest">
              Mentor Analysis
            </h2>
            <p className="text-xs text-slate-500">Analyzing current situation...</p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-slate-300 transition-colors p-2 hover:bg-slate-800 rounded"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Situation Summary */}
        {guidance.situation_summary && (
          <div className="bg-emerald-900/20 border border-emerald-500/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="w-5 h-5 text-emerald-400" />
              <span className="text-sm font-bold text-emerald-400 uppercase tracking-widest">
                Situation Analysis
              </span>
            </div>
            <p className="text-sm text-slate-300 leading-relaxed">
              {guidance.situation_summary}
            </p>
          </div>
        )}

        {/* Observations */}
        {guidance.observations && guidance.observations.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="w-5 h-5 text-blue-400" />
              <span className="text-sm font-bold text-slate-400 uppercase tracking-widest">
                Observations
              </span>
            </div>
            <div className="space-y-2">
              {guidance.observations.map((obs, idx) => (
                <div
                  key={idx}
                  className="text-sm text-blue-300 p-3 bg-blue-900/20 rounded border border-blue-500/30"
                >
                  {obs}
                </div>
              ))}
            </div>
          </div>
        )}
        {/* Next Steps - Most Important */}
        {guidance.next_steps && guidance.next_steps.length > 0 && (
          <div className="bg-gradient-to-r from-emerald-900/30 to-blue-900/30 border-2 border-emerald-500/50 rounded-lg p-5">
            <div className="flex items-center gap-2 mb-4">
              <Brain className="w-6 h-6 text-emerald-400 animate-pulse" />
              <span className="text-base font-bold text-emerald-400 uppercase tracking-widest">
                What To Do Next
              </span>
            </div>
            <div className="space-y-3">
              {guidance.next_steps.map((step, idx) => (
                <div
                  key={idx}
                  className="text-base text-emerald-100 p-4 bg-slate-900/70 rounded-lg border border-emerald-500/30 font-medium"
                >
                  {step}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Questions */}
        {guidance.questions.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <HelpCircle className="w-5 h-5 text-emerald-400" />
              <span className="text-sm font-bold text-emerald-400 uppercase tracking-widest">
                Guiding Questions
              </span>
            </div>
            <div className="space-y-3">
              {guidance.questions.map((q, idx) => (
                <div
                  key={idx}
                  className="text-sm text-slate-200 p-4 bg-slate-900/50 rounded-lg border border-slate-800 hover:border-emerald-500/30 transition-colors"
                >
                  <span className="text-emerald-400 font-bold mr-2">Q{idx + 1}:</span>
                  {q}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Anomalies */}
        {guidance.anomalies.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              <span className="text-sm font-bold text-amber-400 uppercase tracking-widest">
                Anomalies Detected
              </span>
            </div>
            <div className="space-y-2">
              {guidance.anomalies.map((a, idx) => (
                <div
                  key={idx}
                  className="text-sm text-amber-300 p-3 bg-amber-900/20 rounded-lg border border-amber-500/30"
                >
                  {a}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Inconsistencies */}
        {guidance.inconsistencies.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              <span className="text-sm font-bold text-red-400 uppercase tracking-widest">
                Inconsistencies Found
              </span>
            </div>
            <div className="space-y-2">
              {guidance.inconsistencies.map((i, idx) => (
                <div
                  key={idx}
                  className="text-sm text-red-300 p-3 bg-red-900/20 rounded-lg border border-red-500/30"
                >
                  {i}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Concepts to Study */}
        {guidance.concepts.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <BookOpen className="w-5 h-5 text-emerald-400" />
              <span className="text-sm font-bold text-emerald-400 uppercase tracking-widest">
                Concepts to Review
              </span>
            </div>
            <div className="space-y-2">
              {guidance.concepts.map((c, idx) => (
                <div
                  key={idx}
                  className="text-sm text-emerald-300 p-3 bg-emerald-900/20 rounded-lg border border-emerald-500/30"
                >
                  {c}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
