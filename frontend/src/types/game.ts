// src/types/game.ts

export type LearningMode = 'guided_simulation' | 'attacker_campaign' | 'defender_campaign' | 'playground';
export type ExperienceMode = 'beginner' | 'intermediate' | 'advanced';

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
  time_cost?: number;
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
  experienceMode?: ExperienceMode;
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
    action_type?: string;
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

  // AI Counter-Move system
  aiLastMove?: AiMove;
  aiMoveHistory?: AiMove[];

  // Additive hypothesis evaluation envelope (optional, backend-provided)
  hypothesisEvaluation?: HypothesisEvaluation;
  beginnerLearningPath?: BeginnerLearningPath;
  beginnerStepFeedback?: BeginnerStepFeedback;
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
  score?: number;
  grade?: string;
  metrics_breakdown?: {
    efficiency: { label: string; penalty: string; raw: number };
    accuracy: { label: string; bonus: string; raw: number };
    stealth: { label: string; penalty: string; raw: number };
    stability: { label: string; bonus: string; raw: number };
  };
}

export interface AiMove {
  name: string;
  label: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  effects_summary: string[];     // e.g. ["+15 Pressure", "Locks Isolate (1t)"]
  counter_hint: string;          // what to do to counter this
  message?: string;
}

export interface VisualStep {
  source: string;
  target: string;
  status: 'safe' | 'warning' | 'danger' | 'fail' | string;
  desc: string;
}

export interface HypothesisEvaluation {
  status: 'correct' | 'partial' | 'wrong';
  feedback: string;
  hint: string;
  matched_signals: string[];
}

export interface BeginnerLearningPath {
  title: string;
  moduleOrder: Array<{ id: string; name: string }>;
  currentModuleId: string;
  currentModuleName: string;
  currentModuleGoal: string;
  currentModulePrompt: string;
  moduleIndex: number;
  totalModules: number;
}

export interface BeginnerStepFeedback {
  what_happened: string;
  why_it_happened: string;
  what_it_means: string;
}
