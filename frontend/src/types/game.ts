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
  explanation?: string;
}

export interface SystemComponent {
  status: string;
  monitoring: boolean;
  hardened: boolean;
  signals?: string[];
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

  // Core metrics
  pressure: number;
  stability: number;

  // Actions (hypothesis-based)
  availableActions: Action[];

  // Hypotheses
  hypotheses: Hypothesis[];

  // Logs (for System View and Event Log)
  logs: Log[];

  // System View Data
  systemComponents: Record<string, SystemComponent>;
  systemConditions?: Record<string, boolean>;

  // Learning Data
  userAssumptions: Array<{
    id: string;
    label: string;
    timestamp: string;
    validated: boolean | null;
  }>;
  actionHistory: Array<{
    action_id: string;
    action_label: string;
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

  // Session state
  sessionStatus?: 'active' | 'collapsed';
  collapseReason?: string;
  collapseMessage?: string;
  reflectionSummary?: {
    initial_assumptions: Array<{ label: string; validated: boolean | null }>;
    what_broke: string[];
    system_adaptations: string[];
    what_finally_worked: string[];
    what_remains_unsafe: string[];
  };
  scenarioState?: string;
  missionComplete: boolean;
  strategicDebrief?: StrategicDebrief;
}

export interface StrategicDebrief {
  outcome: string;
  turns: number;
  final_pressure: number;
  final_stability: number;
  final_ai_entropy: number;
  ai_end_posture: string;
  hypotheses_validated: number;
  hypotheses_invalidated: number;
  summary: string;
}
