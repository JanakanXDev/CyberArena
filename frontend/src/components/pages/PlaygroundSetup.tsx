import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Sword, Globe, Server, Home, Play } from 'lucide-react';

export const PlaygroundSetup = () => {
  const navigate = useNavigate();
  
  const [selectedEnv, setSelectedEnv] = useState('sandbox_corp');
  const [difficulty, setDifficulty] = useState('medium');

  const environments = [
    { id: 'sandbox_corp', name: 'MegaCorp HQ', icon: <Server className="w-8 h-8 text-blue-400" />, desc: 'Windows Server. Active Directory environment.' },
    { id: 'sandbox_bank', name: 'Secure Bank API', icon: <Shield className="w-8 h-8 text-emerald-400" />, desc: 'Hardened Linux. High AI detection rate.' },
    { id: 'sandbox_iot', name: 'Smart Home Hub', icon: <Home className="w-8 h-8 text-amber-400" />, desc: 'Vulnerable IoT Gateway. Weak credentials.' },
  ];

  const handleStart = () => {
    navigate('/game', { 
      state: { 
        mode: 'sandbox', 
        scenarioId: selectedEnv, // Pass the specific sandbox ID
        difficulty: difficulty,
        inputMode: 'manual' // Sandbox is always manual
      } 
    });
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 font-mono">
      <div className="max-w-5xl w-full">
        <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400 mb-2">
          DEPLOYMENT CONFIGURATION
        </h1>
        <p className="text-slate-500 mb-12">Select your simulation environment and parameters.</p>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          {/* ENVIRONMENT SELECTOR */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-slate-400 text-sm uppercase font-bold tracking-widest mb-4">Select Target Environment</h2>
            <div className="grid grid-cols-1 gap-4">
              {environments.map((env) => (
                <div 
                  key={env.id}
                  onClick={() => setSelectedEnv(env.id)}
                  className={`
                    p-6 rounded-xl border cursor-pointer transition-all flex items-center gap-6
                    ${selectedEnv === env.id 
                      ? 'bg-slate-800 border-emerald-500 shadow-[0_0_20px_rgba(16,185,129,0.1)]' 
                      : 'bg-slate-900/50 border-slate-800 hover:bg-slate-800'}
                  `}
                >
                  <div className={`p-4 rounded-full ${selectedEnv === env.id ? 'bg-slate-700' : 'bg-slate-800'}`}>
                    {env.icon}
                  </div>
                  <div>
                    <h3 className={`text-lg font-bold ${selectedEnv === env.id ? 'text-white' : 'text-slate-400'}`}>
                      {env.name}
                    </h3>
                    <p className="text-slate-500 text-sm">{env.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* SIDEBAR SETTINGS */}
          <div className="space-y-8">
            {/* DIFFICULTY */}
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
              <h2 className="text-slate-400 text-sm uppercase font-bold tracking-widest mb-4">AI Sensitivity</h2>
              <div className="space-y-2">
                {['easy', 'medium', 'hard'].map((level) => (
                  <button 
                    key={level}
                    onClick={() => setDifficulty(level)}
                    className={`w-full p-3 rounded capitalize text-left font-bold transition-all ${difficulty === level ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-500 hover:text-white'}`}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </div>

            {/* LAUNCH BUTTON */}
            <button 
              onClick={handleStart}
              className="w-full py-6 bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white font-black text-xl rounded-xl shadow-2xl shadow-emerald-900/20 flex items-center justify-center gap-3 transition-transform hover:scale-[1.02]"
            >
              INITIALIZE LINK <Play className="w-6 h-6 fill-current" />
            </button>
            
            <button onClick={() => navigate('/')} className="w-full text-center text-slate-600 hover:text-slate-400 text-sm">
              Cancel Deployment
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};