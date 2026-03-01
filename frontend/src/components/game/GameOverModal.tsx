import React from 'react';
import { AlertTriangle, X, RefreshCw, Home } from 'lucide-react';

interface GameOverModalProps {
  reason: string;
  message: string;
  onRestart: () => void;
  onExit: () => void;
}

export const GameOverModal: React.FC<GameOverModalProps> = ({
  reason,
  message,
  onRestart,
  onExit
}) => {
  const getIcon = () => {
    switch (reason) {
      case 'detected':
        return <AlertTriangle className="w-16 h-16 text-red-400" />;
      case 'system_destroyed':
        return <AlertTriangle className="w-16 h-16 text-amber-400" />;
      case 'critical_risk':
        return <AlertTriangle className="w-16 h-16 text-red-500" />;
      default:
        return <AlertTriangle className="w-16 h-16 text-slate-400" />;
    }
  };

  const getTitle = () => {
    switch (reason) {
      case 'detected':
        return 'MISSION COMPROMISED';
      case 'system_destroyed':
        return 'SYSTEM DESTROYED';
      case 'critical_risk':
        return 'CRITICAL FAILURE';
      default:
        return 'GAME OVER';
    }
  };

  return (
    <div className="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-[#1a1a1c] border-2 border-red-500/50 rounded-lg shadow-2xl w-full max-w-2xl p-8 relative">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            {getIcon()}
          </div>
          <h1 className="text-4xl font-black text-red-400 mb-4 uppercase tracking-widest">
            {getTitle()}
          </h1>
          <p className="text-lg text-slate-300 font-mono">
            {message}
          </p>
        </div>

        <div className="bg-slate-900/50 rounded-lg p-6 mb-6">
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-3">
            What Happened?
          </h3>
          <p className="text-sm text-slate-300 leading-relaxed">
            {reason === 'detected' && 
              "Your activities triggered detection systems. The AI defender identified your actions and compromised your mission. In real scenarios, this would result in immediate response and containment."}
            {reason === 'system_destroyed' && 
              "System integrity reached zero. The target system has been completely compromised and is no longer operational."}
            {reason === 'critical_risk' && 
              "Risk level reached maximum. The combination of your actions created an unacceptable level of risk."}
          </p>
        </div>

        <div className="flex gap-4">
          <button
            onClick={onRestart}
            className="flex-1 bg-slate-800 hover:bg-slate-700 text-white font-bold py-4 rounded-lg flex items-center justify-center gap-2 transition-colors uppercase tracking-widest text-sm border border-slate-700"
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </button>
          <button
            onClick={onExit}
            className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white font-black py-4 rounded-lg flex items-center justify-center gap-2 transition-colors uppercase tracking-widest text-sm shadow-lg hover:shadow-emerald-500/50"
          >
            <Home className="w-4 h-4" />
            Return to Base
          </button>
        </div>
      </div>
    </div>
  );
};
