export type EventType = 'INFO' | 'SUCCESS' | 'WARNING' | 'FAILURE' | 'LESSON';

export interface GameEvent {
  id: string;
  type: EventType;
  title: string;
  description: string;
  impact?: string;
}

export interface GameState {
  phase: 'INIT' | 'RECON' | 'ATTACK' | 'DEFENSE' | 'RESOLUTION' | 'COMPLETE';
  attack_stage: string;
  defense_level: string;
  discovered_vectors: string[];
  exposed_assets: string[];
  risk_score: number;
  turn_count: number;
  is_compromised: boolean;
  is_secured: boolean;
  allowed_actions: string[];
  events: GameEvent[];
}

export interface ActionDefinition {
  id: string;
  label: string;
  description: string;
  category: 'diagnosis' | 'exploit' | 'remediation' | 'hypothesis';
  dangerous?: boolean; // For visual hints if we want, or hidden
}
