import React, { useEffect, useState, useRef } from 'react';
import { Server, Database, ShieldCheck, User, ArrowRight, Activity, Globe, Lock } from 'lucide-react';
import { VisualStep } from '../../types/game';

interface XRayPanelProps {
  trace: VisualStep[] | undefined;
}

export const XRayPanel: React.FC<XRayPanelProps> = ({ trace }) => {
  // SIMPLER LOGIC: Just count how many steps to show.
  // This prevents memory leaks and array crashes.
  const [visibleCount, setVisibleCount] = useState(0);
  
  // Use a ref to track if component is mounted (prevents memory leak crashes)
  const isMounted = useRef(true);

  useEffect(() => {
    isMounted.current = true;
    
    // Reset when the trace changes
    setVisibleCount(0);

    if (!trace || trace.length === 0) return;

    const interval = setInterval(() => {
      if (!isMounted.current) return;

      setVisibleCount((prev) => {
        if (prev < trace.length) {
          return prev + 1;
        }
        clearInterval(interval);
        return prev;
      });
    }, 1000); // 1 second per step

    return () => {
      isMounted.current = false;
      clearInterval(interval);
    };
  }, [trace]); // Re-run only if the trace object itself changes

  // SAFETY CHECK: If no trace, show nothing (don't crash)
  if (!trace || !Array.isArray(trace) || trace.length === 0) {
    return null;
  }

  const getIcon = (name: string) => {
    // Normalize string to handle case sensitivity
    const n = name.toLowerCase();
    if (n.includes('player') || n.includes('attacker')) return <User className="w-5 h-5 text-emerald-400" />;
    if (n.includes('firewall')) return <ShieldCheck className="w-5 h-5 text-amber-400" />;
    if (n.includes('server') || n.includes('http')) return <Globe className="w-5 h-5 text-blue-400" />;
    if (n.includes('database')) return <Database className="w-5 h-5 text-purple-400" />;
    if (n.includes('lock') || n.includes('auth')) return <Lock className="w-5 h-5 text-red-400" />;
    return <Server className="w-5 h-5 text-slate-400" />;
  };

  // Render only the slice of steps we are allowed to see
  const currentSteps = trace.slice(0, visibleCount);

  return (
    <div className="bg-slate-900/50 border border-slate-700 rounded-xl p-6 shadow-2xl backdrop-blur-sm animate-in fade-in duration-500">
      <div className="flex items-center gap-2 mb-6 border-b border-slate-700 pb-3">
        <Activity className="w-5 h-5 text-blue-400 animate-pulse" />
        <h3 className="text-sm font-bold text-blue-100 tracking-widest uppercase">
          Live Architecture Trace
        </h3>
      </div>
      
      <div className="space-y-4">
        {currentSteps.map((step, idx) => (
          <div key={idx} className="flex items-center gap-4 bg-black/20 p-3 rounded-lg border border-slate-800/50 animate-in slide-in-from-left-2 duration-300">
            
            {/* SOURCE NODE */}
            <div className="flex flex-col items-center gap-2 min-w-[60px]">
              <div className="bg-slate-800 p-2 rounded-full border border-slate-600 shadow-lg">
                {getIcon(step.source || 'Unknown')}
              </div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{step.source}</span>
            </div>

            {/* ANIMATED CONNECTION LINE */}
            <div className="flex-1 flex flex-col items-center relative px-2">
              <div className={`h-1 w-full rounded-full overflow-hidden ${step.status === 'danger' || step.status === 'fail' ? 'bg-red-900/30' : 'bg-emerald-900/30'}`}>
                 <div className={`h-full w-full origin-left animate-[grow_0.5s_ease-out] ${step.status === 'danger' || step.status === 'fail' ? 'bg-red-500' : 'bg-emerald-500'}`} />
              </div>
              
              {/* STATUS BADGE */}
              <div className={`
                mt-2 text-[10px] px-2 py-1 rounded font-mono uppercase font-bold
                ${step.status === 'danger' ? 'bg-red-900/40 text-red-400 border border-red-800' : 
                  step.status === 'fail' ? 'bg-orange-900/40 text-orange-400 border border-orange-800' : 
                  'bg-emerald-900/40 text-emerald-400 border border-emerald-800'}
              `}>
                {step.desc}
              </div>
            </div>

            {/* TARGET NODE */}
            <div className="flex flex-col items-center gap-2 min-w-[60px]">
              <div className="bg-slate-800 p-2 rounded-full border border-slate-600 shadow-lg">
                {getIcon(step.target || 'Unknown')}
              </div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{step.target}</span>
            </div>
            
          </div>
        ))}
      </div>
    </div>
  );
};
