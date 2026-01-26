import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Sword, Lock, CheckCircle, ChevronRight, Globe } from 'lucide-react';

export const LearningSelect = () => {
  const navigate = useNavigate();
  const [role, setRole] = useState<'attacker' | 'defender'>('attacker');
  
  // 1. DEFINE LEVELS (Must match IDs in backend/scenarios.py)
  const levels = [
    { id: "linux_basics_1", title: "Linux Fundamentals", category: "Basics" },
    { id: "web_sqli", title: "Web Exploitation", category: "Web Security" },
    { id: "net_ftp", title: "Network Hacking", category: "Network" }
  ];

  // 2. SET DEFAULT UNLOCKED STATE
  const [unlockedIds, setUnlockedIds] = useState<string[]>(['linux_basics_1']);

  useEffect(() => {
    // Check localStorage
    const saved = localStorage.getItem('cyber_progress');
    if (saved) {
        try {
            const parsed = JSON.parse(saved);
            // MERGE saved progress with default to ensure Level 1 is ALWAYS unlocked
            const uniqueIds = Array.from(new Set([...parsed, 'linux_basics_1']));
            setUnlockedIds(uniqueIds);
        } catch (e) {
            // If error, reset to default
            setUnlockedIds(['linux_basics_1']);
        }
    } else {
        // If no save found, Force Level 1 unlock
        setUnlockedIds(['linux_basics_1']);
        localStorage.setItem('cyber_progress', JSON.stringify(['linux_basics_1']));
    }
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 p-8 font-mono relative overflow-hidden">
      
      {/* BACKGROUND GRID */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:40px_40px] opacity-10 pointer-events-none" />

      {/* HEADER */}
      <header className="max-w-5xl mx-auto mb-16 flex justify-between items-end relative z-10">
        <div>
          <h1 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400 mb-2 tracking-tighter">
            MISSION SELECT
          </h1>
          <p className="text-slate-500 font-bold uppercase tracking-widest">Select your target.</p>
        </div>
        
        {/* PLAYGROUND BUTTON */}
        <button 
          onClick={() => navigate('/playground')}
          className="group flex items-center gap-3 px-6 py-3 bg-slate-900 border border-emerald-500/30 hover:border-emerald-500 text-emerald-400 hover:text-white rounded-lg transition-all shadow-lg hover:shadow-[0_0_20px_rgba(16,185,129,0.2)]"
        >
          <div className="text-right">
            <div className="text-xs font-bold uppercase tracking-widest text-slate-500 group-hover:text-emerald-400">Sandbox Mode</div>
            <div className="font-bold">ENTER PLAYGROUND</div>
          </div>
          <Globe className="w-8 h-8 opacity-50 group-hover:opacity-100 transition-opacity" />
        </button>
      </header>

      {/* LEVEL LIST */}
      <div className="max-w-5xl mx-auto grid gap-6 relative z-10">
        {levels.map((level, idx) => {
          const isLocked = !unlockedIds.includes(level.id);
          
          return (
            <div 
              key={level.id}
              onClick={() => {
                if (!isLocked) {
                    navigate('/stages', { state: { scenarioId: level.id } });
                }
              }}
              className={`
                relative p-8 rounded-xl border-l-4 flex items-center justify-between transition-all duration-300 group
                ${isLocked 
                  ? 'bg-slate-900/20 border-l-slate-800 border-y border-r border-slate-800/50 opacity-60 cursor-not-allowed grayscale' 
                  : 'bg-slate-900 border-l-emerald-500 border-y border-r border-slate-800 hover:border-r-emerald-500/50 cursor-pointer hover:translate-x-2 shadow-xl'}
              `}
            >
              <div className="flex items-center gap-8">
                 {/* Number Badge */}
                 <div className={`
                   w-12 h-12 flex items-center justify-center font-black text-xl rounded
                   ${isLocked ? 'bg-slate-800 text-slate-600' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'}
                 `}>
                   {idx + 1}
                 </div>
                 
                 <div>
                   <div className="flex items-center gap-3 mb-1">
                      <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                        {level.category}
                      </span>
                      {unlockedIds.includes(level.id) && idx > 0 && <span className="text-[10px] text-emerald-500 font-bold flex items-center gap-1"><CheckCircle className="w-3 h-3"/> UNLOCKED</span>}
                   </div>
                   <h3 className={`text-2xl font-black uppercase ${isLocked ? 'text-slate-600' : 'text-white group-hover:text-emerald-300 transition-colors'}`}>
                     {level.title}
                   </h3>
                 </div>
              </div>

              {/* Action Icon */}
              <div>
                {isLocked ? (
                  <Lock className="w-6 h-6 text-slate-700" />
                ) : (
                  <button className="px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold rounded flex items-center gap-2 transition-all">
                    DEPLOY <ChevronRight className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};