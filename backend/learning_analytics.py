"""
Learning Analytics and Adaptive Curriculum System
Tracks user assumptions, strategies, failures, and concepts to recommend scenarios
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from simulation_engine import SystemState, Hypothesis


@dataclass
class LearningSession:
    """Data from a single learning session"""
    session_id: str
    mode: str
    scenario_id: str
    duration: int  # seconds
    assumptions: List[Dict[str, Any]] = field(default_factory=list)
    strategies: List[str] = field(default_factory=list)
    failures: List[Dict[str, Any]] = field(default_factory=list)
    concepts_touched: List[str] = field(default_factory=list)
    revisions: List[Dict[str, Any]] = field(default_factory=list)
    final_state: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class LearningAnalytics:
    """Tracks and analyzes learning patterns"""

    def __init__(self):
        self.sessions: List[LearningSession] = []
        self.user_profile: Dict[str, Any] = {
            "weak_areas": [],
            "strong_areas": [],
            "preferred_strategies": [],
            "common_mistakes": []
        }

    def record_session(self, session: LearningSession):
        """Record a learning session"""
        self.sessions.append(session)
        self._update_user_profile(session)

    def _update_user_profile(self, session: LearningSession):
        """Update user profile based on session"""
        for failure in session.failures:
            concept = failure.get("concept")
            if concept and concept not in self.user_profile["weak_areas"]:
                self.user_profile["weak_areas"].append(concept)

        for strategy in session.strategies:
            if strategy not in self.user_profile["preferred_strategies"]:
                self.user_profile["preferred_strategies"].append(strategy)

        for assumption in session.assumptions:
            if not assumption.get("validated", True):
                mistake = {
                    "type": "incorrect_assumption",
                    "assumption": assumption.get("label"),
                    "concept": assumption.get("concept")
                }
                if mistake not in self.user_profile["common_mistakes"]:
                    self.user_profile["common_mistakes"].append(mistake)

    def extract_learning_data(self, state: SystemState, hypotheses: List[Hypothesis],
                              action_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract learning data from current session"""
        learning_data = {
            "assumptions": [],
            "strategies": [],
            "failures": [],
            "concepts": [],
            "revisions": []
        }

        for assumption in state.user_assumptions:
            learning_data["assumptions"].append({
                "id": assumption.get("id"),
                "label": assumption.get("label"),
                "validated": assumption.get("validated"),
                "concept": self._identify_concept(assumption.get("label", ""))
            })

        action_types = [a.get("action_id", "").split("_")[0] for a in action_history]
        learning_data["strategies"] = list(set(action_types))

        for action in action_history:
            if action.get("actually_failed"):
                learning_data["failures"].append({
                    "action_id": action.get("action_id"),
                    "turn": action.get("turn"),
                    "concept": self._identify_concept_from_action(action.get("action_id", ""))
                })

        for vuln_id, vuln_data in state.vulnerabilities.items():
            if vuln_data.get("exploited") or vuln_data.get("detected"):
                concept = self._vulnerability_to_concept(vuln_id)
                if concept not in learning_data["concepts"]:
                    learning_data["concepts"].append(concept)

        for contradiction in state.contradictions:
            learning_data["revisions"].append({
                "description": contradiction.get("description"),
                "turn": contradiction.get("turn"),
                "concept": self._identify_concept(contradiction.get("description", ""))
            })

        return learning_data

    def _identify_concept(self, text: str) -> str:
        """Identify security concept from text"""
        text_lower = text.lower()
        if "input" in text_lower or "validation" in text_lower or "normalize" in text_lower:
            return "Input Handling"
        if "decision" in text_lower or "logic" in text_lower or "condition" in text_lower:
            return "Decision Logic"
        if "execution" in text_lower or "context" in text_lower:
            return "Execution Context"
        if "monitor" in text_lower or "observe" in text_lower:
            return "Monitoring and Response"
        if "isolate" in text_lower or "restrict" in text_lower or "access" in text_lower:
            return "Access Control"
        if "stability" in text_lower or "recover" in text_lower:
            return "System Stability"
        return "System Behavior"

    def _identify_concept_from_action(self, action_id: str) -> str:
        """Identify concept from action ID"""
        return self._identify_concept(action_id)

    def _vulnerability_to_concept(self, vuln_id: str) -> str:
        """Map vulnerability ID to security concept"""
        vuln_lower = vuln_id.lower()
        if "decision" in vuln_lower or "logic" in vuln_lower:
            return "Decision Logic"
        if "reflection" in vuln_lower or "output" in vuln_lower:
            return "Output Reflection"
        if "execution" in vuln_lower or "context" in vuln_lower:
            return "Execution Context"
        if "path" in vuln_lower or "scope" in vuln_lower:
            return "Path Scope"
        if "input" in vuln_lower:
            return "Input Handling"
        return "System Behavior"

    def generate_reflection_summary(self, state: SystemState, hypotheses: List[Hypothesis],
                                    action_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a reflection summary at session end"""
        assumptions = [
            {
                "label": a.get("label"),
                "validated": a.get("validated")
            }
            for a in state.user_assumptions[:5]
        ]

        broke = []
        for contradiction in state.contradictions[-5:]:
            if contradiction.get("description"):
                broke.append(contradiction.get("description"))
        for action in action_history[-5:]:
            if action.get("actually_failed"):
                broke.append(f"Action failed: {action.get('action_id')}")

        adaptations = []
        for key, value in state.system_conditions.items():
            if value:
                adaptations.append(key)
        for defense in state.active_defenses:
            adaptations.append(defense)

        finally_worked = [a.get("action_id") for a in action_history[-5:] if not a.get("actually_failed")]

        remains_unsafe = []
        if state.stability < 60:
            remains_unsafe.append("System stability remains degraded")
        if state.system_conditions.get("access_restricted"):
            remains_unsafe.append("Access scope remains restricted")
        if state.system_conditions.get("validation_tightened"):
            remains_unsafe.append("Input handling remains tightened")

        return {
            "initial_assumptions": assumptions,
            "what_broke": broke,
            "system_adaptations": adaptations,
            "what_finally_worked": finally_worked,
            "what_remains_unsafe": remains_unsafe
        }

    def recommend_scenarios(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Recommend scenarios based on user profile"""
        recommendations = []

        for weak_area in self.user_profile["weak_areas"][:2]:
            scenario = self._concept_to_scenario(weak_area)
            if scenario:
                recommendations.append({
                    "scenario_id": scenario["id"],
                    "reason": f"Practice {weak_area}",
                    "priority": "high"
                })

        for mistake in self.user_profile["common_mistakes"][:1]:
            concept = mistake.get("concept")
            if concept:
                scenario = self._concept_to_scenario(concept)
                if scenario:
                    recommendations.append({
                        "scenario_id": scenario["id"],
                        "reason": f"Address common mistake: {mistake.get('type')}",
                        "priority": "medium"
                    })

        return recommendations[:limit]

    def _concept_to_scenario(self, concept: str) -> Optional[Dict[str, Any]]:
        """Map concept to scenario"""
        concept_lower = concept.lower()
        if "input" in concept_lower or "decision" in concept_lower or "logic" in concept_lower:
            return {"id": "input_trust_failures", "title": "Operation: Broken Trust"}
        if "execution" in concept_lower:
            return {"id": "linux_privesc", "title": "Operation: Glass Ceiling"}
        if "monitor" in concept_lower or "access" in concept_lower:
            return {"id": "network_breach", "title": "Operation: Silent Echo"}
        return None

    def get_curriculum_adjustment(self) -> Dict[str, Any]:
        """Get difficulty and focus adjustments for curriculum"""
        adjustment = {
            "difficulty": "medium",
            "focus_areas": [],
            "skip_areas": []
        }

        if len(self.sessions) > 0:
            recent_sessions = self.sessions[-5:]
            success_count = sum(1 for s in recent_sessions
                                if s.final_state.get("stability", 0) > 80)
            success_rate = success_count / len(recent_sessions)

            if success_rate > 0.8:
                adjustment["difficulty"] = "hard"
            elif success_rate < 0.3:
                adjustment["difficulty"] = "easy"

        adjustment["focus_areas"] = self.user_profile["weak_areas"][:3]

        strong_areas = self.user_profile.get("strong_areas", [])
        if len(strong_areas) > 0:
            adjustment["skip_areas"] = strong_areas[:2]

        return adjustment
