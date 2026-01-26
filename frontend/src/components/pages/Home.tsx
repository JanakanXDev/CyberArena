import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Sword, GraduationCap, Gamepad2, Lock } from 'lucide-react';

export const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Background Grid Effect */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
      
      <div className="z-10 text-center max-w-4xl w-full">
        <h1 className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400 mb-4 tracking-tight">
          CYBER_ARENA
        </h1>
        <p className="text-slate-400 text-lg mb-12 max-w-2xl mx-auto">
          The advanced cyber warfare simulation platform. 
          Master the art of <span className="text-red-400">Offense</span> and <span className="text-blue-400">Defense</span>.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* OPTION 1: LEARNING PATH */}
          <div 
            onClick={() => navigate('/learn')}
            className="group relative bg-slate-900/50 border border-slate-800 hover:border-emerald-500 rounded-xl p-8 cursor-pointer transition-all hover:-translate-y-2 hover:shadow-[0_0_30px_rgba(16,185,129,0.2)]"
          >
            <div className="absolute top-4 right-4 bg-emerald-900/30 text-emerald-400 px-3 py-1 rounded-full text-xs font-bold border border-emerald-900">
              CAMPAIGN
            </div>
            <div className="bg-slate-800 w-16 h-16 rounded-lg flex items-center justify-center mb-6 group-hover:bg-emerald-500 transition-colors">
              <GraduationCap className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Learning Path</h2>
            <p className="text-slate-400 text-sm">
              Structured lessons. Choose your role (Attacker/Defender) and unlock modules one by one.
            </p>
          </div>

          {/* OPTION 2: PLAYGROUND */}
          <div 
            onClick={() => navigate('/play')}
            className="group relative bg-slate-900/50 border border-slate-800 hover:border-blue-500 rounded-xl p-8 cursor-pointer transition-all hover:-translate-y-2 hover:shadow-[0_0_30px_rgba(59,130,246,0.2)]"
          >
            <div className="absolute top-4 right-4 bg-blue-900/30 text-blue-400 px-3 py-1 rounded-full text-xs font-bold border border-blue-900">
              SANDBOX
            </div>
            <div className="bg-slate-800 w-16 h-16 rounded-lg flex items-center justify-center mb-6 group-hover:bg-blue-500 transition-colors">
              <Gamepad2 className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Cyber Playground</h2>
            <p className="text-slate-400 text-sm">
              Custom matches. Configure AI difficulty, scenarios, and test your skills freely.
            </p>
          </div>

        </div>
      </div>
    </div>
  );
};