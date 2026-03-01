
"""
AI Systems for CyberArena
- Opponent AI: Adaptive AI that acts as defender (when user attacks) or attacker (when user defends)
- Mentor AI: Disabled by default, only asks questions, never gives answers
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from simulation_engine import SystemState, Action, LearningMode, Phase, Hypothesis
import random


class AIDifficulty(Enum):
    RULE_BASED = "rule_based"
    ADAPTIVE = "adaptive"
    DECEPTIVE = "deceptive"


class AIPersona(Enum):
    DEFENDER = "defender"  # When user is attacker
    ATTACKER = "attacker"  # When user is defender


@dataclass
class AIBehavior:
    """AI behavior pattern"""
    persona: AIPersona
    difficulty: AIDifficulty
    aggressiveness: int = 0
    adaptation_level: int = 0
    user_patterns: Dict[str, Any] = field(default_factory=dict)
    counter_strategies: List[str] = field(default_factory=list)


class OpponentAI:
    """Adaptive AI opponent that monitors and reacts to user behavior"""
    
    def __init__(self, persona: AIPersona, difficulty: AIDifficulty):
        self.persona = persona
        self.difficulty = difficulty
        self.behavior = AIBehavior(persona, difficulty)
        self.action_history: List[Dict[str, Any]] = []
        self.user_patterns: Dict[str, Any] = {}
        self.threat_level: int = 0
        self.last_intent: str = "unknown"
    
    def evaluate_intent(self, action: Optional[Action], hypothesis_id: Optional[str] = None,
                        hypothesis_label: Optional[str] = None) -> str:
        """Evaluate user intent from action or hypothesis without exposing it"""
        if action and action.type == "hypothesis":
            self.last_intent = "test_hypothesis"
            return self.last_intent
        
        if hypothesis_id:
            self.last_intent = "test_hypothesis"
            return self.last_intent
        
        if not action:
            self.last_intent = "unknown"
            return self.last_intent
        
        action_type = (action.type or "").lower()
        if "probe" in action_type or "inspect" in action_type:
            self.last_intent = "recon"
        elif "escalate" in action_type:
            self.last_intent = "escalation"
        elif "isolate" in action_type or "restrict" in action_type or "monitor" in action_type:
            self.last_intent = "containment"
        else:
            self.last_intent = "unknown"
        
        return self.last_intent
        
    def react_to_action(self, user_action: Optional[Action], state: SystemState,
                        available_actions: Optional[List[Action]] = None,
                        intent: Optional[str] = None,
                        mode: Optional[LearningMode] = None) -> List[Dict[str, Any]]:
        """React to user action based on persona and difficulty"""
        if user_action:
            self.action_history.append({
                "action_id": user_action.id,
                "turn": len(self.action_history) + 1,
                "user_action": user_action.label
            })

        # Analyze user pattern
        if user_action:
            self._analyze_user_pattern(user_action, state)
        
        if intent:
            self.last_intent = intent

        # React based on persona and mode
        ai_actions = []
        if self.persona == AIPersona.DEFENDER:
            self._defender_reaction(user_action, state, ai_actions, mode)
        else:  # ATTACKER
            self._attacker_reaction(user_action, state, ai_actions, mode)

        # Mandatory strategy-punishment system
        if user_action:
            ai_actions.extend(self._punish_repetition(user_action, state, mode))
            
        # Update Visual State
        if state and hasattr(state, "ai_visual_state"):
            state.ai_visual_state.entropy = min(100, state.ai_visual_state.entropy + len(ai_actions) * 2)
            if self.threat_level > 70:
                state.ai_visual_state.posture = "aggressive" if self.persona.value == "attacker" else "defensive"
                state.ai_visual_state.distance = "approaching" if self.persona.value == "attacker" else "closing"
            elif self.threat_level > 30:
                state.ai_visual_state.posture = "observing"
                state.ai_visual_state.distance = "middle"
        
        return ai_actions
    
    def _analyze_user_pattern(self, action: Action, state: SystemState):
        """Analyze user behavior patterns for adaptation"""
        action_type = action.type
        
        # Track action frequency
        if action_type not in self.user_patterns:
            self.user_patterns[action_type] = {"count": 0, "success_rate": 0, "streak": 0}
        
        self.user_patterns[action_type]["count"] += 1
        self.user_patterns[action_type]["streak"] += 1
        # Reset streaks for other types
        for key in self.user_patterns:
            if key != action_type:
                self.user_patterns[key]["streak"] = 0
        
        # Update threat level
        if action.pressure_delta > 0:
            self.threat_level = min(100, self.threat_level + action.pressure_delta)
        if action.stability_delta < 0:
            self.threat_level = min(100, self.threat_level + abs(action.stability_delta))
    
    def _defender_reaction(self, user_action: Optional[Action], state: SystemState,
                           ai_actions: List[Dict[str, Any]], mode: Optional[LearningMode]):
        """Defender AI reactions (when user is attacker)"""
        # Mode-specific behavior layering
        if mode == LearningMode.GUIDED_SIMULATION:
            if state.pressure > 30:
                ai_actions.append(self._subtle_monitoring(state))
            if state.pressure > 60 and len(self.action_history) % 3 == 0:
                ai_actions.append(self._introduce_contradiction(state))
        elif mode == LearningMode.PLAYGROUND:
            if state.pressure > 40:
                ai_actions.append(self._aggressive_rate_limit(state))
            if state.pressure > 70:
                ai_actions.append(self._temporary_lockdown(state))
        elif mode == LearningMode.ATTACKER_CAMPAIGN:
            if state.pressure > 20:
                ai_actions.append(self._enable_logging(state))
            if state.pressure > 50:
                ai_actions.append(self._tighten_validation(state))
        
        if self.difficulty == AIDifficulty.RULE_BASED:
            # Simple rule-based responses
            if state.pressure > 30:
                ai_actions.append(self._enable_logging(state))
            if state.pressure > 50:
                ai_actions.append(self._block_suspicious_activity(state))
            if state.pressure > 60:
                ai_actions.append(self._deploy_emergency_patch(state))
        
        elif self.difficulty == AIDifficulty.ADAPTIVE:
            # Adapt based on user patterns
            if user_action and "probe" in user_action.type.lower():
                # User is probing - increase monitoring
                ai_actions.append(self._enable_logging(state))
                ai_actions.append(self._deploy_honeypot(state))
                ai_actions.append(self._tighten_validation(state))
                ai_actions.append(self._introduce_timing_noise(state))
            
            if user_action and "escalate" in user_action.type.lower():
                # User is escalating - block and patch
                ai_actions.append(self._block_suspicious_activity(state))
                ai_actions.append(self._deploy_emergency_patch(state))
                ai_actions.append(self._lock_sensitive_operations(state))
            
            # Learn from repeated patterns
            if self.user_patterns.get("probe", {}).get("count", 0) > 3:
                # User probes repeatedly - deploy deception
                ai_actions.append(self._deploy_deception(state))
        
        elif self.difficulty == AIDifficulty.DECEPTIVE:
            # Counter-strategic behavior
            # Let user think they're succeeding, then counter
            if state.pressure < 25 and self.threat_level > 50:
                # User thinks they're stealthy but we detected them
                ai_actions.append(self._silent_monitoring(state))
                ai_actions.append(self._prepare_counter_attack(state))
                ai_actions.append(self._schedule_countermeasure(state))
                ai_actions.append(self._partial_patch(state))
            
            # Deceptive responses
            if user_action and "probe" in user_action.type.lower():
                # Feed false information
                ai_actions.append(self._feed_false_lead(state))
                ai_actions.append(self._introduce_timing_noise(state))
                ai_actions.append(self._inject_deceptive_response(state))
            
            # Adaptive counter-strategies
            if len(self.action_history) > 5:
                # Identify user strategy and counter it
                strategy = self._identify_user_strategy()
                ai_actions.extend(self._counter_strategy(strategy, state))
                ai_actions.append(self._temporary_lockdown(state))
                ai_actions.append(self._move_attack_surface(state))
    
    def _attacker_reaction(self, user_action: Optional[Action], state: SystemState,
                           ai_actions: List[Dict[str, Any]], mode: Optional[LearningMode]):
        """Attacker AI reactions (when user is defender)"""
        # Mode-specific behavior layering
        if mode == LearningMode.DEFENDER_CAMPAIGN:
            if state.pressure < 30:
                ai_actions.append(self._stealth_probe(state))
            if state.pressure > 50:
                ai_actions.append(self._pivot_attack(state))
        elif mode == LearningMode.PLAYGROUND:
            if any(v.get("exploited") for v in state.vulnerabilities.values()):
                ai_actions.append(self._establish_persistence(state))
            if state.pressure > 60:
                ai_actions.append(self._hide_tracks(state))
        
        if self.difficulty == AIDifficulty.RULE_BASED:
            # Simple scripted attacks
            if state.pressure < 30:
                ai_actions.append(self._probe_vulnerability(state))
            if state.pressure < 50:
                ai_actions.append(self._escalate_privileges(state))
        
        elif self.difficulty == AIDifficulty.ADAPTIVE:
            # Adapt to user defenses
            if user_action and ("monitor" in user_action.type.lower() or "isolate" in user_action.type.lower()):
                # User is monitoring - change attack vector
                ai_actions.append(self._change_attack_vector(state))
                ai_actions.append(self._move_attack_surface(state))
            
            if user_action and "restrict" in user_action.type.lower():
                # User restricted something - try different approach
                ai_actions.append(self._pivot_attack(state))
                ai_actions.append(self._stealth_probe(state))
            
            # Escalate if user is slow to respond
            if len(self.action_history) > 3 and state.pressure < 25:
                ai_actions.append(self._escalate_privileges(state))
        
        elif self.difficulty == AIDifficulty.DECEPTIVE:
            # Advanced attacker behavior
            # Probe gradually, hide tracks, adapt
            if state.pressure < 15:
                # Very stealthy - continue probing
                ai_actions.append(self._stealth_probe(state))
            
            # If user detects something, hide and change approach
            if state.pressure > 40:
                ai_actions.append(self._hide_tracks(state))
                ai_actions.append(self._change_attack_vector(state))
            
            # Persistence mechanisms
            if any(v.get("exploited") for v in state.vulnerabilities.values()):
                ai_actions.append(self._establish_persistence(state))
    
    # Defender actions
    def _make_action(self, name: str, message: str, effects: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"name": name, "message": message, "effects": effects or {}}
    
    def _enable_logging(self, state: SystemState) -> Dict[str, Any]:
        """Enable enhanced logging"""
        effects = {
            "pressure_delta": 2,
            "set_monitoring": "all"
        }
        return self._make_action("enable_logging", "System-wide monitoring enabled.", effects)
    
    def _block_suspicious_activity(self, state: SystemState) -> Dict[str, Any]:
        """Block suspicious IPs/accounts"""
        effects = {
            "pressure_delta": 4,
            "add_defenses": ["ip_block"],
            "lock_action_types": [{"type": "escalate", "turns": 1}]
        }
        return self._make_action("block_suspicious_activity", "Access filters updated.", effects)
    
    def _deploy_emergency_patch(self, state: SystemState) -> Dict[str, Any]:
        """Deploy emergency patch"""
        effects = {
            "patch_vulnerabilities": {"any_active": True},
            "pressure_delta": 2
        }
        return self._make_action("deploy_emergency_patch", "Execution pathways hardened.", effects)
    
    def _deploy_honeypot(self, state: SystemState) -> Dict[str, Any]:
        """Deploy honeypot"""
        effects = {
            "add_defenses": ["honeypot"],
            "pressure_delta": 2
        }
        return self._make_action("deploy_honeypot", "Decoy endpoint activated.", effects)
    
    def _deploy_deception(self, state: SystemState) -> Dict[str, Any]:
        """Deploy deception mechanisms"""
        effects = {
            "add_defenses": ["deception"],
            "pressure_delta": 3,
            "set_conditions": {"deception_active": True}
        }
        return self._make_action("deploy_deception", "Response stream altered.", effects)
    
    def _silent_monitoring(self, state: SystemState) -> Dict[str, Any]:
        """Silent monitoring without alerting user"""
        effects = {
            "pressure_delta": 1,
            "set_monitoring": "all"
        }
        return self._make_action("silent_monitoring", "Authentication subsystem entered monitoring mode.", effects)
    
    def _prepare_counter_attack(self, state: SystemState) -> Dict[str, Any]:
        """Prepare counter-attack"""
        effects = {
            "ai_aggressiveness_delta": 10
        }
        return self._make_action("prepare_counter_attack", "Countermeasures prepared.", effects)
    
    def _feed_false_lead(self, state: SystemState) -> Dict[str, Any]:
        """Feed false information to user"""
        effects = {
            "detect_vulnerabilities": {"false_lead": True}
        }
        return self._make_action("feed_false_lead", "Anomalous signals injected into traffic.", effects)
    
    def _tighten_validation(self, state: SystemState) -> Dict[str, Any]:
        """Temporarily tighten validation rules"""
        effects = {
            "pressure_delta": 3,
            "set_conditions": {"validation_tightened": True},
            "lock_action_types": [{"type": "probe", "turns": 1}, {"type": "inspect", "turns": 1}]
        }
        return self._make_action("tighten_validation", "Input normalization policy updated.", effects)
    
    def _introduce_timing_noise(self, state: SystemState) -> Dict[str, Any]:
        """Introduce timing noise to disrupt probing"""
        effects = {
            "set_monitoring": ["web_server"],
            "pressure_delta": 1,
            "set_conditions": {"timing_jitter": True},
            "lock_action_types": [{"type": "probe", "turns": 1}]
        }
        return self._make_action("introduce_timing_noise", "Response timing jitter introduced.", effects)
    
    def _temporary_lockdown(self, state: SystemState) -> Dict[str, Any]:
        """Temporary lockdown of sensitive operations"""
        effects = {
            "harden_components": ["web_server"],
            "set_conditions": {"access_restricted": True},
            "lock_action_types": [{"type": "escalate", "turns": 2}]
        }
        return self._make_action("temporary_lockdown", "Sensitive operations restricted.", effects)
    
    def _schedule_countermeasure(self, state: SystemState) -> Dict[str, Any]:
        """Schedule delayed adaptive countermeasure"""
        effects = {
            "delayed_consequences": [
                {
                    "turn_delay": 2,
                    "description": "Adaptive filtering intensified",
                    "pressure_delta": 4
                }
            ]
        }
        return self._make_action("schedule_countermeasure", "Adaptive filtering scheduled.", effects)

    def _subtle_monitoring(self, state: SystemState) -> Dict[str, Any]:
        """Subtle monitoring increase for guided mode"""
        effects = {
            "set_monitoring": ["web_server"],
            "pressure_delta": 1
        }
        return self._make_action("subtle_monitoring", "Passive monitoring enabled on web_server.", effects)
    
    def _introduce_contradiction(self, state: SystemState) -> Dict[str, Any]:
        """Introduce contradiction to break assumptions"""
        effects = {
            "invalidate_assumptions": {"any_validated": True},
            "add_contradiction": {"description": "Observed behavior contradicts recent assumption"}
        }
        return self._make_action("introduce_contradiction", "Inconsistent behavior observed in request handling.", effects)
    
    def _aggressive_rate_limit(self, state: SystemState) -> Dict[str, Any]:
        """Aggressive rate limiting for playground"""
        effects = {
            "rate_limit": {"scope": "global", "severity": "high"},
            "lock_action_types": [{"type": "probe", "turns": 2}, {"type": "inspect", "turns": 2}]
        }
        return self._make_action("aggressive_rate_limit", "Request rate limiting enforced.", effects)
    
    def _lock_sensitive_operations(self, state: SystemState) -> Dict[str, Any]:
        """Lock high-impact operations temporarily"""
        effects = {
            "lock_action_types": [{"type": "escalate", "turns": 1}],
            "pressure_delta": 2
        }
        return self._make_action("lock_sensitive_operations", "High-impact operations gated.", effects)
    
    def _partial_patch(self, state: SystemState) -> Dict[str, Any]:
        """Partial patching to alter behavior without full mitigation"""
        effects = {
            "patch_vulnerabilities": {"any_active": True, "partial": True}
        }
        return self._make_action("partial_patch", "Behavioral filters updated.", effects)
    
    def _inject_deceptive_response(self, state: SystemState) -> Dict[str, Any]:
        """Inject deceptive responses"""
        effects = {
            "inject_deception": {"target": "web_server"}
        }
        return self._make_action("inject_deceptive_response", "Deceptive responses injected into output stream.", effects)
    
    def _move_attack_surface(self, state: SystemState) -> Dict[str, Any]:
        """Move or reshuffle attack surface"""
        effects = {
            "move_attack_surface": {"from_active": True}
        }
        return self._make_action("move_attack_surface", "Service routing changed; interface surface shifted.", effects)
    
    def _identify_user_strategy(self) -> str:
        """Identify user's strategy pattern"""
        if not self.user_patterns:
            return "unknown"
        
        # Count action types
        probe_count = self.user_patterns.get("probe", {}).get("count", 0)
        escalate_count = self.user_patterns.get("escalate", {}).get("count", 0)
        
        if probe_count > escalate_count * 2:
            return "stealth_probe"
        elif escalate_count > probe_count:
            return "aggressive_escalation"
        else:
            return "balanced"
    
    def _counter_strategy(self, strategy: str, state: SystemState) -> List[Dict[str, Any]]:
        """Counter user's identified strategy"""
        actions = []
        if strategy == "stealth_probe":
            # User is being stealthy - increase monitoring
            actions.append(self._silent_monitoring(state))
            actions.append(self._deploy_honeypot(state))
        elif strategy == "aggressive_escalation":
            # User is aggressive - block and patch
            actions.append(self._block_suspicious_activity(state))
            actions.append(self._deploy_emergency_patch(state))
        return actions

    def _punish_repetition(self, user_action: Action, state: SystemState,
                           mode: Optional[LearningMode]) -> List[Dict[str, Any]]:
        """Escalate counters when user repeats the same approach"""
        actions: List[Dict[str, Any]] = []
        action_type = user_action.type
        pattern = self.user_patterns.get(action_type, {})
        count = pattern.get("count", 0)
        streak = pattern.get("streak", 0)

        if streak < 3 and count < 5:
            return actions

        # Guided mode is subtle and delayed
        if mode == LearningMode.GUIDED_SIMULATION:
            effects = {
                "pressure_delta": 2,
                "set_conditions": {"validation_tightened": True},
                "delayed_consequences": [
                    {
                        "turn_delay": 2,
                        "description": "Interface assumptions expired",
                        "pressure_delta": 3
                    }
                ]
            }
            actions.append(self._make_action(
                "pattern_resistance",
                "Input normalization policy updated.",
                effects
            ))
            return actions

        # Escalate severity for repeated patterns
        pressure = 4 if streak < 5 else 8
        turns = 1 if streak < 5 else 2
        conditions = {"validation_tightened": True, "timing_jitter": True}
        if streak >= 5:
            conditions.update({"route_shifted": True, "access_restricted": True})

        effects = {
            "pressure_delta": pressure,
            "set_conditions": conditions,
            "lock_action_types": [{"type": action_type, "turns": turns}]
        }
        actions.append(self._make_action(
            "pattern_resistance",
            "System response adapted to repeated approach.",
            effects
        ))
        return actions
    
    # Attacker actions
    def _probe_vulnerability(self, state: SystemState) -> Dict[str, Any]:
        """Probe for vulnerabilities"""
        effects = {
            "pressure_delta": 4,
            "add_attacks": ["probing"]
        }
        return self._make_action("probe_vulnerability", "Anomalous request patterns observed.", effects)
    
    def _escalate_privileges(self, state: SystemState) -> Dict[str, Any]:
        """Attempt context elevation"""
        effects = {
            "pressure_delta": 6,
            "stability_delta": -6,
            "add_attacks": ["privilege_escalation"]
        }
        return self._make_action("escalate_privileges", "Execution boundaries stressed.", effects)
    
    def _change_attack_vector(self, state: SystemState) -> Dict[str, Any]:
        """Change attack vector"""
        effects = {
            "pressure_delta": -2,
            "add_attacks": ["vector_change"]
        }
        return self._make_action("change_attack_vector", "Attack surface shifted.", effects)
    
    def _pivot_attack(self, state: SystemState) -> Dict[str, Any]:
        """Pivot to different attack"""
        effects = {
            "pressure_delta": 5,
            "stability_delta": -4,
            "add_attacks": ["pivot"]
        }
        return self._make_action("pivot_attack", "Lateral movement observed across subsystems.", effects)
    
    def _stealth_probe(self, state: SystemState) -> Dict[str, Any]:
        """Stealthy probing"""
        effects = {
            "pressure_delta": 2,
            "add_attacks": ["stealth_probe"]
        }
        return self._make_action("stealth_probe", "Low-and-slow reconnaissance observed.", effects)
    
    def _hide_tracks(self, state: SystemState) -> Dict[str, Any]:
        """Hide attack tracks"""
        effects = {
            "pressure_delta": -4,
            "add_attacks": ["hide_tracks"]
        }
        return self._make_action("hide_tracks", "Audit trail disrupted.", effects)
    
    def _establish_persistence(self, state: SystemState) -> Dict[str, Any]:
        """Establish persistence"""
        effects = {
            "pressure_delta": 6,
            "stability_delta": -8,
            "add_attacks": ["persistence"]
        }
        return self._make_action("establish_persistence", "Resident process registered.", effects)



