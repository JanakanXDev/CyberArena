"""
Core Simulation Engine for CyberArena
Deterministic yet adaptive simulation with state machines, persistent state,
multi-vulnerability modeling, and AI behavior modules.
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid
import random
from antigravity_ai import AntigravityAI


class LearningMode(Enum):
    GUIDED_SIMULATION = "guided_simulation"
    ATTACKER_CAMPAIGN = "attacker_campaign"
    DEFENDER_CAMPAIGN = "defender_campaign"
    PLAYGROUND = "playground"


class Phase(Enum):
    """Internal engine phases - never shown to user"""
    RECON = "recon"
    EXPLOITATION = "exploitation"
    POST_EXPLOITATION = "post_exploitation"
    DEFENSE = "defense"
    INCIDENT_RESPONSE = "incident_response"
    RECOVERY = "recovery"


@dataclass
class AIVisualState:
    """Represents the visual and behavioral state of the AI entity"""
    posture: str = "observing"
    distance: str = "distant"
    entropy: int = 0

@dataclass
class SystemState:
    """Persistent system state across simulation"""
    pressure: int = 0
    stability: int = 100
    ai_aggressiveness: int = 0
    ai_visual_state: AIVisualState = field(default_factory=AIVisualState)
    phase: Phase = Phase.RECON
    vulnerabilities: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    active_defenses: List[str] = field(default_factory=list)
    active_attacks: List[str] = field(default_factory=list)
    system_components: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    system_conditions: Dict[str, Any] = field(default_factory=dict)
    system_events: List[Dict[str, Any]] = field(default_factory=list)
    user_assumptions: List[Dict[str, Any]] = field(default_factory=list)
    action_history: List[Dict[str, Any]] = field(default_factory=list)
    delayed_consequences: List[Dict[str, Any]] = field(default_factory=list)
    contradictions: List[Dict[str, Any]] = field(default_factory=list)
    learning_data: Dict[str, Any] = field(default_factory=dict)
    session_status: str = "active"  # active | collapsed
    collapse_reason: Optional[str] = None
    collapse_message: Optional[str] = None
    antigravity_feedback: Optional[Dict[str, Any]] = None
    
    # Terminal States
    scenario_state: str = "active"  # "active", "victory", "defeat"
    win_conditions: List[Dict[str, Any]] = field(default_factory=list)
    loss_conditions: List[Dict[str, Any]] = field(default_factory=list)
    max_phase: int = 5
    strategic_debrief: Optional[Dict[str, Any]] = None


@dataclass
class Hypothesis:
    """User hypothesis about system behavior"""
    id: str
    label: str
    description: str
    timestamp: datetime
    tested: bool = False
    validated: Optional[bool] = None
    evidence: List[str] = field(default_factory=list)


@dataclass
class Action:
    """Hypothesis-based action (no exploit/fix names)"""
    id: str
    label: str  # Intent/strategy, e.g., "Probe input validation boundaries"
    description: str  # What it does conceptually
    type: str  # "probe", "escalate", "isolate", "monitor", etc.
    hypothesis_required: Optional[str] = None
    immediate_effect: Dict[str, Any] = field(default_factory=dict)
    delayed_effects: List[Dict[str, Any]] = field(default_factory=list)
    pressure_delta: int = 0
    stability_delta: int = 0
    available: bool = True
    visible: bool = True
    lock_until_turn: int = 0


@dataclass
class DelayedConsequence:
    """Consequence that triggers later"""
    id: str
    trigger_action_id: str
    trigger_turn: int
    effect: Callable[[SystemState], None]
    description: str
    executed: bool = False


@dataclass
class Contradiction:
    """Forces system behavior to break user assumptions"""
    id: str
    assumption_id: str
    trigger_condition: Callable[[SystemState], bool]
    effect: Callable[[SystemState], None]
    description: str
    triggered: bool = False


class SimulationEngine:
    """Core deterministic simulation engine"""
    
    def __init__(self, mode: LearningMode, difficulty: str, scenario_id: str):
        self.mode = mode
        self.difficulty = difficulty
        self.scenario_id = scenario_id
        self.state = SystemState()
        self.ai_opponent = None


@dataclass
class DelayedConsequence:
    """Consequence that triggers later"""
    id: str
    trigger_action_id: str
    trigger_turn: int
    effect: Callable[[SystemState], None]
    description: str
    executed: bool = False


@dataclass
class Contradiction:
    """Forces system behavior to break user assumptions"""
    id: str
    assumption_id: str
    trigger_condition: Callable[[SystemState], bool]
    effect: Callable[[SystemState], None]
    description: str
    triggered: bool = False


class SimulationEngine:
    """Core deterministic simulation engine"""
    
    def __init__(self, mode: LearningMode, difficulty: str, scenario_id: str):
        self.mode = mode
        self.difficulty = difficulty
        self.scenario_id = scenario_id
        self.state = SystemState()
        self.turn_count = 0
        self.hypotheses: List[Hypothesis] = []
        self.available_actions: List[Action] = []
        self.delayed_consequences: List[DelayedConsequence] = []
        self.contradictions: List[Contradiction] = []
        self.ai_opponent = None  # Will be set by AI module
        self.mentor_enabled = False
        self._hypotheses_config: Dict[str, Any] = {}  # Store hypothesis configs
        self.antigravity = AntigravityAI()
        
    def initialize(self, scenario_config: Dict[str, Any]):
        """Initialize simulation from scenario configuration"""
        # Set initial state
        initial_state = scenario_config.get("initial_state", {})
        self.state.pressure = initial_state.get("pressure", 0)
        self.state.stability = initial_state.get("stability", 100)
        
        # Initialize vulnerabilities
        vulnerabilities = scenario_config.get("vulnerabilities", {})
        for vuln_id, vuln_data in vulnerabilities.items():
            self.state.vulnerabilities[vuln_id] = {
                "active": vuln_data.get("active", True),
                "exploited": False,
                "detected": False,
                "severity": vuln_data.get("severity", "medium"),
                "interactions": vuln_data.get("interactions", []),
                "false_lead": vuln_data.get("false_lead", False)
            }

        # Initialize system conditions
        self.state.system_conditions = {
            "errors_suppressed": False,
            "timing_jitter": False,
            "route_shifted": False,
            "validation_tightened": False,
            "access_restricted": False,
            "deception_active": False
        }
        
        # Initialize system components
        components = scenario_config.get("system_components", {})
        for comp_id, comp_data in components.items():
            self.state.system_components[comp_id] = {
                "status": comp_data.get("status", "operational"),
                "monitoring": comp_data.get("monitoring", False),
                "hardened": comp_data.get("hardened", False),
                "signals": comp_data.get("signals", [])
            }

        # Apply initial pressure effects
        self._apply_pressure_effects()
        
        # Initialize empty actions and hypotheses (populated via configure_session)
        self.available_actions = []
        self._hypotheses_config = {}
        
        # Initialize delayed consequences
        delayed_config = scenario_config.get("delayed_consequences", [])
        for dc_config in delayed_config:
            self.delayed_consequences.append(self._create_delayed_consequence(dc_config))
        
        # Initialize contradictions
        contradictions_config = scenario_config.get("contradictions", [])
        for contr_config in contradictions_config:
            self.contradictions.append(self._create_contradiction(contr_config))
            
    def configure_session(self, role: str, focus_component: str):
        """Configure session with role and component focus after initial setup"""
        from scenario_system import get_focused_content
        
        # Get focused content
        focused = get_focused_content(self.scenario_id, self.mode, role, focus_component)
        
        # Initialize actions from focused content
        actions_config = focused.get("actions", [])
        self.available_actions = [self._parse_action(a) for a in actions_config]
        
        # Initialize hypotheses from focused content
        hypotheses_config = focused.get("hypotheses", [])
        self._hypotheses_config = {h["id"]: h for h in hypotheses_config}
        
        # Clear existing created hypotheses
        self.hypotheses = []
        self.state.user_assumptions = []
        
        # Spawn AI Entity visual state based on role
        if role == "attacker":
            self.state.ai_visual_state.posture = "defensive"
            self.state.ai_visual_state.distance = "distant"
        elif role == "defender":
            self.state.ai_visual_state.posture = "aggressive"
            self.state.ai_visual_state.distance = "approaching"
        else:
            self.state.ai_visual_state.posture = "observing"
            self.state.ai_visual_state.distance = "distant"
        # Set Terminal State Objectives
        self.state.win_conditions = focused.get("win_conditions", [])
        self.state.loss_conditions = focused.get("loss_conditions", [])
        self.state.max_phase = focused.get("max_phase", 5)
        self.state.scenario_state = "active"
        self.state.strategic_debrief = None
            
        self._record_system_event(f"Session configured for {role} focusing on {focus_component}.", "info")
    
    def _parse_action(self, action_config: Dict[str, Any]) -> Action:
        """Parse action from configuration"""
        # Actions are available by default unless they require a hypothesis
        # If hypothesis_required is set, available starts as False
        hypothesis_required = action_config.get("hypothesis_required")
        base_available = action_config.get("available", True)
        if hypothesis_required:
            # Action requires hypothesis, so it's not available until hypothesis is validated
            base_available = False
        
        return Action(
            id=action_config["id"],
            label=action_config["label"],
            description=action_config.get("description", ""),
            type=action_config.get("type", "decision"),
            hypothesis_required=hypothesis_required,
            immediate_effect=action_config.get("immediate_effect", {}),
            delayed_effects=action_config.get("delayed_effects", []),
            pressure_delta=action_config.get("pressure_delta", 0),
            stability_delta=action_config.get("stability_delta", 0),
            available=base_available,
            visible=action_config.get("visible", True)
        )
    
    def _create_delayed_consequence(self, config: Dict[str, Any]) -> DelayedConsequence:
        """Create delayed consequence from configuration"""
        def effect_wrapper(state: SystemState):
            # Apply delayed effect
            if "pressure_delta" in config:
                state.pressure = max(0, min(100, state.pressure + config["pressure_delta"]))
            if "stability_delta" in config:
                state.stability = max(0, min(100, state.stability + config["stability_delta"]))
            if "vulnerability_trigger" in config:
                vuln_id = config["vulnerability_trigger"]
                if vuln_id in state.vulnerabilities:
                    state.vulnerabilities[vuln_id]["exploited"] = True
        
        return DelayedConsequence(
            id=config.get("id", str(uuid.uuid4())),
            trigger_action_id=config["trigger_action_id"],
            trigger_turn=config["trigger_turn"],
            effect=effect_wrapper,
            description=config.get("description", "")
        )
    
    def _create_contradiction(self, config: Dict[str, Any]) -> Contradiction:
        """Create contradiction from configuration"""
        def condition_wrapper(state: SystemState) -> bool:
            # Check if condition is met
            condition_type = config.get("condition_type")
            if condition_type == "assumption_validated":
                assumption_id = config.get("assumption_id")
                return any(a.get("id") == assumption_id and a.get("validated") == True 
                          for a in state.user_assumptions)
            elif condition_type == "action_taken":
                action_id = config.get("action_id")
                return any(a.get("action_id") == action_id for a in state.action_history)
            return False
        
        def effect_wrapper(state: SystemState):
            # Break user assumption
            if "reveal_vulnerability" in config:
                vuln_id = config["reveal_vulnerability"]
                if vuln_id in state.vulnerabilities:
                    state.vulnerabilities[vuln_id]["detected"] = True
            if "trigger_failure" in config:
                failure = config["trigger_failure"]
                if failure == "previous_success_fails":
                    # Mark previous successful action as failed
                    if state.action_history:
                        state.action_history[-1]["actually_failed"] = True
        
        return Contradiction(
            id=config.get("id", str(uuid.uuid4())),
            assumption_id=config.get("assumption_id", ""),
            trigger_condition=condition_wrapper,
            effect=effect_wrapper,
            description=config.get("description", "")
        )
    
    def process_action(self, action_id: str, user_input: Optional[str] = None) -> (Dict[str, Any], List[Dict[str, str]]):
        """Process user action and return new state and AI actions"""
        if self.state.session_status == "collapsed":
            return self._get_state_dict(), []
        self.turn_count += 1
        ai_actions = []
        
        # Find action
        action = next((a for a in self.available_actions if a.id == action_id), None)
        if not action:
            if action_id == "tactical_fallback":
                action = Action(
                    id="tactical_fallback",
                    label="Observe AI Behavior & Wait",
                    description="No active vectors available. Observe enemy actions.",
                    type="monitor"
                )
            else:
                print(f"Warning: Action '{action_id}' not found in available actions")
                print(f"Available action IDs: {[a.id for a in self.available_actions]}")
                return self._get_state_dict(), ai_actions
        
        # Check availability (considering hypothesis requirements)
        if action.hypothesis_required:
            hyp = next((h for h in self.hypotheses if h.id == action.hypothesis_required), None)
            if not hyp or not hyp.validated:
                print(f"Warning: Action '{action_id}' requires validated hypothesis '{action.hypothesis_required}'")
                return self._get_state_dict(), ai_actions
        
        if action.lock_until_turn >= self.turn_count:
            print(f"Warning: Action '{action_id}' is temporarily locked by AI")
            return self._get_state_dict(), ai_actions
        
        if not action.available:
            print(f"Warning: Action '{action_id}' is marked as unavailable")
            return self._get_state_dict(), ai_actions
        
        # Record action
        self.state.action_history.append({
            "action_id": action_id,
            "action_type": action.type,
            "turn": self.turn_count,
            "timestamp": datetime.now().isoformat(),
            "actually_failed": False
        })
        
        # Apply immediate effects
        self._apply_immediate_effects(action)
        
        # Check for contradictions
        self._check_contradictions()
        
        # Schedule delayed effects
        self._schedule_delayed_effects(action)
        
        # Process delayed consequences
        self._process_delayed_consequences()
        
        # Apply pressure-based system behavior and strategy punishment
        self._apply_strategy_punishment(action)
        self._apply_pressure_effects()
        
        # Check for collapse conditions
        self._check_system_collapse()
        
        # Check Terminal State Objectives
        self._evaluate_terminal_state()
        
        # Update phase based on state
        self._update_phase()
        
        # Antigravity Observation
        self.antigravity.observe(self.state, action, {"failed": self.state.action_history[-1].get("actually_failed")})
        
        # Check for specific failure feedback
        if self.state.action_history[-1].get("actually_failed"):
            feedback = self.antigravity.analyze_failure("action_failed", {"action": action})
            if feedback:
                self.state.antigravity_feedback = feedback
                self._record_system_event("Antigravity analysis generated.", "info")
        
        return self._get_state_dict(), ai_actions

    def _evaluate_terminal_state(self):
        """Evaluate mode-specific win and loss conditions"""
        if self.state.scenario_state != "active":
            return
            
        # Check Win Conditions
        won = False
        for cond in self.state.win_conditions:
            if cond.get("type") == "hypothesis_validated":
                # Check if all hypotheses configured with 'correct=True' are validated
                target = cond.get("target")
                if target == "all_core_hypotheses":
                    core_hyps = [h_id for h_id, hd in self._hypotheses_config.items() if hd.get("correct")]
                    if core_hyps and all(any(h.id == ch and h.validated for h in self.hypotheses) for ch in core_hyps):
                        won = True
                        break
            elif cond.get("type") == "objective_achieved":
                if any(cond.get("target") in a.get("action_type", "") and not a.get("actually_failed") for a in self.state.action_history):
                    won = True
                    break
            elif cond.get("type") == "integrity_restored":
                if self.state.stability >= cond.get("target", 100) and self.state.pressure == 0:
                    won = True
                    break
                    
        # Check Loss Conditions
        lost = False
        for cond in self.state.loss_conditions:
            if cond.get("type") == "pressure_threshold":
                if self.state.pressure >= cond.get("target", 100):
                    lost = True
                    break
            elif cond.get("type") == "detection_threshold":
                if self.state.pressure >= 90: # proxy for critical detection
                    lost = True
                    break
            elif cond.get("type") == "critical_asset_lost":
                if self.state.stability <= 10: # proxy for asset loss
                    lost = True
                    break
                    
        if won:
            self.state.scenario_state = "victory"
            self._generate_strategic_debrief()
        elif lost:
            self.state.scenario_state = "defeat"
            self._generate_strategic_debrief()
            
    def _generate_strategic_debrief(self):
        """Generate debrief summary when scenario resolves"""
        outcome = self.state.scenario_state
        
        summary = f"Operator achieved {outcome.upper()} on turn {self.turn_count}."
        
        # Analyze performance
        validated = sum(1 for h in self.hypotheses if h.validated)
        invalidated = sum(1 for h in self.hypotheses if h.tested and not h.validated)
        
        self.state.strategic_debrief = {
            "outcome": outcome,
            "turns": self.turn_count,
            "final_pressure": self.state.pressure,
            "final_stability": self.state.stability,
            "final_ai_entropy": self.state.ai_visual_state.entropy,
            "ai_end_posture": self.state.ai_visual_state.posture,
            "hypotheses_validated": validated,
            "hypotheses_invalidated": invalidated,
            "summary": summary
        }
        
        level = "info" if outcome == "victory" else "error"
        self._record_system_event(f"Simulation Terminated: {outcome.upper()} | Debrief Generated", level)
    
    def _record_system_event(self, message: str, level: str = "info"):
        """Record a system-visible event for the current turn"""
        self.state.system_events.append({
            "turn": self.turn_count,
            "message": message,
            "level": level
        })

    def _check_system_collapse(self):
        """Check if the system has collapsed"""
        if self.state.session_status == "collapsed":
            return
        if self.state.stability <= 0:
            self.state.session_status = "collapsed"
            self.state.collapse_reason = "stability_failure"
            self.state.collapse_message = "Operational stability failed. Access pathways collapsed."
            self._record_system_event("Operational stability failed. Access pathways collapsed.", "error")
            
            # Antigravity Collapse Analysis
            feedback = self.antigravity.analyze_failure("collapse", {})
            if feedback:
                self.state.antigravity_feedback = feedback

    def _apply_strategy_punishment(self, action: Action):
        """Apply escalating counters when a strategy is repeated"""
        if not action:
            return
        recent = [a for a in self.state.action_history[-6:]]
        if not recent:
            return

        # Count repeats by action type and exact action id
        same_type_count = sum(1 for a in recent if a.get("action_type") == action.type)
        same_id_count = sum(1 for a in recent if a.get("action_id") == action.id)

        pressure_bump = 0
        if same_id_count >= 3:
            pressure_bump = 8
            self._record_system_event("Repetitive interaction pattern detected. Routing hardened.", "warning")
            self._set_condition("route_shifted", True)
            self._set_condition("validation_tightened", True)
            self._lock_action_type(action.type, turns=2)
        elif same_type_count >= 3:
            pressure_bump = 4
            self._record_system_event("Repeated approach observed. Input handling tightened.", "warning")
            self._set_condition("validation_tightened", True)
            self._lock_action_type(action.type, turns=1)

        if pressure_bump > 0:
            self.state.pressure = max(0, min(100, self.state.pressure + pressure_bump))

    def _set_condition(self, key: str, value: bool):
        """Set a system condition and record transitions"""
        previous = self.state.system_conditions.get(key)
        self.state.system_conditions[key] = value
        if previous is None or previous == value:
            return
        if value:
            self._record_system_event(self._condition_message(key, True))
        else:
            self._record_system_event(self._condition_message(key, False))

    def _condition_message(self, key: str, enabled: bool) -> str:
        on_map = {
            "errors_suppressed": "Error details suppressed.",
            "timing_jitter": "Response timing jitter introduced.",
            "route_shifted": "Service routes shifted.",
            "validation_tightened": "Input normalization policy tightened.",
            "access_restricted": "Access scope restricted.",
            "deception_active": "Deceptive responses activated."
        }
        off_map = {
            "errors_suppressed": "Error details restored to baseline.",
            "timing_jitter": "Response timing stabilized.",
            "route_shifted": "Service routes stabilized.",
            "validation_tightened": "Input normalization policy relaxed.",
            "access_restricted": "Access scope restored.",
            "deception_active": "Deceptive responses withdrawn."
        }
        return on_map.get(key, "System posture changed.") if enabled else off_map.get(key, "System posture normalized.")

    def _apply_pressure_effects(self):
        """Apply system behavior changes based on pressure level"""
        pressure = self.state.pressure
        if pressure >= 80:
            self._set_condition("errors_suppressed", True)
            self._set_condition("timing_jitter", True)
            self._set_condition("route_shifted", True)
            self._set_condition("validation_tightened", True)
            self._set_condition("access_restricted", True)
            self._set_condition("deception_active", True)
        elif pressure >= 50:
            self._set_condition("errors_suppressed", True)
            self._set_condition("timing_jitter", True)
            self._set_condition("validation_tightened", True)
            self._set_condition("route_shifted", False)
            self._set_condition("access_restricted", False)
            self._set_condition("deception_active", False)
        elif pressure >= 25:
            self._set_condition("errors_suppressed", False)
            self._set_condition("timing_jitter", True)
            self._set_condition("validation_tightened", False)
            self._set_condition("route_shifted", False)
            self._set_condition("access_restricted", False)
            self._set_condition("deception_active", False)
        else:
            self._set_condition("errors_suppressed", False)
            self._set_condition("timing_jitter", False)
            self._set_condition("validation_tightened", False)
            self._set_condition("route_shifted", False)
            self._set_condition("access_restricted", False)
            self._set_condition("deception_active", False)

        # Reflect conditions into component signals
        for comp in self.state.system_components.values():
            signals = set(comp.get("signals", []))
            signals.update({"errors_suppressed"} if self.state.system_conditions.get("errors_suppressed") else set())
            signals.update({"timing_jitter"} if self.state.system_conditions.get("timing_jitter") else set())
            signals.update({"route_shifted"} if self.state.system_conditions.get("route_shifted") else set())
            signals.update({"validation_tightened"} if self.state.system_conditions.get("validation_tightened") else set())
            signals.update({"access_restricted"} if self.state.system_conditions.get("access_restricted") else set())
            signals.update({"deception_active"} if self.state.system_conditions.get("deception_active") else set())
            # Remove signals that are no longer active
            for s in list(signals):
                if s in self.state.system_conditions and not self.state.system_conditions.get(s, False):
                    signals.discard(s)
            comp["signals"] = sorted(signals)

    def _lock_action_type(self, action_type: str, turns: int):
        if not action_type or turns <= 0:
            return
        for action in self.available_actions:
            if action.type == action_type:
                action.lock_until_turn = max(action.lock_until_turn, self.turn_count + turns)
    
    def _apply_immediate_effects(self, action: Action):
        """Apply immediate effects of action"""
        # Update metrics (cap at 0-100)
        self.state.pressure = max(0, min(100, self.state.pressure + action.pressure_delta))
        self.state.stability = max(0, min(100, self.state.stability + action.stability_delta))
        
        # Apply immediate effects from config
        immediate = action.immediate_effect
        if "vulnerability_exploited" in immediate:
            vuln_id = immediate["vulnerability_exploited"]
            if vuln_id in self.state.vulnerabilities:
                self.state.vulnerabilities[vuln_id]["exploited"] = True
        
        if "component_modified" in immediate:
            comp_id = immediate["component_modified"]
            if comp_id in self.state.system_components:
                mod = immediate.get("modification", {})
                self.state.system_components[comp_id].update(mod)
                self._record_system_event(f"{comp_id} configuration changed.", "info")
    
    def _check_contradictions(self):
        """Check and trigger contradictions"""
        for contradiction in self.contradictions:
            if not contradiction.triggered and contradiction.trigger_condition(self.state):
                contradiction.effect(self.state)
                contradiction.triggered = True
                # Log contradiction
                self.state.contradictions.append({
                    "id": contradiction.id,
                    "description": contradiction.description,
                    "turn": self.turn_count
                })
                
                # Antigravity Contradiction Analysis
                feedback = self.antigravity.analyze_failure("contradiction", {"contradicted_assumption": contradiction.assumption_id})
                if feedback:
                    self.state.antigravity_feedback = feedback
    
    def _schedule_delayed_effects(self, action: Action):
        """Schedule delayed effects for action"""
        for delayed_effect in action.delayed_effects:
            turn_delay = delayed_effect.get("turn_delay", 1)
            dc = DelayedConsequence(
                id=str(uuid.uuid4()),
                trigger_action_id=action.id,
                trigger_turn=self.turn_count + turn_delay,
                effect=lambda s, de=delayed_effect: self._apply_delayed_effect(s, de),
                description=delayed_effect.get("description", "")
            )
            self.delayed_consequences.append(dc)
    
    def _apply_delayed_effect(self, state: SystemState, effect_config: Dict[str, Any]):
        """Apply a delayed effect"""
        if "pressure_delta" in effect_config:
            state.pressure = max(0, min(100, state.pressure + effect_config["pressure_delta"]))
        if "stability_delta" in effect_config:
            state.stability = max(0, min(100, state.stability + effect_config["stability_delta"]))
        if "vulnerability_trigger" in effect_config:
            vuln_id = effect_config["vulnerability_trigger"]
            if vuln_id in state.vulnerabilities:
                state.vulnerabilities[vuln_id]["exploited"] = True
        if effect_config.get("mark_previous_failed") and state.action_history:
            state.action_history[-1]["actually_failed"] = True
    
    def _process_delayed_consequences(self):
        """Process delayed consequences that should trigger now"""
        for dc in self.delayed_consequences:
            if not dc.executed and dc.trigger_turn <= self.turn_count:
                dc.effect(self.state)
                dc.executed = True
    
    def _update_phase(self):
        """Update internal phase based on state (never shown to user)"""
        # Phase transitions based on state, not user actions
        if self.state.pressure > 70:
            self.state.phase = Phase.INCIDENT_RESPONSE
        elif any(v["exploited"] for v in self.state.vulnerabilities.values()):
            if self.state.phase == Phase.RECON:
                self.state.phase = Phase.EXPLOITATION
            elif self.state.phase == Phase.EXPLOITATION:
                self.state.phase = Phase.POST_EXPLOITATION
        elif self.mode == LearningMode.DEFENDER_CAMPAIGN:
            if self.state.pressure > 30:
                self.state.phase = Phase.DEFENSE
    
    def add_hypothesis(self, hypothesis: Hypothesis):
        """Add user hypothesis"""
        self.hypotheses.append(hypothesis)
        self.state.user_assumptions.append({
            "id": hypothesis.id,
            "label": hypothesis.label,
            "timestamp": hypothesis.timestamp.isoformat(),
            "validated": None
        })
    
    def evaluate_hypothesis(self, hypothesis_id: str) -> bool:
        """Dynamically evaluate hypothesis validation based on current state"""
        hyp_config = self._hypotheses_config.get(hypothesis_id, {})
        base_correct = hyp_config.get("correct", False)
        
        # Determine actual validity dynamically
        validated = base_correct
        
        # Component State Modifier: hyp_error_oracle (wrong hypothesis) can become
        # conditionally true if web_server monitoring was triggered (see issue #2)
        if hypothesis_id == "hyp_error_oracle":
            web_server = self.state.system_components.get("web_server", {})
            if web_server.get("monitoring"):
                validated = True
            
        return validated

    def validate_hypothesis(self, hypothesis_id: str, _client_validated: bool = False):
        """Validate a hypothesis dynamically, ignoring client boolean"""
        hypothesis = next((h for h in self.hypotheses if h.id == hypothesis_id), None)
        if hypothesis:
            # Perform server-side dynamic validation
            validated = self.evaluate_hypothesis(hypothesis_id)
            
            hypothesis.tested = True
            hypothesis.validated = validated
            
            # Update assumption tracking
            for assumption in self.state.user_assumptions:
                if assumption["id"] == hypothesis_id:
                    assumption["validated"] = validated
                    
            # Trigger AI Reaction on Hypothesis Validation
            if getattr(self, "ai_opponent", None):
                # Validation attempts always increase entropy/pressure
                self.state.ai_visual_state.entropy = min(100, self.state.ai_visual_state.entropy + 10)
                if validated:
                    # Successful validation often prompts a defense reaction
                    self.state.ai_visual_state.posture = "defensive"
                    self.state.ai_visual_state.distance = "close"
                    self._record_system_event(f"AI Entity reacted to hypothesis validation.", "warning")
                else:
                    self.state.ai_visual_state.posture = "observing"
                    self._record_system_event(f"Hypothesis check yielded no usable vectors. AI monitoring continues.", "info")
                    
            # Unlock actions if needed
            if validated:
                for action in self.available_actions:
                    if action.hypothesis_required == hypothesis_id:
                        action.available = True
    
    def _get_state_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for API response"""
        # Filter visible actions
        visible_actions = [a for a in self.available_actions if a.visible]
        
        # Freeze actions if scenario has ended
        if self.state.scenario_state != "active":
            visible_actions = []
            
        action_dicts = []
        for a in visible_actions:
            # Check if action requires hypothesis
            available = a.available  # Start with action's base availability
            # Temporarily locked by AI counter-actions (only lock if FUTURE turn)
            if a.lock_until_turn > self.turn_count:
                available = False
            
            # If action requires hypothesis, check if it's validated
            if a.hypothesis_required:
                hyp = next((h for h in self.hypotheses if h.id == a.hypothesis_required), None)
                if hyp and hyp.validated is True:
                    available = True  # Hypothesis validated, action available
                elif hyp and hyp.validated is False:
                    available = False  # Hypothesis invalidated, action unavailable
                else:
                    available = False  # Hypothesis not tested yet, action unavailable
            # If no hypothesis required, use the action's base availability (should be True)
            
            action_dicts.append({
                "id": a.id,
                "label": a.label,
                "description": a.description,
                "type": a.type,
                "available": available
            })
            
        # Fallback Logic: Prevent Dead States
        if (not action_dicts or all(not a["available"] for a in action_dicts)) and self.state.scenario_state == "active":
            action_dicts.append({
                "id": "tactical_fallback",
                "label": "Observe AI Behavior & Wait",
                "description": "No active vectors available. Observe enemy actions.",
                "type": "monitor",
                "available": True
            })
        
        # Get hypotheses - combine created ones with config ones
        hypotheses_list = []
        for h in self.hypotheses:
            hyp_config = self._hypotheses_config.get(h.id, {})
            # Pick the right explanation based on the validation result
            if h.tested and h.validated is not None:
                if h.validated:
                    explanation = hyp_config.get("why_correct", "")
                else:
                    explanation = hyp_config.get("why_wrong", "")
            else:
                explanation = None
            hypotheses_list.append({
                "id": h.id,
                "label": h.label,
                "description": h.description,
                "tested": h.tested,
                "validated": h.validated,
                "explanation": explanation
            })
        
        # Add hypotheses from config that haven't been created yet
        for hyp_id, hyp_config in self._hypotheses_config.items():
            if not any(h.id == hyp_id for h in self.hypotheses):
                hypotheses_list.append({
                    "id": hyp_config.get("id", hyp_id),
                    "label": hyp_config.get("label", ""),
                    "description": hyp_config.get("description", ""),
                    "tested": False,
                    "validated": None,
                    "explanation": None
                })
        
        return {
            "mode": self.mode.value,
            "scenario_id": self.scenario_id,
            "turn_count": self.turn_count,
            "pressure": self.state.pressure,
            "stability": self.state.stability,
            "ai_aggressiveness": self.state.ai_aggressiveness,
            "ai_visual_state": {
                "posture": self.state.ai_visual_state.posture,
                "distance": self.state.ai_visual_state.distance,
                "entropy": self.state.ai_visual_state.entropy
            },
            "available_actions": action_dicts,
            "hypotheses": hypotheses_list,
            "user_assumptions": self.state.user_assumptions,
            "system_components": self.state.system_components,
            "system_conditions": self.state.system_conditions,
            "vulnerabilities": {k: {
                "active": v.get("active", False),
                "exploited": v.get("exploited", False),
                "detected": v.get("detected", False)
            } for k, v in self.state.vulnerabilities.items()},
            "action_history": [
                {
                    "action_id": a.action_id if hasattr(a, "action_id") else getattr(a, "id", str(a)),
                    "action_label": next((cfg.get("label", a.action_id) for cfg in self._actions_config if cfg.get("id") == a.action_id), a.action_id) if hasattr(a, "action_id") else str(a),
                    "turn": getattr(a, "turn_count", getattr(a, "turn", 0)),
                    "timestamp": a.timestamp.strftime("%H:%M:%S") if hasattr(a, "timestamp") and hasattr(a.timestamp, "strftime") else "",
                    "actually_failed": getattr(a, "actually_failed", False)
                } for a in self.state.action_history[-10:]
            ],
            "contradictions": self.state.contradictions,
            "session_status": self.state.session_status,
            "collapse_reason": self.state.collapse_reason,
            "collapse_reason": self.state.collapse_reason,
            "collapse_message": self.state.collapse_message,
            "system_events": self.state.system_events[-10:],
            "antigravity_feedback": self.state.antigravity_feedback,
            "scenario_state": self.state.scenario_state,
            "strategic_debrief": self.state.strategic_debrief
        }

    def _apply_ai_action_effects(self, ai_action: Dict[str, Any]):
        """Apply AI counter-action effects to simulation state"""
        effects = ai_action.get("effects", {}) if isinstance(ai_action, dict) else {}
        if not effects:
            return
        
        # Metric deltas
        if "pressure_delta" in effects:
            self.state.pressure = max(0, min(100, self.state.pressure + effects["pressure_delta"]))
        if "stability_delta" in effects:
            self.state.stability = max(0, min(100, self.state.stability + effects["stability_delta"]))
        if "ai_aggressiveness_delta" in effects:
            self.state.ai_aggressiveness = max(0, min(100, self.state.ai_aggressiveness + effects["ai_aggressiveness_delta"]))
        
        # Component state changes
        set_monitoring = effects.get("set_monitoring")
        if set_monitoring:
            if set_monitoring == "all":
                for comp_id in self.state.system_components:
                    self.state.system_components[comp_id]["monitoring"] = True
            elif isinstance(set_monitoring, list):
                for comp_id in set_monitoring:
                    if comp_id in self.state.system_components:
                        self.state.system_components[comp_id]["monitoring"] = True
        
        harden_components = effects.get("harden_components", [])
        for comp_id in harden_components:
            if comp_id in self.state.system_components:
                self.state.system_components[comp_id]["hardened"] = True
        
        # Defenses / attacks markers
        for defense in effects.get("add_defenses", []):
            if defense not in self.state.active_defenses:
                self.state.active_defenses.append(defense)
        for attack in effects.get("add_attacks", []):
            if attack not in self.state.active_attacks:
                self.state.active_attacks.append(attack)
        
        # Rate limiting indicators
        rate_limit = effects.get("rate_limit")
        if rate_limit:
            if "rate_limit" not in self.state.active_defenses:
                self.state.active_defenses.append("rate_limit")
        
        # Patch vulnerabilities
        patch_config = effects.get("patch_vulnerabilities")
        if patch_config:
            partial = patch_config.get("partial", False)
            if patch_config.get("any_active"):
                for vuln_id, vuln in self.state.vulnerabilities.items():
                    if vuln.get("active") and not vuln.get("patched"):
                        vuln["patched"] = True
                        if not partial:
                            vuln["active"] = False
                        break
            for vuln_id in patch_config.get("ids", []):
                if vuln_id in self.state.vulnerabilities:
                    self.state.vulnerabilities[vuln_id]["patched"] = True
                    if not partial:
                        self.state.vulnerabilities[vuln_id]["active"] = False
        
        # Detect vulnerabilities (false leads / bait)
        detect_config = effects.get("detect_vulnerabilities")
        if detect_config:
            if detect_config.get("false_lead"):
                for vuln_id, vuln in self.state.vulnerabilities.items():
                    if vuln.get("false_lead"):
                        vuln["detected"] = True
                        break
            for vuln_id in detect_config.get("ids", []):
                if vuln_id in self.state.vulnerabilities:
                    self.state.vulnerabilities[vuln_id]["detected"] = True
        
        # Invalidate assumptions (break user model)
        invalidate = effects.get("invalidate_assumptions")
        if invalidate:
            if invalidate.get("any_validated"):
                for assumption in self.state.user_assumptions:
                    if assumption.get("validated") is True:
                        assumption["validated"] = False
                        break
            for assumption_id in invalidate.get("ids", []):
                for assumption in self.state.user_assumptions:
                    if assumption.get("id") == assumption_id:
                        assumption["validated"] = False
        
        # Add contradiction log
        contradiction = effects.get("add_contradiction")
        if contradiction:
            self.state.contradictions.append({
                "id": contradiction.get("id", str(uuid.uuid4())),
                "description": contradiction.get("description", "Unexpected system behavior observed"),
                "turn": self.turn_count
            })
        
        # Deception markers
        if effects.get("inject_deception"):
            if "deception" not in self.state.active_defenses:
                self.state.active_defenses.append("deception")
            self._set_condition("deception_active", True)

        # System condition overrides
        conditions = effects.get("set_conditions")
        if conditions and isinstance(conditions, dict):
            for key, value in conditions.items():
                self._set_condition(key, bool(value))
        
        # Move attack surface (toggle active vuln)
        move_surface = effects.get("move_attack_surface")
        if move_surface:
            if move_surface.get("from_active"):
                active_vulns = [v_id for v_id, v in self.state.vulnerabilities.items() if v.get("active")]
                if active_vulns:
                    disable_id = random.choice(active_vulns)
                    self.state.vulnerabilities[disable_id]["active"] = False
                    inactive_vulns = [v_id for v_id, v in self.state.vulnerabilities.items() if not v.get("active")]
                    if inactive_vulns:
                        enable_id = random.choice(inactive_vulns)
                        self.state.vulnerabilities[enable_id]["active"] = True
            self._set_condition("route_shifted", True)
        
        # Action locks (availability changes)
        for lock in effects.get("lock_action_types", []):
            lock_type = lock.get("type")
            turns = max(0, int(lock.get("turns", 0)))
            if not lock_type or turns <= 0:
                continue
            for action in self.available_actions:
                if action.type == lock_type:
                    action.lock_until_turn = max(action.lock_until_turn, self.turn_count + turns)
        
        for lock in effects.get("lock_actions", []):
            lock_id = lock.get("id")
            turns = max(0, int(lock.get("turns", 0)))
            if not lock_id or turns <= 0:
                continue
            action = next((a for a in self.available_actions if a.id == lock_id), None)
            if action:
                action.lock_until_turn = max(action.lock_until_turn, self.turn_count + turns)
        
        # Schedule delayed consequences
        for dc in effects.get("delayed_consequences", []):
            turn_delay = dc.get("turn_delay", 1)
            delayed_effect = {k: v for k, v in dc.items() if k != "turn_delay"}
            self.delayed_consequences.append(
                DelayedConsequence(
                    id=str(uuid.uuid4()),
                    trigger_action_id=ai_action.get("name", "ai_counter"),
                    trigger_turn=self.turn_count + turn_delay,
                    effect=lambda s, de=delayed_effect: self._apply_delayed_effect(s, de),
                    description=dc.get("description", "AI countermeasure activated")
                )
            )

    def apply_ai_actions(self, ai_actions: List[Dict[str, Any]]):
        """Apply a list of AI counter-actions to the current state"""
        for ai_action in ai_actions or []:
            self._apply_ai_action_effects(ai_action)
        # Reflect AI-driven pressure changes into behavior
        self._apply_pressure_effects()
        self._check_system_collapse()
