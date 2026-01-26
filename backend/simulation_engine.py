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
class SystemState:
    """Persistent system state across simulation"""
    risk_score: int = 0
    detection_level: int = 0
    integrity: int = 100
    ai_aggressiveness: int = 0
    phase: Phase = Phase.RECON
    vulnerabilities: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    active_defenses: List[str] = field(default_factory=list)
    active_attacks: List[str] = field(default_factory=list)
    system_components: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    user_assumptions: List[Dict[str, Any]] = field(default_factory=list)
    action_history: List[Dict[str, Any]] = field(default_factory=list)
    delayed_consequences: List[Dict[str, Any]] = field(default_factory=list)
    contradictions: List[Dict[str, Any]] = field(default_factory=list)
    learning_data: Dict[str, Any] = field(default_factory=dict)


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
    risk_delta: int = 0
    detection_delta: int = 0
    integrity_delta: int = 0
    available: bool = True
    visible: bool = True


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
        
    def initialize(self, scenario_config: Dict[str, Any]):
        """Initialize simulation from scenario configuration"""
        # Set initial state
        initial_state = scenario_config.get("initial_state", {})
        self.state.risk_score = initial_state.get("risk", 0)
        self.state.detection_level = initial_state.get("detection", 0)
        self.state.integrity = initial_state.get("integrity", 100)
        
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
        
        # Initialize system components
        components = scenario_config.get("system_components", {})
        for comp_id, comp_data in components.items():
            self.state.system_components[comp_id] = {
                "status": comp_data.get("status", "operational"),
                "monitoring": comp_data.get("monitoring", False),
                "hardened": comp_data.get("hardened", False)
            }
        
        # Initialize actions
        actions_config = scenario_config.get("actions", [])
        self.available_actions = [self._parse_action(a) for a in actions_config]
        
        # Initialize hypotheses from config (but don't create Hypothesis objects yet)
        # They will be created when user tests them
        hypotheses_config = scenario_config.get("hypotheses", [])
        # Store config for later use
        self._hypotheses_config = {h["id"]: h for h in hypotheses_config}
        
        # Initialize delayed consequences
        delayed_config = scenario_config.get("delayed_consequences", [])
        for dc_config in delayed_config:
            self.delayed_consequences.append(self._create_delayed_consequence(dc_config))
        
        # Initialize contradictions
        contradictions_config = scenario_config.get("contradictions", [])
        for contr_config in contradictions_config:
            self.contradictions.append(self._create_contradiction(contr_config))
    
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
            risk_delta=action_config.get("risk_delta", 0),
            detection_delta=action_config.get("detection_delta", 0),
            integrity_delta=action_config.get("integrity_delta", 0),
            available=base_available,
            visible=action_config.get("visible", True)
        )
    
    def _create_delayed_consequence(self, config: Dict[str, Any]) -> DelayedConsequence:
        """Create delayed consequence from configuration"""
        def effect_wrapper(state: SystemState):
            # Apply delayed effect
            if "risk_delta" in config:
                state.risk_score = max(0, min(100, state.risk_score + config["risk_delta"]))
            if "detection_delta" in config:
                state.detection_level = max(0, min(100, state.detection_level + config["detection_delta"]))
            if "integrity_delta" in config:
                state.integrity = max(0, min(100, state.integrity + config["integrity_delta"]))
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
    
    def process_action(self, action_id: str, user_input: Optional[str] = None) -> Dict[str, Any]:
        """Process user action and return new state"""
        self.turn_count += 1
        
        # Find action
        action = next((a for a in self.available_actions if a.id == action_id), None)
        if not action:
            print(f"Warning: Action '{action_id}' not found in available actions")
            print(f"Available action IDs: {[a.id for a in self.available_actions]}")
            return self._get_state_dict()
        
        # Check availability (considering hypothesis requirements)
        if action.hypothesis_required:
            hyp = next((h for h in self.hypotheses if h.id == action.hypothesis_required), None)
            if not hyp or not hyp.validated:
                print(f"Warning: Action '{action_id}' requires validated hypothesis '{action.hypothesis_required}'")
                return self._get_state_dict()
        
        if not action.available:
            print(f"Warning: Action '{action_id}' is marked as unavailable")
            return self._get_state_dict()
        
        # Record action
        self.state.action_history.append({
            "action_id": action_id,
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
        
        # Update AI opponent (if active)
        if self.ai_opponent:
            self.ai_opponent.react_to_action(action, self.state)
        
        # Update phase based on state
        self._update_phase()
        
        return self._get_state_dict()
    
    def _apply_immediate_effects(self, action: Action):
        """Apply immediate effects of action"""
        # Update metrics
        self.state.risk_score = max(0, min(100, self.state.risk_score + action.risk_delta))
        self.state.detection_level = max(0, min(100, self.state.detection_level + action.detection_delta))
        self.state.integrity = max(0, min(100, self.state.integrity + action.integrity_delta))
        
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
        if "risk_delta" in effect_config:
            state.risk_score = max(0, min(100, state.risk_score + effect_config["risk_delta"]))
        if "detection_delta" in effect_config:
            state.detection_level = max(0, min(100, state.detection_level + effect_config["detection_delta"]))
        if "integrity_delta" in effect_config:
            state.integrity = max(0, min(100, state.integrity + effect_config["integrity_delta"]))
        if "vulnerability_trigger" in effect_config:
            vuln_id = effect_config["vulnerability_trigger"]
            if vuln_id in state.vulnerabilities:
                state.vulnerabilities[vuln_id]["exploited"] = True
    
    def _process_delayed_consequences(self):
        """Process delayed consequences that should trigger now"""
        for dc in self.delayed_consequences:
            if not dc.executed and dc.trigger_turn <= self.turn_count:
                dc.effect(self.state)
                dc.executed = True
    
    def _update_phase(self):
        """Update internal phase based on state (never shown to user)"""
        # Phase transitions based on state, not user actions
        if self.state.detection_level > 70:
            self.state.phase = Phase.INCIDENT_RESPONSE
        elif any(v["exploited"] for v in self.state.vulnerabilities.values()):
            if self.state.phase == Phase.RECON:
                self.state.phase = Phase.EXPLOITATION
            elif self.state.phase == Phase.EXPLOITATION:
                self.state.phase = Phase.POST_EXPLOITATION
        elif self.mode == LearningMode.DEFENDER_CAMPAIGN:
            if self.state.detection_level > 30:
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
    
    def validate_hypothesis(self, hypothesis_id: str, validated: bool):
        """Validate a hypothesis"""
        hypothesis = next((h for h in self.hypotheses if h.id == hypothesis_id), None)
        if hypothesis:
            hypothesis.tested = True
            hypothesis.validated = validated
            # Update assumption
            for assumption in self.state.user_assumptions:
                if assumption["id"] == hypothesis_id:
                    assumption["validated"] = validated
            # Unlock actions if needed
            if validated:
                for action in self.available_actions:
                    if action.hypothesis_required == hypothesis_id:
                        action.available = True
    
    def _get_state_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for API response"""
        # Filter visible actions
        visible_actions = [a for a in self.available_actions if a.visible]
        action_dicts = []
        for a in visible_actions:
            # Check if action requires hypothesis
            available = a.available  # Start with action's base availability
            
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
        
        # Get hypotheses - combine created ones with config ones
        hypotheses_list = [{
            "id": h.id,
            "label": h.label,
            "description": h.description,
            "tested": h.tested,
            "validated": h.validated
        } for h in self.hypotheses]
        
        # Add hypotheses from config that haven't been created yet
        for hyp_id, hyp_config in self._hypotheses_config.items():
            if not any(h.id == hyp_id for h in self.hypotheses):
                hypotheses_list.append({
                    "id": hyp_config.get("id", hyp_id),
                    "label": hyp_config.get("label", ""),
                    "description": hyp_config.get("description", ""),
                    "tested": False,
                    "validated": None
                })
        
        return {
            "mode": self.mode.value,
            "scenario_id": self.scenario_id,
            "turn_count": self.turn_count,
            "risk_score": self.state.risk_score,
            "detection_level": self.state.detection_level,
            "integrity": self.state.integrity,
            "ai_aggressiveness": self.state.ai_aggressiveness,
            "available_actions": action_dicts,
            "hypotheses": hypotheses_list,
            "user_assumptions": self.state.user_assumptions,
            "system_components": self.state.system_components,
            "vulnerabilities": {k: {
                "active": v.get("active", False),
                "exploited": v.get("exploited", False),
                "detected": v.get("detected", False)
            } for k, v in self.state.vulnerabilities.items()},
            "action_history": self.state.action_history[-10:],  # Last 10 actions
            "contradictions": self.state.contradictions
        }
