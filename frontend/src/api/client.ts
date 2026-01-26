import { GameState, LearningMode } from '../types/game';

const API_URL = 'http://localhost:5000';

export const api = {
  // START GAME: Start new simulation session
  startGame: async (
    mode: LearningMode = 'guided_simulation',
    difficulty: string = 'medium',
    scenarioId: string = 'input_trust_failures',
    stageIndex: number = 0
  ): Promise<GameState> => {
    console.log('API: startGame called with:', { mode, difficulty, scenarioId, stageIndex });
    console.log('API: Making request to:', `${API_URL}/start`);
    
    try {
      const response = await fetch(`${API_URL}/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode,
          difficulty,
          scenarioId,
          stageIndex
        }),
      });
      
      console.log('API: Response status:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('API: Error response:', errorText);
        throw new Error(`Failed to start session: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('API: Response data received:', data);
      return data;
    } catch (error) {
      console.error('API: startGame error:', error);
      throw error;
    }
  },

  // SEND ACTION: Send action, hypothesis, or command
  sendAction: async (actionIdOrCommand: string): Promise<GameState> => {
    console.log('API: sendAction called with:', actionIdOrCommand);
    
    try {
      const response = await fetch(`${API_URL}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          actionId: actionIdOrCommand
        }),
      });
      
      console.log('API: Action response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('API: Action error response:', errorText);
        throw new Error(`Action failed: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('API: Action response data:', data);
      return data;
    } catch (error) {
      console.error('API: sendAction error:', error);
      throw error;
    }
  },

  // TOGGLE MENTOR: Enable/disable mentor AI
  toggleMentor: async (): Promise<{ enabled: boolean }> => {
    const response = await fetch(`${API_URL}/mentor/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (!response.ok) throw new Error('Failed to toggle mentor');
    return response.json();
  },

  // GET MENTOR ANALYSIS: Get mentor's analysis of current situation
  getMentorAnalysis: async (): Promise<any> => {
    const response = await fetch(`${API_URL}/mentor/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (!response.ok) throw new Error('Failed to get mentor analysis');
    return response.json();
  },

  // GET LEARNING DATA: Get learning analytics and recommendations
  getLearningData: async (): Promise<any> => {
    const response = await fetch(`${API_URL}/learning/data`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (!response.ok) throw new Error('Failed to get learning data');
    return response.json();
  }
};