import React, { useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Shield, GraduationCap, Globe, Server, Terminal, Play, Target, ShieldCheck, Code, BookOpen } from 'lucide-react';
import { ExperienceMode, LearningMode } from '../../types/game';

export const MissionSelect = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const presetExperience = (location.state?.experienceMode as ExperienceMode) || 'advanced';
  const [selectedMode, setSelectedMode] = useState<LearningMode | null>(null);
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null);
  const [difficulty, setDifficulty] = useState<string>('medium');
  const [experienceMode, setExperienceMode] = useState<ExperienceMode>(presetExperience);

  const learningModes = [
    {
      id: 'guided_simulation' as LearningMode,
      title: 'Guided Simulation',
      description: 'Continuous simulation with hidden phases. Outcomes hidden before actions. At least one action appears successful but fails later.',
      icon: <Play className="w-6 h-6 text-blue-400" />,
      color: 'blue'
    },
    {
      id: 'attacker_campaign' as LearningMode,
      title: 'Attacker Campaign',
      description: 'Play as attacker. AI defender actively monitors, patches, blocks, and deploys deception. Learn stealth, evasion, pivoting.',
      icon: <Target className="w-6 h-6 text-red-400" />,
      color: 'red'
    },
    {
      id: 'defender_campaign' as LearningMode,
      title: 'Defender Campaign',
      description: 'Play as defender. AI attacker probes, escalates, persists, and adapts. Learn detection, incident response, forensics.',
      icon: <ShieldCheck className="w-6 h-6 text-emerald-400" />,
      color: 'emerald'
    },
    {
      id: 'playground' as LearningMode,
      title: 'Playground Mode',
      description: 'No fixed objectives. Full freedom. Multiple unstable surfaces active. Optional AI opponent. Break the system, recover manually.',
      icon: <Code className="w-6 h-6 text-purple-400" />,
      color: 'purple'
    }
  ];

  const scenarios = [
    {
      id: 'level_0_tutorial',
      title: 'Level 0: The Evidence Loop',
      category: 'Tutorial',
      difficulty: 'Trainee',
      icon: <GraduationCap className="w-6 h-6 text-yellow-500" />,
      desc: 'Learn the core game loop: investigate first, deduce second.',
      tier: 'all'
    },
    {
      id: 'beginner_input_basics',
      title: 'Beginner: Input Validation Basics',
      category: 'Beginner',
      difficulty: 'Beginner',
      icon: <Globe className="w-6 h-6 text-emerald-300" />,
      desc: 'Simple input handling signals with clear cause and effect.',
      tier: 'beginner'
    },
    {
      id: 'beginner_rate_limit_basics',
      title: 'Beginner: Rate Limit Basics',
      category: 'Beginner',
      difficulty: 'Beginner',
      icon: <Server className="w-6 h-6 text-emerald-300" />,
      desc: 'Understand request bursts vs spaced traffic in a controlled API.',
      tier: 'beginner'
    },
    {
      id: 'beginner_auth_basics',
      title: 'Beginner: Authentication Basics',
      category: 'Beginner',
      difficulty: 'Beginner',
      icon: <Shield className="w-6 h-6 text-emerald-300" />,
      desc: 'Learn retry windows and lockout behavior with minimal complexity.',
      tier: 'beginner'
    },
    {
      id: 'intermediate_signal_fusion',
      title: 'Intermediate: Signal Fusion',
      category: 'Intermediate',
      difficulty: 'Intermediate',
      icon: <Terminal className="w-6 h-6 text-amber-300" />,
      desc: 'Combine multiple system signals with mild ambiguity.',
      tier: 'intermediate'
    },
    {
      id: 'input_trust_failures',
      title: 'Operation: Broken Trust',
      category: 'Web Exploitation',
      difficulty: 'Recruit',
      icon: <Globe className="w-6 h-6 text-blue-400" />,
      desc: 'Legacy admin portal with brittle input handling. Multiple interacting fault lines.',
      tier: 'advanced'
    },
    {
      id: 'linux_privesc',
      title: 'Operation: Glass Ceiling',
      category: 'Linux Operations',
      difficulty: 'Veteran',
      icon: <Terminal className="w-6 h-6 text-emerald-400" />,
      desc: 'Standard shell obtained. Escalation required. Detection systems active.',
      tier: 'advanced'
    },
    {
      id: 'network_breach',
      title: 'Operation: Silent Echo',
      category: 'Network Intrusion',
      difficulty: 'Elite',
      icon: <Server className="w-6 h-6 text-purple-400" />,
      desc: 'Pivot through DMZ. Lateral movement. Exfiltration required.',
      tier: 'advanced'
    }
  ];

  const visibleScenarios = useMemo(() => {
    if (experienceMode === 'beginner') {
      return scenarios.filter((s) => s.tier === 'beginner' || s.tier === 'all');
    }
    if (experienceMode === 'intermediate') {
      return scenarios.filter((s) => s.tier === 'intermediate' || s.id === 'input_trust_failures' || s.tier === 'all');
    }
    return scenarios.filter((s) => s.tier === 'advanced' || s.tier === 'all');
  }, [experienceMode]);

  const handleModeSelect = (mode: LearningMode) => {
    setSelectedMode(mode);
    setSelectedScenario(null);
  };

  const handleScenarioSelect = (scenarioId: string) => {
    setSelectedScenario(scenarioId);
  };

  const handleStart = () => {
    if (selectedMode && selectedScenario) {
      const scenario = scenarios.find(s => s.id === selectedScenario);
      navigate('/game', {
        state: {
          mode: selectedMode,
          scenarioId: selectedScenario,
          difficulty,
          scenarioName: scenario?.title ?? 'Operation: Broken Trust',
          experienceMode
        }
      });
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-slate-300 font-mono p-10">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-12 text-center space-y-4">
          <div className="inline-flex items-center justify-center p-4 bg-emerald-500/10 rounded-full mb-4">
            <Shield className="w-16 h-16 text-emerald-500" />
          </div>
          <h1 className="text-5xl font-black text-white tracking-tighter">
            CYBER<span className="text-emerald-500">ARENA</span>
          </h1>
          <p className="text-slate-500 max-w-2xl mx-auto">
            A serious cybersecurity simulation learning platform. Not a course, not a quiz, not a CTF.
            Train to think like real security engineers through hypothesis formation, strategic reasoning, and meaningful failure.
          </p>
        </div>

        {/* Learning Center Button */}
        <div className="mb-12 text-center">
          <button
            onClick={() => navigate('/learn')}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-black py-4 px-8 rounded-lg flex items-center justify-center gap-3 transition-all uppercase tracking-widest text-lg shadow-lg hover:shadow-blue-500/50 mx-auto"
          >
            <BookOpen className="w-6 h-6" />
            Learning Center
          </button>
          <p className="text-sm text-slate-500 mt-3">
            Start with interactive lessons to learn fundamentals, then apply them in operations
          </p>
        </div>

        {/* Learning Mode Selection */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-white mb-6 text-center uppercase tracking-widest">
            Select Learning Mode
          </h2>
          <div className="mb-6 bg-[#111] border border-slate-800 rounded-lg p-4">
            <div className="text-xs text-slate-400 uppercase tracking-widest font-bold mb-3">Choose Your Experience</div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {([
                { id: 'beginner', label: 'Beginner', desc: 'Guided learning and simple scenarios' },
                { id: 'intermediate', label: 'Intermediate', desc: 'Partial guidance and moderate ambiguity' },
                { id: 'advanced', label: 'Advanced', desc: 'Full simulation and current behavior' }
              ] as Array<{ id: ExperienceMode; label: string; desc: string }>).map((exp) => (
                <button
                  key={exp.id}
                  onClick={() => {
                    setExperienceMode(exp.id);
                    setSelectedScenario(null);
                  }}
                  className={`text-left p-3 rounded border transition-all ${
                    experienceMode === exp.id
                      ? 'border-emerald-500 bg-emerald-900/20'
                      : 'border-slate-800 bg-slate-900/40 hover:border-slate-700'
                  }`}
                >
                  <div className="text-sm font-bold text-white">{exp.label}</div>
                  <div className="text-xs text-slate-400 mt-1">{exp.desc}</div>
                </button>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {learningModes.map((mode) => (
              <button
                key={mode.id}
                onClick={() => handleModeSelect(mode.id)}
                className={`p-6 rounded-lg border text-left transition-all ${selectedMode === mode.id
                    ? `border-${mode.color}-500 bg-${mode.color}-900/20`
                    : 'border-slate-800 bg-[#111] hover:border-slate-700'
                  }`}
              >
                <div className="flex items-start gap-4 mb-3">
                  <div className={`p-3 rounded bg-slate-900`}>{mode.icon}</div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-white mb-2">{mode.title}</h3>
                    <p className="text-sm text-slate-400 leading-relaxed">{mode.description}</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Scenario Selection (shown after mode selection) */}
        {selectedMode && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white uppercase tracking-widest">
                Select Scenario
              </h2>
              <div className="flex items-center gap-4">
                <label htmlFor="difficulty-select" className="text-sm text-slate-400 uppercase tracking-widest">Difficulty:</label>
                <select
                  id="difficulty-select"
                  name="difficulty"
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="bg-slate-900 border border-slate-800 rounded px-3 py-1 text-sm text-slate-300"
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {visibleScenarios.map((scenario) => (
                <button
                  key={scenario.id}
                  onClick={() => handleScenarioSelect(scenario.id)}
                  className={`p-6 rounded-lg border text-left transition-all ${selectedScenario === scenario.id
                      ? 'border-emerald-500 bg-emerald-900/20'
                      : 'border-slate-800 bg-[#111] hover:border-slate-700'
                    }`}
                >
                  <div className="flex justify-between items-start mb-4">
                    <div className="p-3 bg-slate-900 rounded">{scenario.icon}</div>
                    <span className="text-[10px] font-bold uppercase tracking-widest bg-slate-900 px-2 py-1 rounded text-slate-500">
                      {scenario.difficulty}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">{scenario.title}</h3>
                  <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">
                    {scenario.category}
                  </div>
                  <p className="text-sm text-slate-400 leading-relaxed">{scenario.desc}</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Start Button */}
        {selectedMode && selectedScenario && (
          <div className="text-center">
            <button
              onClick={handleStart}
              className="bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-black py-4 px-12 rounded-lg flex items-center justify-center gap-3 transition-colors uppercase tracking-widest text-lg shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)] mx-auto"
            >
              <Play className="w-5 h-5 fill-current" />
              Start Simulation
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
