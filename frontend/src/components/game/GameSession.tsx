import React, { useState, useCallback, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Dashboard } from '../layout/Dashboard';
import { BriefingScreen } from './BriefingScreen';
import { api } from '../../api/client';
import { ExperienceMode, GameState, LearningMode } from '../../types/game';

const LOADING_STATE: GameState = {
  mode: 'guided_simulation',
  scenarioId: 'loading',
  scenarioName: 'Initializing...',
  turnCount: 0,
  pressure: 0,
  stability: 100,
  availableActions: [],
  hypotheses: [],
  logs: [],
  systemComponents: {},
  systemConditions: {},
  userAssumptions: [],
  actionHistory: [],
  contradictions: [],
  sessionStatus: 'active',
  missionComplete: false
};

export const GameSession = () => {
  const location = useLocation();
  const {
    mode = 'guided_simulation' as LearningMode,
    scenarioId = 'input_trust_failures',
    difficulty = 'medium',
    scenarioName = 'Operation: Broken Trust',
    experienceMode = 'advanced' as ExperienceMode
  } = location.state || {};

  // Phase: 'briefing' → 'loading' → 'playing'
  const [phase, setPhase] = useState<'briefing' | 'loading' | 'playing'>('briefing');
  const [gameState, setGameState] = useState<GameState>(LOADING_STATE);

  const startGame = useCallback(async () => {
    setPhase('loading');
    try {
      const initialState = await api.startGame(mode, difficulty, scenarioId, 0, experienceMode);
      setGameState(initialState);
      setPhase('playing');
    } catch (error) {
      console.error('Connection failed:', error);
      alert(`Failed to start game: ${error instanceof Error ? error.message : String(error)}`);
      setPhase('briefing'); // Allow retry
    }
  }, [mode, difficulty, scenarioId, experienceMode]);

  const [isProcessing, setIsProcessing] = useState(false);
  const beginnerModuleIds = [
    'beginner_signals',
    'beginner_hypothesis',
    'beginner_actions',
    'beginner_cause_effect',
    'beginner_metrics',
    'beginner_final_simulation',
  ];

  const handleAction = async (input: string) => {
    if (gameState.sessionStatus === 'collapsed' || gameState.missionComplete || isProcessing) return;
    setIsProcessing(true);
    try {
      const newState = await api.sendAction(input);
      setGameState(newState);
    } catch (error) {
      console.error('Action error:', error);
      alert(`Action failed: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsProcessing(false);
    }
  };

  useEffect(() => {
    if (!gameState?.scenarioId || gameState?.scenarioState !== 'victory') return;
    if (!beginnerModuleIds.includes(gameState.scenarioId)) return;
    try {
      const raw = localStorage.getItem('beginner_learning_path_progress') || '[]';
      const completed = JSON.parse(raw) as string[];
      if (!completed.includes(gameState.scenarioId)) {
        localStorage.setItem(
          'beginner_learning_path_progress',
          JSON.stringify([...completed, gameState.scenarioId])
        );
      }
    } catch {
      // Ignore storage errors and keep gameplay functional.
    }
  }, [gameState]);

  if (phase === 'briefing') {
    return (
      <BriefingScreen
        mode={mode}
        scenarioName={scenarioName}
        onBegin={startGame}
      />
    );
  }

  if (phase === 'loading') {
    return (
      <div className="bg-black min-h-screen flex flex-col items-center justify-center gap-4 font-mono">
        <div className="text-emerald-500 text-xl animate-pulse tracking-widest">ESTABLISHING UPLINK...</div>
        <div className="w-48 h-0.5 bg-slate-800 rounded-full overflow-hidden">
          <div className="h-full bg-emerald-500 animate-[slide_1.5s_ease-in-out_infinite]" style={{ width: '60%' }} />
        </div>
      </div>
    );
  }

  return <Dashboard state={gameState} onAction={handleAction} isProcessing={isProcessing} />;
};
