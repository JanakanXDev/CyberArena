
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
        
    def react_to_action(self, user_action: Action, state: SystemState):
        """React to user action based on persona and difficulty"""
        self.action_history.append({
            "action_id": user_action.id,
            "turn": len(self.action_history) + 1,
            "user_action": user_action.label
        })
        
        # Analyze user pattern
        self._analyze_user_pattern(user_action, state)
        
        # React based on persona
        if self.persona == AIPersona.DEFENDER:
            self._defender_reaction(user_action, state)
        else:  # ATTACKER
            self._attacker_reaction(user_action, state)
    
    def _analyze_user_pattern(self, action: Action, state: SystemState):
        """Analyze user behavior patterns for adaptation"""
        action_type = action.type
        
        # Track action frequency
        if action_type not in self.user_patterns:
            self.user_patterns[action_type] = {"count": 0, "success_rate": 0}
        
        self.user_patterns[action_type]["count"] += 1
        
        # Update threat level
        if action.risk_delta > 0:
            self.threat_level = min(100, self.threat_level + action.risk_delta)
        if action.detection_delta > 0:
            self.threat_level = min(100, self.threat_level + action.detection_delta)
    
    def _defender_reaction(self, user_action: Action, state: SystemState):
        """Defender AI reactions (when user is attacker)"""
        if self.difficulty == AIDifficulty.RULE_BASED:
            # Simple rule-based responses
            if state.detection_level > 30:
                self._enable_logging(state)
            if state.detection_level > 50:
                self._block_suspicious_activity(state)
            if state.risk_score > 60:
                self._deploy_emergency_patch(state)
        
        elif self.difficulty == AIDifficulty.ADAPTIVE:
            # Adapt based on user patterns
            if "probe" in user_action.type.lower():
                # User is probing - increase monitoring
                self._enable_logging(state)
                self._deploy_honeypot(state)
            
            if "escalate" in user_action.type.lower():
                # User is escalating - block and patch
                self._block_suspicious_activity(state)
                self._deploy_emergency_patch(state)
            
            # Learn from repeated patterns
            if self.user_patterns.get("probe", {}).get("count", 0) > 3:
                # User probes repeatedly - deploy deception
                self._deploy_deception(state)
        
        elif self.difficulty == AIDifficulty.DECEPTIVE:
            # Counter-strategic behavior
            # Let user think they're succeeding, then counter
            if state.detection_level < 20 and self.threat_level > 50:
                # User thinks they're stealthy but we detected them
                self._silent_monitoring(state)
                self._prepare_counter_attack(state)
            
            # Deceptive responses
            if "probe" in user_action.type.lower():
                # Feed false information
                self._feed_false_lead(state)
            
            # Adaptive counter-strategies
            if len(self.action_history) > 5:
                # Identify user strategy and counter it
                strategy = self._identify_user_strategy()
                self._counter_strategy(strategy, state)
    
    def _attacker_reaction(self, user_action: Action, state: SystemState):
        """Attacker AI reactions (when user is defender)"""
        if self.difficulty == AIDifficulty.RULE_BASED:
            # Simple scripted attacks
            if state.detection_level < 30:
                self._probe_vulnerability(state)
            if state.detection_level < 50:
                self._escalate_privileges(state)
        
        elif self.difficulty == AIDifficulty.ADAPTIVE:
            # Adapt to user defenses
            if "monitor" in user_action.type.lower() or "isolate" in user_action.type.lower():
                # User is monitoring - change attack vector
                self._change_attack_vector(state)
            
            if "restrict" in user_action.type.lower():
                # User restricted something - try different approach
                self._pivot_attack(state)
            
            # Escalate if user is slow to respond
            if len(self.action_history) > 3 and state.detection_level < 20:
                self._escalate_privileges(state)
        
        elif self.difficulty == AIDifficulty.DECEPTIVE:
            # Advanced attacker behavior
            # Probe gradually, hide tracks, adapt
            if state.detection_level < 10:
                # Very stealthy - continue probing
                self._stealth_probe(state)
            
            # If user detects something, hide and change approach
            if state.detection_level > 40:
                self._hide_tracks(state)
                self._change_attack_vector(state)
            
            # Persistence mechanisms
            if any(v.get("exploited") for v in state.vulnerabilities.values()):
                self._establish_persistence(state)
    
    # Defender actions
    def _enable_logging(self, state: SystemState):
        """Enable enhanced logging"""
        state.detection_level = min(100, state.detection_level + 5)
        for comp_id in state.system_components:
            state.system_components[comp_id]["monitoring"] = True
    
    def _block_suspicious_activity(self, state: SystemState):
        """Block suspicious IPs/accounts"""
        state.detection_level = min(100, state.detection_level + 10)
        state.active_defenses.append("ip_block")
    
    def _deploy_emergency_patch(self, state: SystemState):
        """Deploy emergency patch"""
        # Patch one vulnerability
        for vuln_id, vuln in state.vulnerabilities.items():
            if vuln.get("active") and not vuln.get("patched"):
                vuln["patched"] = True
                vuln["active"] = False
                break
    
    def _deploy_honeypot(self, state: SystemState):
        """Deploy honeypot"""
        state.active_defenses.append("honeypot")
        state.detection_level = min(100, state.detection_level + 3)
    
    def _deploy_deception(self, state: SystemState):
        """Deploy deception mechanisms"""
        state.active_defenses.append("deception")
        state.detection_level = min(100, state.detection_level + 5)
    
    def _silent_monitoring(self, state: SystemState):
        """Silent monitoring without alerting user"""
        state.detection_level = min(100, state.detection_level + 2)
        for comp_id in state.system_components:
            state.system_components[comp_id]["monitoring"] = True
    
    def _prepare_counter_attack(self, state: SystemState):
        """Prepare counter-attack"""
        state.ai_aggressiveness = min(100, state.ai_aggressiveness + 10)
    
    def _feed_false_lead(self, state: SystemState):
        """Feed false information to user"""
        # Mark a false lead vulnerability as detected
        for vuln_id, vuln in state.vulnerabilities.items():
            if vuln.get("false_lead"):
                vuln["detected"] = True
                break
    
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
    
    def _counter_strategy(self, strategy: str, state: SystemState):
        """Counter user's identified strategy"""
        if strategy == "stealth_probe":
            # User is being stealthy - increase monitoring
            self._silent_monitoring(state)
            self._deploy_honeypot(state)
        elif strategy == "aggressive_escalation":
            # User is aggressive - block and patch
            self._block_suspicious_activity(state)
            self._deploy_emergency_patch(state)
    
    # Attacker actions
    def _probe_vulnerability(self, state: SystemState):
        """Probe for vulnerabilities"""
        state.risk_score = min(100, state.risk_score + 5)
        state.active_attacks.append("probing")
    
    def _escalate_privileges(self, state: SystemState):
        """Attempt privilege escalation"""
        state.risk_score = min(100, state.risk_score + 10)
        state.active_attacks.append("privilege_escalation")
    
    def _change_attack_vector(self, state: SystemState):
        """Change attack vector"""
        state.active_attacks.append("vector_change")
        # Reduce detection temporarily
        state.detection_level = max(0, state.detection_level - 5)
    
    def _pivot_attack(self, state: SystemState):
        """Pivot to different attack"""
        state.active_attacks.append("pivot")
        state.risk_score = min(100, state.risk_score + 8)
    
    def _stealth_probe(self, state: SystemState):
        """Stealthy probing"""
        state.risk_score = min(100, state.risk_score + 3)
        state.detection_level = max(0, state.detection_level - 2)
        state.active_attacks.append("stealth_probe")
    
    def _hide_tracks(self, state: SystemState):
        """Hide attack tracks"""
        state.detection_level = max(0, state.detection_level - 10)
        state.active_attacks.append("hide_tracks")
    
    def _establish_persistence(self, state: SystemState):
        """Establish persistence"""
        state.risk_score = min(100, state.risk_score + 15)
        state.active_attacks.append("persistence")


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
        
        # Analyze current situation
        situation_parts = []
        
        # Risk analysis
        if state.risk_score > 70:
            situation_parts.append("High risk detected")
            guidance["questions"].append(
                "What actions have led to this elevated risk level? Are there patterns you notice?"
            )
        elif state.risk_score > 40:
            situation_parts.append("Moderate risk present")
            guidance["questions"].append(
                "What factors are contributing to the current risk level?"
            )
        else:
            situation_parts.append("Low risk state")
            guidance["questions"].append(
                "What strategies are keeping the risk low? Are there hidden threats?"
            )
        
        # Detection analysis
        if state.detection_level > 70:
            situation_parts.append("High detection level")
            guidance["questions"].append(
                "The system is highly alert. What might have triggered this? How can you operate under increased scrutiny?"
            )
            guidance["concepts"].append("Stealth and evasion techniques")
        elif state.detection_level > 40:
            situation_parts.append("Moderate detection")
            guidance["questions"].append(
                "Detection is increasing. What patterns in your actions might be causing this?"
            )
        else:
            situation_parts.append("Low detection")
            guidance["questions"].append(
                "You're operating under the radar. Is this sustainable? What might change?"
            )
        
        # Integrity analysis
        if state.integrity < 50:
            situation_parts.append("System integrity compromised")
            guidance["questions"].append(
                "System integrity is low. What happened? Can this be recovered, and should it be?"
            )
            guidance["concepts"].append("System recovery and incident response")
        elif state.integrity < 80:
            situation_parts.append("System integrity degraded")
            guidance["questions"].append(
                "System integrity is declining. What's causing this degradation?"
            )
        
        # Vulnerability analysis
        exploited_vulns = [k for k, v in state.vulnerabilities.items() if v.get("exploited")]
        detected_vulns = [k for k, v in state.vulnerabilities.items() if v.get("detected")]
        active_vulns = [k for k, v in state.vulnerabilities.items() if v.get("active") and not v.get("exploited")]
        
        if exploited_vulns:
            situation_parts.append(f"{len(exploited_vulns)} vulnerability(ies) exploited")
            guidance["questions"].append(
                f"You've exploited {len(exploited_vulns)} vulnerability(ies). What are the implications? How do they interact?"
            )
        
        if detected_vulns:
            situation_parts.append(f"{len(detected_vulns)} vulnerability(ies) detected")
            guidance["observations"].append(
                f"System has detected {len(detected_vulns)} vulnerability(ies). This changes the threat landscape."
            )
        
        if active_vulns:
            guidance["questions"].append(
                f"There are {len(active_vulns)} active vulnerability(ies) you haven't exploited. What's your strategy?"
            )
        
        # Action history analysis
        if action_history and len(action_history) > 0:
            recent_actions = action_history[-5:]
            action_types = [a.get("action_id", "").split("_")[0] for a in recent_actions]
            
            if "probe" in action_types or "inspect" in action_types:
                guidance["observations"].append(
                    "You've been probing and inspecting. What have you learned? What patterns emerge?"
                )
                guidance["questions"].append(
                    "Based on your probing, what hypotheses can you form about the system's behavior?"
                )
            
            if "escalate" in action_types:
                guidance["observations"].append(
                    "You've escalated privileges or context. What new capabilities does this give you?"
                )
                guidance["questions"].append(
                    "With escalated access, what new attack surfaces or defense options are available?"
                )
            
            if any(a.get("actually_failed") for a in recent_actions):
                guidance["anomalies"].append(
                    "Some of your recent actions appeared successful but later failed. What might explain this discrepancy?"
                )
                guidance["questions"].append(
                    "When actions fail unexpectedly, what does that tell you about the system's true state?"
                )
        
        # Contradiction analysis
        if state.contradictions:
            latest = state.contradictions[-1]
            guidance["inconsistencies"].append(
                f"Your assumptions have been contradicted: {latest.get('description', 'Something unexpected happened')}"
            )
            guidance["questions"].append(
                "When your assumptions are wrong, how do you revise your mental model? What new information do you need?"
            )
        
        # AI opponent analysis
        if state.ai_aggressiveness > 0:
            situation_parts.append("AI opponent active")
            guidance["observations"].append(
                f"AI opponent aggressiveness is at {state.ai_aggressiveness}%. The opponent is actively responding."
            )
            guidance["questions"].append(
                "How is the AI opponent adapting to your actions? What patterns can you identify in their responses?"
            )
        
        # Component analysis
        monitored_components = [k for k, v in state.system_components.items() if v.get("monitoring")]
        hardened_components = [k for k, v in state.system_components.items() if v.get("hardened")]
        
        if monitored_components:
            guidance["observations"].append(
                f"Components {', '.join(monitored_components)} are being monitored. This affects your operational security."
            )
            guidance["questions"].append(
                "How does active monitoring change your approach? What actions become riskier?"
            )
        
        if hardened_components:
            guidance["observations"].append(
                f"Components {', '.join(hardened_components)} have been hardened. Some attack vectors may be closed."
            )
            guidance["questions"].append(
                "With hardened components, what alternative approaches might work?"
            )
        
        # Build situation summary
        if situation_parts:
            guidance["situation_summary"] = "Current situation: " + ", ".join(situation_parts) + "."
        else:
            guidance["situation_summary"] = "System is in initial state. Begin by forming hypotheses about the system's behavior."
        
        # Add strategic questions based on mode/context
        if state.detection_level > state.risk_score:
            guidance["questions"].append(
                "Detection is higher than risk. What does this tell you about the system's priorities?"
            )
        
        if len(state.user_assumptions) > 0:
            untested = [a for a in state.user_assumptions if a.get("validated") is None]
            if untested:
                guidance["questions"].append(
                    f"You have {len(untested)} untested assumption(s). How can you validate them?"
                )
        
        # NEXT STEPS GUIDANCE - What should you do now?
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
        
        # Check if there are untested hypotheses
        if hypotheses:
            untested_hypotheses = [h for h in hypotheses if not h.tested]
            if untested_hypotheses:
                next_steps.append(
                    f"💡 You have {len(untested_hypotheses)} untested hypothesis(ies). Consider testing one to unlock new actions."
                )
        
        # Check available actions
        available = [a for a in available_actions if a.available]
        locked = [a for a in available_actions if not a.available]
        
        if not available:
            if locked:
                next_steps.append(
                    f"🔒 You have {len(locked)} action(s) locked. Form and validate the required hypothesis to unlock them."
                )
            return next_steps if next_steps else ["No actions available at this time."]
        
        # Analyze what actions are available
        action_types = {}
        for action in available:
            action_type = action.type if hasattr(action, 'type') else 'unknown'
            if action_type not in action_types:
                action_types[action_type] = []
            action_types[action_type].append(action)
        
        # Suggest based on current state
        if not action_history or len(action_history) == 0:
            # Just started - suggest probing
            if 'probe' in action_types or 'inspect' in action_types:
                next_steps.append(
                    "🎯 Start by probing or inspecting the system to gather information and form hypotheses."
                )
            else:
                next_steps.append(
                    "🎯 Begin by exploring available actions to understand the system's behavior."
                )
        else:
            # Analyze recent actions
            recent_types = [a.get("action_id", "").split("_")[0] for a in action_history[-3:]]
            
            # If only probing, suggest next step
            if all(t in ['probe', 'inspect'] for t in recent_types):
                if 'escalate' in action_types:
                    next_steps.append(
                        "⚡ You've gathered enough information. Consider escalating your approach to test your hypotheses."
                    )
                elif hypotheses and any(not h.tested for h in hypotheses):
                    next_steps.append(
                        "🧪 Based on your probing, test a hypothesis to unlock more advanced actions."
                    )
            
            # If escalated, suggest what's next
            if 'escalate' in recent_types:
                if state.detection_level > 50:
                    next_steps.append(
                        "⚠️ Detection is high. Consider isolating components or restricting execution to reduce risk."
                    )
                elif 'isolate' in action_types or 'restrict' in action_types:
                    next_steps.append(
                        "🛡️ You've escalated. Now consider defensive actions like isolating components or restricting execution."
                    )
            
            # If detection is high, suggest defensive actions
            if state.detection_level > 60:
                if 'isolate' in action_types:
                    next_steps.append(
                        "🔒 High detection detected. Consider isolating compromised components to contain the threat."
                    )
                elif 'restrict' in action_types:
                    next_steps.append(
                        "🚫 Detection is critical. Restrict execution capabilities to limit the attack surface."
                    )
                elif 'monitor' in action_types:
                    next_steps.append(
                        "👁️ Detection is high. Enable monitoring to understand what's happening in the system."
                    )
            
            # If risk is high, suggest mitigation
            if state.risk_score > 70:
                if 'isolate' in action_types:
                    next_steps.append(
                        "⚠️ Risk is critical. Isolate vulnerable components immediately to prevent further damage."
                    )
                elif 'restrict' in action_types:
                    next_steps.append(
                        "🚨 High risk detected. Restrict system capabilities to reduce the attack surface."
                    )
            
            # If integrity is low, suggest recovery
            if state.integrity < 50:
                if 'isolate' in action_types:
                    next_steps.append(
                        "💔 System integrity is compromised. Isolate affected components to prevent spread."
                    )
                elif 'restrict' in action_types:
                    next_steps.append(
                        "🔧 System integrity is low. Restrict execution to prevent further degradation."
                    )
            
            # If vulnerabilities are exploited but not detected
            exploited = [k for k, v in state.vulnerabilities.items() if v.get("exploited")]
            if exploited and state.detection_level < 30:
                next_steps.append(
                    f"🎯 You've exploited {len(exploited)} vulnerability(ies) without detection. Consider your next move carefully."
                )
        
        # If no specific guidance, provide general next step
        if not next_steps:
            if 'probe' in action_types:
                next_steps.append("🔍 Continue probing to gather more information about the system.")
            elif 'inspect' in action_types:
                next_steps.append("🔎 Inspect system components to understand their behavior.")
            elif available:
                next_steps.append(f"✅ You have {len(available)} available action(s). Consider your strategy and proceed.")
        
        return next_steps
    
    def get_guidance(self, state: SystemState, last_action: Optional[Action] = None, 
                    action_history: List[Dict[str, Any]] = None,
                    available_actions: List[Action] = None,
                    hypotheses: List[Hypothesis] = None) -> Optional[Dict[str, Any]]:
        """Get mentor guidance (only questions, never answers)"""
        # Always provide guidance when requested (analyze current situation)
        return self.analyze_situation(state, last_action, action_history, available_actions, hypotheses)
