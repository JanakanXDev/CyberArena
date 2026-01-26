import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Dashboard } from '../layout/Dashboard';
import { api } from '../../api/client';
import { GameState, LearningMode } from '../../types/game';
import { RefreshCw, Play } from 'lucide-react';

const LOADING_STATE: GameState = {
  mode: 'guided_simulation',
  scenarioId: 'loading',
  scenarioName: 'Initializing...',
  turnCount: 0,
  riskScore: 0,
  detectionLevel: 0,
  integrity: 100,
  aiAggressiveness: 0,
  availableActions: [],
  hypotheses: [],
  logs: [],
  systemComponents: {},
  vulnerabilities: {},
  userAssumptions: [],
  actionHistory: [],
  contradictions: [],
  isGameOver: false,
  missionComplete: false
};

export const GameSession = () => {
  console.log('GameSession component rendering');
  
  const navigate = useNavigate();
  const location = useLocation();
  const { 
    mode = 'guided_simulation' as LearningMode,
    scenarioId = 'input_trust_failures',
    difficulty = 'medium'
  } = location.state || {};
  
  console.log('GameSession location state:', { mode, scenarioId, difficulty });
  
  const [gameState, setGameState] = useState<GameState>(LOADING_STATE);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    console.log('GameSession useEffect triggered');
    const initGame = async () => {
      console.log('initGame called with:', { mode, difficulty, scenarioId });
      setIsLoading(true);
      try {
        console.log('Calling api.startGame...');
        const initialState = await api.startGame(mode, difficulty, scenarioId, 0);
        console.log('Initial game state received:', initialState);
        console.log('Available actions:', initialState.availableActions?.length || 0);
        console.log('Available action IDs:', initialState.availableActions?.map((a: any) => a.id) || []);
        console.log('Hypotheses:', initialState.hypotheses?.length || 0);
        setGameState(initialState);
        console.log('Game state set');
      } catch (error) {
        console.error("Connection failed:", error);
        console.error("Error details:", error);
        alert(`Failed to start game: ${error instanceof Error ? error.message : String(error)}`);
      } finally {
        setIsLoading(false);
        console.log('Loading set to false');
      }
    };
    initGame();
  }, [mode, scenarioId, difficulty]);

  const handleAction = async (input: string) => {
    if (gameState.isGameOver || gameState.missionComplete) return;

    console.log('Handling action:', input);
    try {
      const newState = await api.sendAction(input);
      console.log('Action response:', newState);
      setGameState(newState);
    } catch (error) {
      console.error('Action error:', error);
      alert(`Action failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const handleRestart = () => window.location.reload();
  const handleExit = () => navigate('/');

  if (isLoading) {
    return (
      <div className="bg-black min-h-screen flex items-center justify-center text-emerald-500 font-mono text-xl animate-pulse">
        ESTABLISHING UPLINK...
      </div>
    );
  }

  // No completion screen - continuous simulation
  // In Guided Simulation mode, show debrief only at end
  // In other modes, simulation continues indefinitely

  return <Dashboard state={gameState} onAction={handleAction} />;
};