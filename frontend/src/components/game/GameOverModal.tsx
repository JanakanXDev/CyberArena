import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, Trophy, RefreshCw, ArrowRight } from 'lucide-react';

// Inside GameOverModal.tsx

interface GameOverModalProps {
  // Relax the type to string so it accepts 'Running' or 'Failed' without crashing
  result: string; 
  score: number;
  onRestart: () => void;
  currentLevelId: string;
}
// ... rest of the file
// DEFINE THE ORDER OF LEVELS HERE
// UPDATE THIS LIST TO MATCH scenarios.py KEYS EXACTLY
const LEVEL_ORDER = [
  'linux_basics_1', 
  'web_sqli', 
  'net_ftp', 
  'sys_privesc', 
  'forensics_logs'
];

export const GameOverModal: React.FC<GameOverModalProps> = ({ result, score, onRestart, currentLevelId }) => {
  const navigate = useNavigate();
  const isWin = result === 'Victory';

  const handleNextLevel = () => {
    // 1. FIND CURRENT INDEX
    const currentIndex = LEVEL_ORDER.indexOf(currentLevelId);
    
    // 2. DETERMINE NEXT LEVEL ID
    if (currentIndex !== -1 && currentIndex < LEVEL_ORDER.length - 1) {
      const nextLevelId = LEVEL_ORDER[currentIndex + 1];
      
      // 3. SAVE TO LOCAL STORAGE
      const saved = localStorage.getItem('cyber_progress_ids');
      const unlockedIds: string[] = saved ? JSON.parse(saved) : ['web_sqli'];
      
      if (!unlockedIds.includes(nextLevelId)) {
        unlockedIds.push(nextLevelId);
        localStorage.setItem('cyber_progress_ids', JSON.stringify(unlockedIds));
      }
    }
    
    navigate('/learn');
  };

  return (
    <div className="fixed inset-0 bg-black/90 backdrop-blur-sm flex items-center justify-center z-50 p-4 font-mono">
      <div className={`
        max-w-md w-full border-2 rounded-xl p-8 text-center shadow-[0_0_50px_rgba(0,0,0,0.5)] relative overflow-hidden
        ${isWin ? 'border-emerald-500 bg-slate-900' : 'border-red-600 bg-slate-900'}
      `}>
        {/* ANIMATED BACKGROUND GLOW */}
        <div className={`absolute inset-0 opacity-20 ${isWin ? 'bg-emerald-500/20' : 'bg-red-500/20'} animate-pulse`} />

        <div className="relative z-10">
          <div className="flex justify-center mb-6">
            <div className={`p-6 rounded-full border-4 ${isWin ? 'bg-emerald-900/50 border-emerald-500' : 'bg-red-900/50 border-red-500'}`}>
              {isWin ? <Trophy className="w-16 h-16 text-emerald-400" /> : <ShieldAlert className="w-16 h-16 text-red-500" />}
            </div>
          </div>

          <h2 className={`text-3xl font-black tracking-widest mb-2 uppercase ${isWin ? 'text-white' : 'text-red-500'}`}>
            {isWin ? 'MISSION ACCOMPLISHED' : 'CONNECTION TERMINATED'}
          </h2>
          
          <p className="text-slate-400 mb-8 text-sm">
            {isWin 
              ? `Root access achieved. Intelligence gathered. Logging out...` 
              : "Intrusion Detection System (IDS) flagged your IP. You have been blacklisted."}
          </p>

          <div className="flex flex-col gap-3">
            {isWin && (
              <button
                onClick={handleNextLevel}
                className="w-full py-4 px-6 rounded font-bold flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-900/50 transition-all hover:scale-105"
              >
                ACCESS NEXT TARGET <ArrowRight className="w-5 h-5" />
              </button>
            )}

            <button
              onClick={onRestart}
              className={`
                w-full py-3 px-4 rounded font-bold flex items-center justify-center gap-2 transition-all border
                ${isWin 
                  ? 'bg-transparent border-emerald-800 text-emerald-500 hover:bg-emerald-900/20' 
                  : 'bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-900/50'}
              `}
            >
              <RefreshCw className="w-4 h-4" />
              {isWin ? 'REPLAY MISSION' : 'REBOOT SYSTEM'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};