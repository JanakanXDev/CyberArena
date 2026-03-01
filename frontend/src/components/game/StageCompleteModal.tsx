import React from 'react';
import { CheckCircle, ArrowRight, Home } from 'lucide-react';

interface StageCompleteModalProps {
  message: string;
  onContinue: () => void;
  onExit: () => void;
}

export const StageCompleteModal: React.FC<StageCompleteModalProps> = ({
  message,
  onContinue,
  onExit
}) => {
  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-[#1a1a1c] border-2 border-emerald-500/50 rounded-lg shadow-2xl w-full max-w-2xl p-8 relative">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <CheckCircle className="w-16 h-16 text-emerald-400" />
          </div>
          <h1 className="text-4xl font-black text-emerald-400 mb-4 uppercase tracking-widest">
            STAGE COMPLETE
          </h1>
          <p className="text-lg text-slate-300 font-mono">
            {message}
          </p>
        </div>

        <div className="bg-emerald-900/20 rounded-lg p-6 mb-6 border border-emerald-500/30">
          <h3 className="text-sm font-bold text-emerald-400 uppercase tracking-widest mb-3">
            Objectives Achieved
          </h3>
          <ul className="text-sm text-slate-300 space-y-2">
            <li className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              Vulnerabilities identified and handled
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              System integrity maintained
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              Detection managed effectively
            </li>
          </ul>
        </div>

        <div className="flex gap-4">
          <button
            onClick={onContinue}
            className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white font-black py-4 rounded-lg flex items-center justify-center gap-2 transition-colors uppercase tracking-widest text-sm shadow-lg hover:shadow-emerald-500/50"
          >
            <ArrowRight className="w-4 h-4" />
            Continue to Next Stage
          </button>
          <button
            onClick={onExit}
            className="flex-1 bg-slate-800 hover:bg-slate-700 text-white font-bold py-4 rounded-lg flex items-center justify-center gap-2 transition-colors uppercase tracking-widest text-sm border border-slate-700"
          >
            <Home className="w-4 h-4" />
            Return to Base
          </button>
        </div>
      </div>
    </div>
  );
};
