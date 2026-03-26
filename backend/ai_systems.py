
"""
AI Systems for CyberArena
- Opponent AI: Named-move catalog system with difficulty scaling and Ollama integration
- Mentor AI: Disabled by default, only asks questions, never gives answers
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from simulation_engine import SystemState, Action, LearningMode, Phase, Hypothesis
import random


class AIDifficulty(Enum):
    RULE_BASED = "rule_based"
    ADAPTIVE   = "adaptive"
    DECEPTIVE  = "deceptive"


class AIPersona(Enum):
    DEFENDER = "defender"   # AI defends; player is attacker
    ATTACKER = "attacker"   # AI attacks; player is defender


@dataclass
class AIBehavior:
    """AI behavior pattern"""
    persona: AIPersona
    difficulty: AIDifficulty
    aggressiveness: int = 0
    adaptation_level: int = 0
    user_patterns: Dict[str, Any] = field(default_factory=dict)
    counter_strategies: List[str] = field(default_factory=list)


# ─── Named AI Move Catalog ────────────────────────────────────────────────────
# Each move entry:
#   label         — short name shown in UI
#   description   — one-sentence narrative shown to player
#   severity      — "low" | "medium" | "high" | "critical"
#   persona       — which AI role uses this move ("attacker" | "defender")
#   effects       — dict applied to state: pressure_delta, stability_delta,
#                   lock_action_types [{type, turns}]
#   counter_hint  — what the player should do to counter this

AI_MOVE_CATALOG: Dict[str, Dict[str, Any]] = {

    # ── ATTACKER moves ─────────────────────────────────────────────────────────
    "stealth_probe": {
        "label": "Stealth Probe",
        "description": "Low-rate packets scan the service boundary; WAF thresholds stay untouched.",
        "severity": "low",
        "persona": "attacker",
        "effects": {"pressure_delta": 4},
        "counter_hint": "Enable monitoring on the web server to catch low-rate probes.",
    },
    "network_recon": {
        "label": "Network Reconnaissance",
        "description": "Attacker enumerates exposed ports and fingerprints service versions.",
        "severity": "low",
        "persona": "attacker",
        "effects": {"pressure_delta": 6},
        "counter_hint": "Audit scheduled jobs or run memory forensics to catch recon artifacts.",
    },
    "credential_stuffing": {
        "label": "Credential Stuffing",
        "description": "Leaked credential lists are replayed against the login endpoint in bursts.",
        "severity": "medium",
        "persona": "attacker",
        "effects": {"pressure_delta": 10, "stability_delta": -5},
        "counter_hint": "Restrict authentication surfaces or throttle outbound traffic.",
    },
    "cron_persistence": {
        "label": "Cron Persistence Planted",
        "description": "A scheduled cron job is registered to re-execute the payload every three hours.",
        "severity": "medium",
        "persona": "attacker",
        "effects": {"pressure_delta": 8, "stability_delta": -4},
        "counter_hint": "Audit scheduled jobs to find and purge the planted entry.",
    },
    "lateral_movement": {
        "label": "Lateral Movement",
        "description": "Attacker pivots from the web server to the database host using a stolen service token.",
        "severity": "high",
        "persona": "attacker",
        "effects": {
            "pressure_delta": 15,
            "stability_delta": -10,
            "lock_action_types": [{"type": "isolate", "turns": 1}],
        },
        "counter_hint": "Isolate the web server immediately to sever the pivot path.",
    },
    "log_wiping": {
        "label": "Log Wiping",
        "description": "Access logs from the last 24 hours are deleted to erase traces of intrusion.",
        "severity": "high",
        "persona": "attacker",
        "effects": {
            "pressure_delta": 12,
            "lock_action_types": [{"type": "inspect", "turns": 2}],
        },
        "counter_hint": "Run memory forensics — logs are gone but RAM still holds traces.",
    },
    "data_staging": {
        "label": "Data Staging",
        "description": "Sensitive records are quietly copied to a staging directory before exfiltration.",
        "severity": "medium",
        "persona": "attacker",
        "effects": {"pressure_delta": 10, "stability_delta": -5},
        "counter_hint": "Throttle outbound traffic to disrupt the staging transfer.",
    },
    "privilege_escalation": {
        "label": "Privilege Escalation",
        "description": "A SUID binary is exploited to obtain root on the application server.",
        "severity": "high",
        "persona": "attacker",
        "effects": {"pressure_delta": 18, "stability_delta": -8},
        "counter_hint": "Isolate the compromised component and audit cron/SUID entries.",
    },
    "traffic_flood": {
        "label": "Traffic Flood (DoS)",
        "description": "Tens of thousands of requests per second hammer the service toward crash.",
        "severity": "critical",
        "persona": "attacker",
        "effects": {"pressure_delta": 25, "stability_delta": -15},
        "counter_hint": "Apply traffic shaping to rate-limit the flood and buy time.",
    },
    "process_injection": {
        "label": "Process Injection",
        "description": "Shellcode is injected into a live web-server worker process in memory.",
        "severity": "critical",
        "persona": "attacker",
        "effects": {
            "pressure_delta": 20,
            "stability_delta": -12,
            "lock_action_types": [{"type": "monitor", "turns": 1}],
        },
        "counter_hint": "Run memory forensics to detect injected code before it escalates.",
    },

    # ── DEFENDER moves ─────────────────────────────────────────────────────────
    "timing_jitter": {
        "label": "Timing Jitter Introduced",
        "description": "Random response delays are added to confuse timing-based probing.",
        "severity": "low",
        "persona": "defender",
        "effects": {
            "pressure_delta": -2,
            "lock_action_types": [{"type": "probe", "turns": 1}],
        },
        "counter_hint": "Switch to a payload-content probe instead of timing analysis.",
    },
    "validation_tightened": {
        "label": "Input Validation Tightened",
        "description": "Normalization rules are updated to block known payload patterns.",
        "severity": "medium",
        "persona": "defender",
        "effects": {
            "pressure_delta": -3,
            "lock_action_types": [
                {"type": "probe", "turns": 1},
                {"type": "inspect", "turns": 1},
            ],
        },
        "counter_hint": "Vary payload encoding or probe non-standard fields.",
    },
    "ip_block": {
        "label": "IP Range Blocked",
        "description": "Your egress IP range is added to the WAF deny list.",
        "severity": "medium",
        "persona": "defender",
        "effects": {
            "pressure_delta": -5,
            "lock_action_types": [
                {"type": "probe", "turns": 2},
                {"type": "stealth_probe", "turns": 2},
            ],
        },
        "counter_hint": "Rotate source address or use a slow-fragment approach.",
    },
    "honeypot_activated": {
        "label": "Honeypot Activated",
        "description": "A convincing fake endpoint is deployed to lure and flag the attacker.",
        "severity": "medium",
        "persona": "defender",
        "effects": {
            "pressure_delta": 5,
            "deploy_honeypot_vuln": {}
        },
        "counter_hint": "Fingerprint endpoints carefully before probing obvious targets.",
    },
    "silently_harden_component": {
        "label": "Silent Hardening",
        "description": "A critical system component is stealthily hardened against basic exploitation.",
        "severity": "high",
        "persona": "defender",
        "effects": {
            "harden_components": ["authentication_service", "database"]
        },
        "counter_hint": "Look for alternative lateral movement paths.",
    },
    "emergency_patch": {
        "label": "Emergency Patch Deployed",
        "description": "A hotfix closes the exploited input path — but leaves other surfaces open.",
        "severity": "high",
        "persona": "defender",
        "effects": {
            "pressure_delta": -8,
            "lock_action_types": [
                {"type": "escalate", "turns": 2},
                {"type": "pivot", "turns": 2},
            ],
        },
        "counter_hint": "Find an alternative vector the patch doesn't cover.",
    },
    "adaptive_rate_limit": {
        "label": "Adaptive Rate Limiting",
        "description": "The WAF dynamically throttles suspicious request patterns in real-time.",
        "severity": "high",
        "persona": "defender",
        "effects": {
            "pressure_delta": -6,
            "lock_action_types": [
                {"type": "stealth_probe", "turns": 2},
                {"type": "probe", "turns": 2},
            ],
        },
        "counter_hint": "Slow your request cadence or rotate attack vectors.",
    },
    "full_lockdown": {
        "label": "Full System Lockdown",
        "description": "All sensitive operations are frozen system-wide for several turns.",
        "severity": "critical",
        "persona": "defender",
        "effects": {
            "pressure_delta": -10,
            "lock_action_types": [
                {"type": "escalate", "turns": 3},
                {"type": "pivot", "turns": 3},
            ],
        },
        "counter_hint": "Wait out the lockdown window or target a different component.",
    },
}


class OpponentAI:
    """AI opponent with a visible named-move system.

    Each turn the AI picks one or more moves from AI_MOVE_CATALOG
    based on difficulty level + game state. The returned list of move
    records (label, description, severity, effects_summary, counter_hint)
    is surfaced in the Threat Feed panel on the frontend.

    Difficulty scaling:
      RULE_BASED  — predictable scripted sequence, 1 move/turn
      ADAPTIVE    — reacts to player's last action type, 1-2 moves/turn
      DECEPTIVE   — Ollama picks best moves + writes custom message, 2-3 moves/turn
    """

    def __init__(self, persona: AIPersona, difficulty: AIDifficulty):
        self.persona    = persona
        self.difficulty = difficulty
        self.behavior   = AIBehavior(persona, difficulty)
        self.action_history: List[Dict[str, Any]] = []
        self.user_patterns:  Dict[str, Any]       = {}
        self.threat_level: int = 0
        self.last_intent: str  = "unknown"
        self._turn: int = 0
        self._last_move_id: Optional[str] = None

    # ── Public interface ──────────────────────────────────────────────────

    def evaluate_intent(self, action: Optional[Action],
                        hypothesis_id: Optional[str] = None,
                        hypothesis_label: Optional[str] = None) -> str:
        if action and action.type == "hypothesis":
            self.last_intent = "test_hypothesis"; return self.last_intent
        if hypothesis_id:
            self.last_intent = "test_hypothesis"; return self.last_intent
        if not action:
            self.last_intent = "unknown"; return self.last_intent
        t = (action.type or "").lower()
        if any(k in t for k in ("probe", "inspect")):
            self.last_intent = "recon"
        elif "escalate" in t:
            self.last_intent = "escalation"
        elif any(k in t for k in ("isolate", "restrict", "monitor")):
            self.last_intent = "containment"
        else:
            self.last_intent = "unknown"
        return self.last_intent

    def pick_and_execute_move(
        self,
        state: SystemState,
        user_action: Optional[Action],
        mode: Optional[LearningMode] = None,
    ) -> List[Dict[str, Any]]:
        """Pick AI move(s) for this turn and return structured move records.

        Each record shape:
          { name, label, description, severity, effects_summary,
            counter_hint, effects, message }

        The first record is the primary move shown in the Threat Feed.
        """
        self._turn += 1

        if user_action:
            self.action_history.append({
                "action_id":        user_action.id,
                "turn":             self._turn,
                "user_action":      user_action.label,
                "user_action_type": user_action.type,
            })
            self._analyze_user_pattern(user_action, state)

        # Pick move IDs according to difficulty
        if self.difficulty == AIDifficulty.RULE_BASED:
            move_ids = self._pick_rule_based(state)
        elif self.difficulty == AIDifficulty.ADAPTIVE:
            move_ids = self._pick_adaptive(state, user_action)
        else:
            move_ids = self._pick_deceptive(state, user_action, mode)

        # Keep only moves that match our persona
        persona_val = self.persona.value
        move_ids = [m for m in move_ids
                    if AI_MOVE_CATALOG.get(m, {}).get("persona") == persona_val]
        if not move_ids:
            move_ids = self._fallback_moves()

        # Add repetition punishment if player spams same action
        punishment_ids: List[str] = []
        if user_action:
            punishment_ids = self._punish_repetition_ids(user_action)

        all_ids = move_ids + punishment_ids

        # Build records
        ai_actions: List[Dict[str, Any]] = []
        for mid in all_ids:
            rec = self._build_move_record(mid)
            if rec:
                ai_actions.append(rec)
                self._last_move_id = mid

        # Update visual state
        if state and hasattr(state, "ai_visual_state"):
            state.ai_visual_state.entropy = min(
                100, state.ai_visual_state.entropy + len(ai_actions) * 3
            )
            if self.threat_level > 70:
                state.ai_visual_state.posture  = "aggressive" if persona_val == "attacker" else "defensive"
                state.ai_visual_state.distance = "approaching" if persona_val == "attacker" else "closing"
            elif self.threat_level > 30:
                state.ai_visual_state.posture  = "observing"
                state.ai_visual_state.distance = "middle"

        return ai_actions

    # Backward-compat alias used in engine.py
    def react_to_action(self, user_action, state, available_actions=None,
                        intent=None, mode=None):
        return self.pick_and_execute_move(state, user_action, mode)

    # ── Difficulty pickers ────────────────────────────────────────────────

    def _pick_rule_based(self, state: SystemState) -> List[str]:
        """1 move/turn — predictable scripted ladder."""
        if self.persona == AIPersona.ATTACKER:
            seq = [
                "stealth_probe", "network_recon", "credential_stuffing",
                "cron_persistence", "lateral_movement", "log_wiping",
                "privilege_escalation", "process_injection", "traffic_flood",
            ]
        else:
            seq = [
                "timing_jitter", "validation_tightened", "ip_block",
                "honeypot_activated", "emergency_patch", "silently_harden_component",
                "adaptive_rate_limit", "full_lockdown",
            ]
        return [seq[(self._turn - 1) % len(seq)]]

    def _pick_adaptive(self, state: SystemState,
                       user_action: Optional[Action]) -> List[str]:
        """React to player's last action type and overall style — 1-2 moves."""
        ut = (user_action.type or "").lower() if user_action else ""

        # Determine the user's favored "Type"
        dominant_type = None
        max_count = 0
        for t, stats in self.user_patterns.items():
            if stats["count"] >= 3 and stats["count"] > max_count:
                dominant_type = t.lower()
                max_count = stats["count"]

        if self.persona == AIPersona.ATTACKER:
            # Type Advantage counters
            if dominant_type and "isolate" in dominant_type:
                picks = ["lateral_movement", "process_injection"]
            elif dominant_type and "restrict" in dominant_type:
                picks = ["privilege_escalation"]
            elif "isolate" in ut:
                picks = ["lateral_movement", "process_injection"]
            elif "monitor" in ut or "inspect" in ut:
                picks = ["log_wiping", "stealth_probe"]
            elif "restrict" in ut:
                picks = ["credential_stuffing", "cron_persistence"]
            elif state.pressure > 70:
                picks = ["traffic_flood"]
            elif state.pressure > 40:
                picks = ["privilege_escalation", "lateral_movement"]
            else:
                picks = ["network_recon", "credential_stuffing"]
        else:
            # Type Advantage counters
            if dominant_type and "escalate" in dominant_type:
                picks = ["full_lockdown", "emergency_patch"]
            elif dominant_type and "probe" in dominant_type:
                picks = ["honeypot_activated", "timing_jitter"]
            elif "probe" in ut or "stealth" in ut:
                picks = ["honeypot_activated", "timing_jitter"]
            elif "escalate" in ut or "pivot" in ut:
                picks = ["emergency_patch", "ip_block"]
            elif state.pressure > 60:
                picks = ["adaptive_rate_limit", "validation_tightened"]
            else:
                picks = ["validation_tightened"]

        return picks[:2] if self.threat_level > 50 else picks[:1]

    def _pick_deceptive(self, state: SystemState, user_action: Optional[Action],
                        mode: Optional[LearningMode]) -> List[str]:
        """2-3 moves — tries Ollama, falls back to adaptive + bonus."""
        try:
            picks = self._ollama_pick_moves(state, user_action)
            if picks:
                return picks[:3]
        except Exception:
            pass

        adaptive = self._pick_adaptive(state, user_action)
        if self.persona == AIPersona.ATTACKER:
            extras = ["process_injection", "data_staging", "privilege_escalation"]
        else:
            extras = ["full_lockdown", "adaptive_rate_limit", "emergency_patch"]
        for e in extras:
            if e not in adaptive:
                adaptive.append(e)
                break
        return adaptive[:3]

    def _ollama_pick_moves(self, state: SystemState,
                           user_action: Optional[Action]) -> List[str]:
        """Ask Ollama to pick the best move IDs (4s hard timeout)."""
        import urllib.request, json, threading

        persona_val = self.persona.value
        available = [k for k, v in AI_MOVE_CATALOG.items()
                     if v["persona"] == persona_val]
        catalog_text = "\n".join(
            f"  {mid}: {AI_MOVE_CATALOG[mid]['label']} — {AI_MOVE_CATALOG[mid]['description']}"
            for mid in available
        )
        ua_str = f"{user_action.label} ({user_action.type})" if user_action else "none"
        prompt = (
            f"You are an AI {persona_val} in a cybersecurity game.\n"
            f"State: pressure={state.pressure}, stability={state.stability}, turn={self._turn}.\n"
            f"Player just did: {ua_str}\n\n"
            f"Pick 2-3 move IDs that are most effective right now. "
            f"Reply ONLY with a JSON array of ID strings.\n\nMoves:\n{catalog_text}"
        )

        result: List[str] = []
        err: List[Exception] = []

        def call():
            try:
                payload = json.dumps({
                    "model": "llama3:8b", "prompt": prompt, "stream": False,
                    "options": {"temperature": 0.4, "num_predict": 80}
                }).encode()
                req = urllib.request.Request(
                    "http://localhost:11434/api/generate", data=payload,
                    headers={"Content-Type": "application/json"}, method="POST"
                )
                with urllib.request.urlopen(req, timeout=4) as r:
                    text = json.loads(r.read()).get("response", "").strip()
                    s, e = text.find("["), text.rfind("]") + 1
                    if s >= 0 and e > s:
                        picks = json.loads(text[s:e])
                        result.extend(p for p in picks if p in AI_MOVE_CATALOG)
            except Exception as ex:
                err.append(ex)

        t = threading.Thread(target=call, daemon=True)
        t.start(); t.join(timeout=5)
        if err or not result:
            raise RuntimeError("Ollama unavailable or returned no valid moves")
        return result

    def _fallback_moves(self) -> List[str]:
        if self.persona == AIPersona.ATTACKER:
            return ["stealth_probe"]
        return ["timing_jitter"]

    # ── Build structured record ───────────────────────────────────────────

    def _build_move_record(self, move_id: str) -> Optional[Dict[str, Any]]:
        defn = AI_MOVE_CATALOG.get(move_id)
        if not defn:
            return None
        effects = defn.get("effects", {})
        summary: List[str] = []
        pd = effects.get("pressure_delta", 0)
        sd = effects.get("stability_delta", 0)
        if pd > 0:  summary.append(f"+{pd} Pressure")
        elif pd < 0: summary.append(f"{pd} Pressure")
        if sd < 0:  summary.append(f"{sd} Stability")
        elif sd > 0: summary.append(f"+{sd} Stability")
        for lk in effects.get("lock_action_types", []):
            summary.append(f"Locks {lk['type'].title()} ({lk['turns']}t)")

        return {
            "name":          move_id,
            "label":         defn["label"],
            "description":   defn["description"],
            "severity":      defn["severity"],
            "effects_summary": summary,
            "counter_hint":  defn.get("counter_hint", ""),
            "effects":       effects,
            "message":       defn["description"],   # backward compat
        }

    # ── Helpers ───────────────────────────────────────────────────────────

    def _analyze_user_pattern(self, action: Action, state: SystemState):
        t = action.type
        if t not in self.user_patterns:
            self.user_patterns[t] = {"count": 0, "streak": 0}
        self.user_patterns[t]["count"]  += 1
        self.user_patterns[t]["streak"] += 1
        for k in self.user_patterns:
            if k != t:
                self.user_patterns[k]["streak"] = 0
        if action.pressure_delta > 0:
            self.threat_level = min(100, self.threat_level + action.pressure_delta)
        if action.stability_delta < 0:
            self.threat_level = min(100, self.threat_level + abs(action.stability_delta))

    def _punish_repetition_ids(self, user_action: Action) -> List[str]:
        """Return extra move IDs as punishment for repetition (adds 'pattern_resistance')."""
        t = user_action.type
        streak = self.user_patterns.get(t, {}).get("streak", 0)
        if streak < 3:
            return []
        # We'll add a virtual entry; _build_move_record handles it
        return ["pattern_resistance"]

    def _build_move_record(self, move_id: str) -> Optional[Dict[str, Any]]:
        # Handle the virtual pattern_resistance entry
        if move_id == "pattern_resistance":
            return {
                "name": "pattern_resistance",
                "label": "Pattern Resistance",
                "description": "The system adapted to your repeated approach and counter-calibrated.",
                "severity": "medium",
                "effects_summary": ["+6 Pressure", "Locks repeated action type (2t)"],
                "counter_hint": "Vary your action types to prevent the AI from adapting.",
                "effects": {
                    "pressure_delta": 6,
                    "set_conditions": {"validation_tightened": True},
                },
                "message": "System adapted to repeated approach.",
            }
        defn = AI_MOVE_CATALOG.get(move_id)
        if not defn:
            return None
        effects = defn.get("effects", {})
        summary: List[str] = []
        pd = effects.get("pressure_delta", 0)
        sd = effects.get("stability_delta", 0)
        if pd > 0:   summary.append(f"+{pd} Pressure")
        elif pd < 0: summary.append(f"{pd} Pressure")
        if sd < 0:   summary.append(f"{sd} Stability")
        elif sd > 0: summary.append(f"+{sd} Stability")
        for lk in effects.get("lock_action_types", []):
            summary.append(f"Locks {lk['type'].title()} ({lk['turns']}t)")
        return {
            "name":            move_id,
            "label":           defn["label"],
            "description":     defn["description"],
            "severity":        defn["severity"],
            "effects_summary": summary,
            "counter_hint":    defn.get("counter_hint", ""),
            "effects":         effects,
            "message":         defn["description"],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Mentor AI — only asks questions, never gives direct answers
# ─────────────────────────────────────────────────────────────────────────────

class MentorAI:
    """Mentor AI that only asks questions, never gives answers"""

    def __init__(self):
        self.enabled = False
        self.question_history: List[Dict[str, Any]] = []

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def analyze_situation(self, state: SystemState, last_action: Optional[Action] = None,
                          action_history: List[Dict[str, Any]] = None,
                          available_actions: List[Action] = None,
                          hypotheses: List[Hypothesis] = None) -> Dict[str, Any]:
        guidance = {
            "type": "analysis",
            "situation_summary": "",
            "questions": [],
            "anomalies": [],
            "inconsistencies": [],
            "concepts": [],
            "observations": [],
            "next_steps": [],
        }

        situation_parts = []
        active_conditions = [k for k, v in state.system_conditions.items() if v]
        if active_conditions:
            situation_parts.append("System posture tightening")
            guidance["observations"].append("Behavioral changes active: " + ", ".join(active_conditions))
            guidance["questions"].append("Which recent actions triggered these behavioral shifts?")

        if state.stability < 60:
            situation_parts.append("Stability degraded")
            guidance["questions"].append("Stability is drifting. What chain of actions caused the degradation?")

        monitored = [k for k, v in state.system_components.items() if v.get("monitoring")]
        hardened  = [k for k, v in state.system_components.items() if v.get("hardened")]
        if monitored:
            guidance["observations"].append(f"Monitoring active on {', '.join(monitored)}.")
            guidance["questions"].append("How does active monitoring change your next step?")
        if hardened:
            guidance["observations"].append(f"Hardening observed on {', '.join(hardened)}.")
            guidance["questions"].append("What alternative approach avoids the hardened surface?")

        if action_history and len(action_history) > 0:
            recent = action_history[-5:]
            types  = [a.get("action_id", "").split("_")[0] for a in recent]
            if "probe" in types or "inspect" in types:
                guidance["observations"].append("You've been probing. Patterns should be forming.")
                guidance["questions"].append("Based on your probing, what hypothesis can you test next?")
            if "escalate" in types:
                guidance["observations"].append("You've escalated context. New behaviors should be visible.")
                guidance["questions"].append("How does the system react when you push execution boundaries?")
            if any(a.get("actually_failed") for a in recent):
                guidance["anomalies"].append("Some recent actions appeared successful but later failed.")
                guidance["questions"].append("When a result flips later, what does that say about hidden adaptation?")

        if state.contradictions:
            latest = state.contradictions[-1]
            guidance["inconsistencies"].append(
                f"Assumption contradicted: {latest.get('description', 'Unexpected behavior observed')}"
            )
            guidance["questions"].append("When your assumptions are wrong, how do you revise your mental model?")

        guidance["situation_summary"] = (
            "Current situation: " + ", ".join(situation_parts) + "."
            if situation_parts
            else "System is in initial state. Begin by forming hypotheses about the system's behavior."
        )

        if state.user_assumptions:
            untested = [a for a in state.user_assumptions if a.get("validated") is None]
            if untested:
                guidance["questions"].append(
                    f"You have {len(untested)} untested assumption(s). How can you validate them?"
                )

        guidance["next_steps"] = self._suggest_next_steps(
            state, last_action, action_history, available_actions, hypotheses
        )
        return guidance

    def _suggest_next_steps(self, state, last_action, action_history,
                            available_actions, hypotheses):
        next_steps = []
        if not available_actions:
            return ["No actions available. Check if you need to form and validate a hypothesis first."]

        if hypotheses:
            untested = [h for h in hypotheses if not h.tested]
            if untested:
                next_steps.append(f"You have {len(untested)} untested hypothesis(ies). Test one to unlock new actions.")

        available = [a for a in available_actions if a.available]
        locked    = [a for a in available_actions if not a.available]
        if not available:
            if locked:
                next_steps.append(f"{len(locked)} action(s) locked. Validate the required hypothesis to unlock them.")
            return next_steps or ["No actions available at this time."]

        action_types: Dict[str, List] = {}
        for a in available:
            t = a.type if hasattr(a, "type") else "unknown"
            action_types.setdefault(t, []).append(a)

        if not action_history:
            if "probe" in action_types or "inspect" in action_types:
                next_steps.append("Start by probing or inspecting to gather information.")
            else:
                next_steps.append("Begin exploring available actions to understand system behavior.")
        else:
            recent_types = [a.get("action_id", "").split("_")[0] for a in action_history[-3:]]
            if all(t in ["probe", "inspect"] for t in recent_types):
                if "escalate" in action_types:
                    next_steps.append("You've gathered info. Consider escalating to test hypotheses.")
                elif hypotheses and any(not h.tested for h in hypotheses):
                    next_steps.append("Based on your probing, test a hypothesis to unlock advanced actions.")
            if "escalate" in recent_types:
                if state.pressure > 60:
                    next_steps.append("System pressure rising. Consider isolating components.")
                elif "isolate" in action_types or "restrict" in action_types:
                    next_steps.append("You've escalated. Consider isolating or restricting execution.")
            if state.pressure > 70:
                if "isolate" in action_types:
                    next_steps.append("High pressure. Isolate components to contain the threat.")
                elif "restrict" in action_types:
                    next_steps.append("Critical pressure. Restrict execution to limit the surface.")
            if state.stability < 50:
                if "isolate" in action_types:
                    next_steps.append("Stability compromised. Isolate affected components.")
                elif "restrict" in action_types:
                    next_steps.append("Low stability. Restrict execution to prevent further degradation.")

        if not next_steps:
            if "probe" in action_types:
                next_steps.append("Continue probing to gather more information.")
            elif available:
                next_steps.append(f"You have {len(available)} available action(s). Consider your next move.")
        return next_steps

    def get_guidance(self, state, last_action=None, action_history=None,
                     available_actions=None, hypotheses=None):
        return self.analyze_situation(state, last_action, action_history,
                                      available_actions, hypotheses)

# ── Anti-Abuse Input Filter ────────────────────────────────────────────────

class InputFilter:
    """Pre-LLM semantic filter to reject garbage/nonsense hypothesis text."""

    # Known system terms the user should reference
    KNOWN_COMPONENTS = {
        "waf", "firewall", "web server", "webserver", "database", "db",
        "api", "server", "login", "endpoint", "session", "auth",
        "authentication", "service", "network", "port", "cron", "scheduler",
        "log", "logs", "input", "output", "traffic", "request", "response",
        "admin", "shell", "process", "memory", "dns", "proxy", "gateway",
        "component", "system", "application", "app", "backend", "frontend",
    }
    KNOWN_ATTACK_VECTORS = {
        "injection", "sql", "xss", "bypass", "escalation", "privilege",
        "brute force", "credential", "overflow", "exploit", "vulnerability",
        "payload", "malware", "phishing", "dos", "ddos", "flood",
        "persistence", "lateral", "pivot", "exfiltration", "recon",
        "reconnaissance", "scan", "probe", "sniff", "spoof", "tamper",
        "hijack", "mitm", "man in the middle", "rootkit", "backdoor",
        "trojan", "worm", "ransomware", "cron job", "scheduled task",
        "rate limit", "honeypot", "decoy", "validation", "sanitization",
        "encoding", "obfuscation", "evasion", "stealth", "hardened",
        "patched", "compromised", "breached", "attack", "defense",
        "monitoring", "detection", "alert", "block", "restrict", "isolate",
    }
    MIN_LENGTH = 10

    @classmethod
    def validate(cls, text: str) -> dict:
        """Returns {"valid": bool, "reason": str}."""
        text_lower = text.strip().lower()
        if len(text_lower) < cls.MIN_LENGTH:
            return {"valid": False, "reason": "Input too short. Describe your theory in detail."}

        has_component = any(term in text_lower for term in cls.KNOWN_COMPONENTS)
        has_vector = any(term in text_lower for term in cls.KNOWN_ATTACK_VECTORS)

        if not has_component and not has_vector:
            return {
                "valid": False,
                "reason": "No recognizable system components or attack vectors detected. "
                          "Reference specific parts of the system (e.g., WAF, database, login) "
                          "and describe a specific vulnerability or behavior."
            }
        return {"valid": True, "reason": ""}


# ── Hybrid Hypothesis Validation System ────────────────────────────────────

class OllamaValidator:
    """LLM = Intent Interpreter ONLY. Parses user text into structured intent JSON.
    Does NOT decide correctness — that is the Engine's job."""

    @staticmethod
    def parse_intent(user_text: str, hypothesis_labels: list) -> dict:
        """
        Sends user_text to LLaMA to extract structured intent.
        Returns: { "target": str, "claim": str, "confidence": float,
                   "best_match_id": str|null, "explanation": str }
        The LLM NEVER decides truth; it only interprets what the user is trying to say.
        """
        import json
        import urllib.request

        # Build a label map for the LLM to reference (no correctness info!)
        label_list = "\n".join(
            f'- id: "{h["id"]}", label: "{h["label"]}"'
            for h in hypothesis_labels
        )

        prompt = f"""You are a cybersecurity intent parser. Your ONLY job is to understand 
what system component and claim the user is making. You do NOT judge correctness.

The user wrote: "{user_text}"

Available hypothesis IDs in this scenario:
{label_list}

Your task:
1. Identify the system component the user is targeting (e.g., "input_validation", "session_management", "scheduled_tasks", "network_traffic", "authentication").
2. Identify the claim type (e.g., "bypass_possible", "persistence_via_cron", "exfiltration_active", "rate_limit_evasion", "decoy_endpoint").
3. Rate your confidence (0.0–1.0) that you understood the user's intent correctly.
4. If the user's text closely matches one of the available hypothesis labels, provide that hypothesis ID as "best_match_id". Otherwise null.
5. Write a brief 1-sentence summary of the user's intent.

Reply ONLY with a raw JSON object:
{{
  "target": string,
  "claim": string,
  "confidence": number,
  "best_match_id": string or null,
  "explanation": string
}}
"""
        try:
            req = urllib.request.Request(
                "http://localhost:11434/api/generate",
                data=json.dumps({
                    "model": "llama3:8b",
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                response_text = result.get("response", "{}")
                parsed = json.loads(response_text)
                # Ensure confidence is a float in [0, 1]
                parsed["confidence"] = max(0.0, min(1.0, float(parsed.get("confidence", 0.5))))
                return parsed
        except Exception as e:
            print(f"OllamaValidator.parse_intent error: {e}")
            return {
                "target": "unknown",
                "claim": "unknown",
                "confidence": 0.0,
                "best_match_id": None,
                "explanation": "Intent parsing failed due to AI subsystem timeout."
            }


class EngineValidator:
    """Engine = Truth Validator. Matches parsed LLM intent against actual
    simulation state to produce a deterministic, explainable verdict."""

    @staticmethod
    def evaluate(intent: dict, hypotheses_config: dict, state) -> dict:
        """
        Deterministically validates parsed intent against real engine state.
        Returns graded classification:
        {
            "classification": "correct" | "partial" | "incorrect",
            "confidence": float,
            "matched_hypothesis_id": str | None,
            "matched_signals": [...],
            "missing_elements": [...],
            "contradiction_feedback": str
        }
        """
        llm_confidence = intent.get("confidence", 0.0)
        best_match_id = intent.get("best_match_id")
        target = (intent.get("target") or "").lower()
        claim = (intent.get("claim") or "").lower()

        matched_signals = []
        missing_elements = []
        matched_id = None
        engine_correct = False

        # Strategy 1: Direct ID match from LLM
        if best_match_id and best_match_id in hypotheses_config:
            hyp = hypotheses_config[best_match_id]
            if hyp.get("correct") is True:
                engine_correct = True
                matched_id = best_match_id
                matched_signals.append(f"Matched hypothesis: {hyp.get('label', best_match_id)}")
            else:
                missing_elements.append(f"Hypothesis '{hyp.get('label', best_match_id)}' is not a true vulnerability in this scenario.")

        # Strategy 2: Semantic fallback — scan all hypotheses for keyword overlap
        if not matched_id:
            for hyp_id, hyp in hypotheses_config.items():
                hyp_label = (hyp.get("label") or "").lower()
                hyp_desc = (hyp.get("description") or "").lower()

                # Check if target/claim keywords overlap with hypothesis text
                target_match = target in hyp_label or target in hyp_desc
                claim_match = claim in hyp_label or claim in hyp_desc

                if target_match or claim_match:
                    if hyp.get("correct") is True:
                        engine_correct = True
                        matched_id = hyp_id
                        matched_signals.append(f"Semantic match: {hyp.get('label', hyp_id)}")
                    else:
                        missing_elements.append(f"'{hyp.get('label', hyp_id)}' is a known decoy/false lead.")

        # Strategy 3: State-aware checks — validate against live component/vulnerability state
        if state:
            # Check if the user references something that is hardened
            for comp_id, comp in getattr(state, 'system_components', {}).items():
                if comp_id.replace("_", " ") in target or comp_id.replace("_", "") in target:
                    if comp.get("hardened"):
                        missing_elements.append(f"Component '{comp_id}' is currently hardened — exploits against it will fail.")
                    if comp.get("monitoring"):
                        matched_signals.append(f"Component '{comp_id}' is being monitored.")

            # Check if user references a patched vulnerability
            for vuln_id, vuln in getattr(state, 'vulnerabilities', {}).items():
                if vuln_id.replace("_", " ") in target or vuln_id in claim:
                    if vuln.get("patched"):
                        missing_elements.append(f"Vulnerability '{vuln_id}' has been patched.")
                    if vuln.get("false_lead"):
                        missing_elements.append(f"'{vuln_id}' is a decoy/honeypot — not a real vulnerability.")
                    if vuln.get("active") and not vuln.get("false_lead") and not vuln.get("patched"):
                        matched_signals.append(f"Vulnerability '{vuln_id}' is active and exploitable.")

            # Check active defenses
            for defense in getattr(state, 'active_defenses', []):
                if defense.replace("_", " ") in claim or defense in target:
                    matched_signals.append(f"Defense '{defense}' is currently active.")

        # ── Compute final classification ──
        # Engine truth ALWAYS overrides LLM confidence
        if engine_correct and matched_id:
            combined_confidence = min(1.0, llm_confidence * 0.4 + 0.6)  # Engine boost
            if combined_confidence >= 0.8:
                classification = "correct"
            else:
                classification = "partial"
        elif matched_signals and not engine_correct:
            # User identified real signals but didn't nail the exact hypothesis
            combined_confidence = llm_confidence * 0.5
            classification = "partial" if combined_confidence >= 0.5 else "incorrect"
        else:
            combined_confidence = llm_confidence * 0.3  # Heavy penalty when engine says no
            classification = "incorrect"

        # ── Build contradiction feedback ──
        feedback = EngineValidator._build_contradiction_feedback(
            intent, classification, matched_signals, missing_elements, state
        )

        return {
            "classification": classification,
            "confidence": round(combined_confidence, 2),
            "matched_hypothesis_id": matched_id,
            "matched_signals": matched_signals,
            "missing_elements": missing_elements,
            "contradiction_feedback": feedback
        }

    @staticmethod
    def _build_contradiction_feedback(intent, classification, signals, missing, state) -> str:
        """Build structured, educational feedback referencing actual system state."""
        parts = []

        if classification == "correct":
            parts.append(f"✓ Hypothesis validated. Your analysis correctly identified the vulnerability.")
            if signals:
                parts.append(f"Evidence: {'; '.join(signals)}")
        elif classification == "partial":
            parts.append(f"⚠ Partial match. Your reasoning has merit but is incomplete.")
            if signals:
                parts.append(f"Correct observations: {'; '.join(signals)}")
            if missing:
                parts.append(f"Issues: {'; '.join(missing)}")
        else:
            target = intent.get("target", "unknown")
            claim = intent.get("claim", "unknown")
            parts.append(f"✗ Contradiction detected.")
            parts.append(f"Your hypothesis targets '{target}' with claim '{claim}'.")
            if missing:
                parts.append(f"However: {'; '.join(missing)}")
            else:
                parts.append("No matching vulnerability pattern exists in the current system state.")

            # Reference recent events if available
            if state and hasattr(state, 'system_events') and state.system_events:
                recent = state.system_events[-3:]
                event_msgs = [e.get("message", "") for e in recent if e.get("level") != "info"]
                if event_msgs:
                    parts.append(f"Recent system activity: {'; '.join(event_msgs)}")

            # Reference active defenses
            if state and hasattr(state, 'active_defenses') and state.active_defenses:
                parts.append(f"Active defenses: {', '.join(state.active_defenses)}")

        return " | ".join(parts)