class MentorAI:
    """Mentor AI that only asks questions, never gives answers"""

    def __init__(self):
        self.enabled = False
        self.question_history: List[Dict[str, Any]] = []

    def enable(self):
        """Enable mentor (only on user request)"""
        self.enabled = True

    def disable(self):
        """Disable mentor"""
        self.enabled = False

    def analyze_situation(self, state: SystemState, last_action: Optional[Action] = None,
                         action_history: List[Dict[str, Any]] = None,
                         available_actions: List[Action] = None,
                         hypotheses: List[Hypothesis] = None) -> Dict[str, Any]:
        """Analyze current situation and provide contextual guidance"""
        guidance = {
            "type": "analysis",
            "situation_summary": "",
            "questions": [],
            "anomalies": [],
            "inconsistencies": [],
            "concepts": [],
            "observations": [],
            "next_steps": []
        }

        situation_parts = []
        active_conditions = [k for k, v in state.system_conditions.items() if v]
        if active_conditions:
            situation_parts.append("System posture tightening")
            guidance["observations"].append(
                "Behavioral changes are active: " + ", ".join(active_conditions)
            )
            guidance["questions"].append(
                "Which of your recent actions likely triggered these behavioral shifts?"
            )

        if state.stability < 60:
            situation_parts.append("Stability degraded")
            guidance["questions"].append(
                "Stability is drifting. What chain of actions caused the degradation?"
            )

        monitored_components = [k for k, v in state.system_components.items() if v.get("monitoring")]
        hardened_components = [k for k, v in state.system_components.items() if v.get("hardened")]
        if monitored_components:
            guidance["observations"].append(
                f"Monitoring active on {', '.join(monitored_components)}."
            )
            guidance["questions"].append(
                "How does active monitoring change your next step?"
            )

        if hardened_components:
            guidance["observations"].append(
                f"Hardening observed on {', '.join(hardened_components)}."
            )
            guidance["questions"].append(
                "What alternative approach avoids the hardened surface?"
            )

        if action_history and len(action_history) > 0:
            recent_actions = action_history[-5:]
            action_types = [a.get("action_id", "").split("_")[0] for a in recent_actions]

            if "probe" in action_types or "inspect" in action_types:
                guidance["observations"].append(
                    "You've been probing and inspecting. Patterns should be forming."
                )
                guidance["questions"].append(
                    "Based on your probing, what hypothesis can you test next?"
                )

            if "escalate" in action_types:
                guidance["observations"].append(
                    "You've escalated context. New behaviors should be visible."
                )
                guidance["questions"].append(
                    "How does the system react when you push execution boundaries?"
                )

            if any(a.get("actually_failed") for a in recent_actions):
                guidance["anomalies"].append(
                    "Some recent actions appeared successful but later failed."
                )
                guidance["questions"].append(
                    "When a result flips later, what does that say about hidden adaptation?"
                )

        if state.contradictions:
            latest = state.contradictions[-1]
            guidance["inconsistencies"].append(
                f"Your assumptions have been contradicted: {latest.get('description', 'Unexpected behavior observed')}"
            )
            guidance["questions"].append(
                "When your assumptions are wrong, how do you revise your mental model?"
            )

        if situation_parts:
            guidance["situation_summary"] = "Current situation: " + ", ".join(situation_parts) + "."
        else:
            guidance["situation_summary"] = "System is in initial state. Begin by forming hypotheses about the system's behavior."

        if len(state.user_assumptions) > 0:
            untested = [a for a in state.user_assumptions if a.get("validated") is None]
            if untested:
                guidance["questions"].append(
                    f"You have {len(untested)} untested assumption(s). How can you validate them?"
                )

        guidance["next_steps"] = self._suggest_next_steps(
            state, last_action, action_history, available_actions, hypotheses
        )

        return guidance

    def _suggest_next_steps(self, state: SystemState, last_action: Optional[Action],
                           action_history: List[Dict[str, Any]],
                           available_actions: List[Action],
                           hypotheses: List[Hypothesis]) -> List[str]:
        """Suggest what to do next based on current situation"""
        next_steps = []

        if not available_actions:
            return ["No actions available. Check if you need to form and validate a hypothesis first."]

        if hypotheses:
            untested_hypotheses = [h for h in hypotheses if not h.tested]
            if untested_hypotheses:
                next_steps.append(
                    f"You have {len(untested_hypotheses)} untested hypothesis(ies). Test one to unlock new actions."
                )

        available = [a for a in available_actions if a.available]
        locked = [a for a in available_actions if not a.available]

        if not available:
            if locked:
                next_steps.append(
                    f"You have {len(locked)} action(s) locked. Form and validate the required hypothesis to unlock them."
                )
            return next_steps if next_steps else ["No actions available at this time."]

        action_types: Dict[str, List[Action]] = {}
        for action in available:
            action_type = action.type if hasattr(action, 'type') else 'unknown'
            if action_type not in action_types:
                action_types[action_type] = []
            action_types[action_type].append(action)

        if not action_history or len(action_history) == 0:
            if 'probe' in action_types or 'inspect' in action_types:
                next_steps.append(
                    "Start by probing or inspecting to gather information and form hypotheses."
                )
            else:
                next_steps.append(
                    "Begin by exploring available actions to understand system behavior."
                )
        else:
            recent_types = [a.get("action_id", "").split("_")[0] for a in action_history[-3:]]

            if all(t in ['probe', 'inspect'] for t in recent_types):
                if 'escalate' in action_types:
                    next_steps.append(
                        "You've gathered enough information. Consider escalating your approach to test hypotheses."
                    )
                elif hypotheses and any(not h.tested for h in hypotheses):
                    next_steps.append(
                        "Based on your probing, test a hypothesis to unlock more advanced actions."
                    )

            if 'escalate' in recent_types:
                if state.pressure > 60:
                    next_steps.append(
                        "System pressure is rising. Consider isolating components or restricting execution."
                    )
                elif 'isolate' in action_types or 'restrict' in action_types:
                    next_steps.append(
                        "You've escalated. Consider defensive actions like isolating components or restricting execution."
                    )

            if state.pressure > 70:
                if 'isolate' in action_types:
                    next_steps.append(
                        "System pressure is high. Isolate components to contain the threat."
                    )
                elif 'restrict' in action_types:
                    next_steps.append(
                        "Pressure is critical. Restrict execution capabilities to limit the surface."
                    )
                elif 'monitor' in action_types:
                    next_steps.append(
                        "Pressure is high. Enable monitoring to understand system reactions."
                    )

            if state.stability < 50:
                if 'isolate' in action_types:
                    next_steps.append(
                        "Stability is compromised. Isolate affected components to prevent spread."
                    )
                elif 'restrict' in action_types:
                    next_steps.append(
                        "Stability is low. Restrict execution to prevent further degradation."
                    )

        if not next_steps:
            if 'probe' in action_types:
                next_steps.append("Continue probing to gather more information about the system.")
            elif 'inspect' in action_types:
                next_steps.append("Inspect system components to understand their behavior.")
            elif available:
                next_steps.append(f"You have {len(available)} available action(s). Consider your strategy and proceed.")

        return next_steps

    def get_guidance(self, state: SystemState, last_action: Optional[Action] = None,
                    action_history: List[Dict[str, Any]] = None,
                    available_actions: List[Action] = None,
                    hypotheses: List[Hypothesis] = None) -> Optional[Dict[str, Any]]:
        """Get mentor guidance (only questions, never answers)"""
        return self.analyze_situation(state, last_action, action_history, available_actions, hypotheses)
