import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { BookOpen, Terminal, HelpCircle, ShieldAlert, CheckCircle, Lock, Play, ArrowLeft } from 'lucide-react';

export const StageSelect = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const scenarioId = location.state?.scenarioId || 'linux_basics_1';
  
  // In a real app, load this from API/LocalStorage
  const [completedStages] = useState<number[]>([0]); 

  // Hardcoded stages list (Should match backend/scenarios.py)
  const stages = [
    { id: 0, title: "The File Tree", type: "learn", icon: <BookOpen className="w-5 h-5"/> },
    { id: 1, title: "Reading Files", type: "learn", icon: <Terminal className="w-5 h-5"/> },
    { id: 2, title: "Knowledge Check", type: "quiz", icon: <HelpCircle className="w-5 h-5"/> },
    { id: 3, title: "Final Exam", type: "exam", icon: <ShieldAlert className="w-5 h-5"/> },
  ];

  const handleStageClick = (index: number) => {
    // Logic: Can only click unlocked stages
    if (index === 0 || completedStages.includes(index - 1) || completedStages.includes(index)) {
        navigate('/game', { state: { scenarioId, stageIndex: index } });
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 p-8 font-mono flex flex-col items-center">
      <div className="w-full max-w-2xl mb-8 flex items-center gap-4">
        <button onClick={() => navigate('/learn')} className="p-2 bg-slate-900 rounded hover:bg-slate-800 text-slate-400">
            <ArrowLeft className="w-6 h-6" />
        </button>
        <div>
            <h1 className="text-2xl font-bold text-emerald-400">MISSION: LINUX BASICS</h1>
            <p className="text-slate-500 text-sm">Complete all stages to earn your badge.</p>
        </div>
      </div>

      <div className="w-full max-w-2xl space-y-4">
        {stages.map((stage, idx) => {
          const isUnlocked = idx === 0 || completedStages.includes(idx - 1) || completedStages.includes(idx);
          const isDone = completedStages.includes(idx);

          return (
            <div 
              key={idx}
              onClick={() => handleStageClick(idx)}
              className={`
                relative p-6 rounded-xl border flex items-center justify-between transition-all duration-300
                ${isUnlocked 
                   ? 'bg-slate-900 border-slate-700 hover:border-emerald-500 cursor-pointer hover:translate-x-2' 
                   : 'bg-slate-900/30 border-slate-800 opacity-50 cursor-not-allowed'}
              `}
            >
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-full ${isDone ? 'bg-emerald-900/50 text-emerald-400' : 'bg-slate-800 text-slate-400'}`}>
                  {isDone ? <CheckCircle className="w-6 h-6"/> : stage.icon}
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">{stage.title}</h3>
                  <span className={`text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded border ${
                      stage.type === 'exam' ? 'border-red-900 text-red-400 bg-red-900/20' : 
                      stage.type === 'quiz' ? 'border-amber-900 text-amber-400 bg-amber-900/20' : 
                      'border-blue-900 text-blue-400 bg-blue-900/20'
                  }`}>
                      {stage.type}
                  </span>
                </div>
              </div>

              <div>
                {!isUnlocked ? <Lock className="w-5 h-5 text-slate-600"/> : <Play className="w-5 h-5 text-emerald-500"/>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};