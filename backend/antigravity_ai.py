"""
Antigravity AI: Post-Exposure Cognitive Analysis
Specializes in analyzing player assumptions, reasoning patterns, and strategic behavior.
Does NOT execute gameplay logic or act as an opponent.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class ReasoningModel:
    """Shadow model of player's likely reasoning"""
    focus_metric: str = "unknown"  # e.g., "pressure", "stability"
    suspected_strategy: str = "unknown"  # e.g., "brute_force", "stealth"
    tunnel_vision_detected: bool = False
    repetition_count: int = 0
    last_action_type: str = None
    ignored_signals: List[str] = field(default_factory=list)
    false_assumptions: List[str] = field(default_factory=list)

class AntigravityAI:
    def __init__(self):
        self.reasoning_model = ReasoningModel()
        self.history: List[Dict[str, Any]] = []
        self.feedback_buffer: List[Dict[str, Any]] = []

    def observe(self, state: Any, action: Any, result: Dict[str, Any]) -> None:
        """Observe player action and system response to update reasoning model"""
        if not action:
            return

        # 1. Track Repetition (Strategy Spamming)
        if hasattr(action, 'type') and action.type == self.reasoning_model.last_action_type:
            self.reasoning_model.repetition_count += 1
        else:
            self.reasoning_model.repetition_count = 0
            if hasattr(action, 'type'):
                self.reasoning_model.last_action_type = action.type

        # 2. Detect Tunnel Vision (Ignoring side-channel signals)
        # If system has signals (e.g., 'timing_jitter') but player keeps spamming 'probe'
        system_signals = self._extract_signals(state)
        if system_signals and self.reasoning_model.repetition_count > 2:
            self.reasoning_model.tunnel_vision_detected = True
            for signal in system_signals:
                if signal not in self.reasoning_model.ignored_signals:
                    self.reasoning_model.ignored_signals.append(signal)
        
        # 3. Infer Focus
        if action.pressure_delta > 0:
            self.reasoning_model.focus_metric = "pressure"
        elif action.stability_delta < 0:
            self.reasoning_model.focus_metric = "stability"

        self.history.append({
            "turn": state.turn_count if hasattr(state, 'turn_count') else 0,
            "action": action.label if hasattr(action, 'label') else "unknown",
            "result_summary": self._summarize_result(result),
            "reasoning_snapshot": str(self.reasoning_model)
        })

    def analyze_failure(self, failure_type: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze a failure event and generate cognitive feedback.
        Only returns feedback if the failure implies a reasoning error.
        """
        
        feedback = {
            "type": "antigravity_insight",
            "tone": "neutral",
            "trigger": failure_type,
            "insight": "",
            "reasoning_gap": ""
        }

        if failure_type == "contradiction":
            # Player assumption was explicitly contradicted
            assumption = context.get("contradicted_assumption", "unknown")
            feedback["insight"] = f"The system behavior contradicted the assumption: '{assumption}'."
            feedback["reasoning_gap"] = "Relied on a static model of system rules while the system state had shifted."
            return feedback

        elif failure_type == "action_failed":
            # Action failed (e.g. locked or blocked)
            if self.reasoning_model.tunnel_vision_detected:
                signals = ", ".join(self.reasoning_model.ignored_signals)
                feedback["insight"] = f"Action failed because environmental signals were ignored: [{signals}]."
                feedback["reasoning_gap"] = "Tunnel vision observed. Strategy extraction persisted despite clear warning signals."
                self.reasoning_model.tunnel_vision_detected = False # Reset after reporting
                return feedback
            
            if self.reasoning_model.repetition_count > 3:
                feedback["insight"] = "System adapted to neutralize the repeated strategy."
                feedback["reasoning_gap"] = "Pattern formed a predictable signature. Variation was required but not provided."
                return feedback

        elif failure_type == "collapse":
            feedback["insight"] = "Total system collapse occurred due to unchecked instability."
            feedback["reasoning_gap"] = "Focus on objective completion overrode system health monitoring."
            return feedback

        return None

    def _extract_signals(self, state: Any) -> List[str]:
        """Extract active signals from system state"""
        signals = []
        if hasattr(state, 'system_conditions'):
            for k, v in state.system_conditions.items():
                if v: signals.append(k)
        return signals

    def _summarize_result(self, result: Dict[str, Any]) -> str:
        # Simplistic summary for internal tracking
        return "success" if not result.get("failed") else "fail"
