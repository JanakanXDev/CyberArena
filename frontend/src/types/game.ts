// src/types/game.ts

export type LearningMode = 'guided_simulation' | 'attacker_campaign' | 'defender_campaign' | 'playground';

export interface Log {
  id: string;
  timestamp: string;
  source: string;
  category: 'system_view' | 'event_log';
  type: 'info' | 'success' | 'error' | 'warning';
  message: string;
}

export interface Action {
  id: string;
  label: string; // Hypothesis-based intent (e.g., "Probe input validation boundaries")
  description: string; // Conceptual description
  type: string; // "probe", "escalate", "isolate", "monitor", etc.
  available: boolean;
}

export interface Hypothesis {
  id: string;
  label: string;
  description: string;
  tested: boolean;
  validated: boolean | null;
}

export interface SystemComponent {
  status: string;
  monitoring: boolean;
  hardened: boolean;
}

export interface Vulnerability {
  active: boolean;
  exploited: boolean;
  detected: boolean;
}

export interface MentorGuidance {
  type: 'question' | 'analysis';
  situation_summary?: string;
  questions: string[];
  anomalies: string[];
  inconsistencies: string[];
  concepts: string[];
  observations?: string[];
  next_steps?: string[];
}

export interface GameState {
  mode: LearningMode;
  scenarioId: string;
  scenarioName: string;
  turnCount: number;
  
  // State Panel Metrics
  riskScore: number;
  detectionLevel: number;
  integrity: number;
  aiAggressiveness: number;
  
  // Actions (hypothesis-based)
  availableActions: Action[];
  
  // Hypotheses
  hypotheses: Hypothesis[];
  
  // Logs (for System View and Event Log)
  logs: Log[];
  
  // System View Data
  systemComponents: Record<string, SystemComponent>;
  vulnerabilities: Record<string, Vulnerability>;
  
  // Learning Data
  userAssumptions: Array<{
    id: string;
    label: string;
    timestamp: string;
    validated: boolean | null;
  }>;
  actionHistory: Array<{
    action_id: string;
    turn: number;
    timestamp: string;
    actually_failed?: boolean;
  }>;
  contradictions: Array<{
    id: string;
    description: string;
    turn: number;
  }>;
  
  // Mentor Guidance
  mentorGuidance?: MentorGuidance;
  
  // No phase shown, no completion flags (continuous simulation)
  isGameOver: boolean;
  missionComplete: boolean;
}