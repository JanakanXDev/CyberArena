"""
Beginner learning path metadata and additive feedback helpers.
This module does not change core hypothesis validation rules.
"""

from typing import Dict, Any, List

BEGINNER_MODULE_ORDER: List[str] = [
    "beginner_signals",
    "beginner_hypothesis",
    "beginner_actions",
    "beginner_cause_effect",
    "beginner_metrics",
    "beginner_final_simulation",
]


BEGINNER_MODULES: Dict[str, Dict[str, str]] = {
    "beginner_signals": {
        "name": "Signals",
        "goal": "Observe system responses, read State Signals, then name what changed—before forming theories.",
        "prompt": "Use Observe logs → Check system state → pick the identification that matches what you saw.",
    },
    "beginner_hypothesis": {
        "name": "Hypothesis",
        "goal": "Form one clear, testable hypothesis from observed evidence.",
        "prompt": "Write a hypothesis that references one concrete signal.",
    },
    "beginner_actions": {
        "name": "Actions",
        "goal": "Understand what each action type does and when to use it.",
        "prompt": "Choose one low-risk action and observe the result.",
    },
    "beginner_cause_effect": {
        "name": "Cause & Effect",
        "goal": "Connect action choices to system reactions.",
        "prompt": "Run an action, then explain the immediate system response.",
    },
    "beginner_metrics": {
        "name": "Metrics",
        "goal": "Understand pressure and stability changes over turns.",
        "prompt": "Track pressure/stability after each action and describe the pattern.",
    },
    "beginner_final_simulation": {
        "name": "Final Simulation",
        "goal": "Combine signals, hypotheses, actions, and metrics in one run.",
        "prompt": "Use the full loop: observe, hypothesize, act, and reflect.",
    },
}

# Maps identification action id → system_conditions key (must match scenario_system identify_map)
_IDENTIFY_TO_SIGNAL: Dict[str, str] = {
    "act_beginner_identify_timing": "timing_jitter",
    "act_beginner_identify_validation": "validation_tightened",
    "act_beginner_identify_access": "access_restricted",
    "act_beginner_identify_routing": "route_shifted",
    "act_beginner_identify_errors": "errors_suppressed",
    "act_beginner_identify_deception": "deception_active",
}

_SIGNAL_HUMAN: Dict[str, str] = {
    "timing_jitter": "response timing / delay behavior",
    "validation_tightened": "input validation or filtering",
    "access_restricted": "access or reach restrictions",
    "route_shifted": "routing or path changes",
    "errors_suppressed": "suppressed or generic errors",
    "deception_active": "deceptive or bait behavior",
}


def is_beginner_module(scenario_id: str) -> bool:
    return scenario_id in BEGINNER_MODULES


def learning_path_payload(scenario_id: str) -> Dict[str, Any]:
    module = BEGINNER_MODULES.get(scenario_id)
    if not module:
        return {}
    module_index = BEGINNER_MODULE_ORDER.index(scenario_id)
    payload: Dict[str, Any] = {
        "title": "Beginner Learning Path",
        "moduleOrder": [
            {"id": module_id, "name": BEGINNER_MODULES[module_id]["name"]}
            for module_id in BEGINNER_MODULE_ORDER
        ],
        "currentModuleId": scenario_id,
        "currentModuleName": module["name"],
        "currentModuleGoal": module["goal"],
        "currentModulePrompt": module["prompt"],
        "moduleIndex": module_index,
        "totalModules": len(BEGINNER_MODULE_ORDER),
    }
    if scenario_id == "beginner_signals":
        payload["observationOnly"] = True
    return payload


def _signals_feedback_lines(active: List[str]) -> str:
    if not active:
        return (
            "→ No defender-driven signal is active in State Signals yet.\n"
            "→ Run **Observe logs** or **Check system state**, then watch this panel after the system responds."
        )
    lines = ["→ Active signal(s) detected in State Signals:"]
    for k in active:
        label = _SIGNAL_HUMAN.get(k, k.replace("_", " "))
        lines.append(f"→ {label}")
    return "\n".join(lines)


def step_feedback_payload(state: Any, available_actions: List[Any], scenario_id: str) -> Dict[str, str]:
    if not is_beginner_module(scenario_id):
        return {}

    latest_action = state.action_history[-1] if getattr(state, "action_history", []) else None
    latest_event = state.system_events[-1] if getattr(state, "system_events", []) else None
    conditions = getattr(state, "system_conditions", {}) or {}
    active_conditions = [k for k, v in conditions.items() if v]
    observed = list(getattr(state, "learning_data", {}).get("beginner_signals_observed", []) or [])

    if scenario_id == "beginner_signals":
        if not latest_action:
            return {
                "what_happened": "→ Session started in observation mode (no scoring pressure).",
                "why_it_happened": "→ This module is only about reading the environment before you conclude anything.",
                "what_it_means": _signals_feedback_lines(active_conditions)
                + "\n→ Next: run **Observe logs**, then **Check system state**, and read State Signals.",
            }

        aid = latest_action.get("action_id", "")
        failed = latest_action.get("actually_failed", False)
        alabel = latest_action.get("action_label") or aid

        if aid == "act_observe_logs":
            wh = (
                "→ You reviewed event logs for recent system and defender activity."
                + (" The read did not complete cleanly." if failed else " New entries should reflect the last interaction.")
            )
            wy = (
                "→ Logs are the first place defenders leave traces of automated reactions (filters, blocks, jitter)."
                if not failed
                else "→ The system sometimes resists passive reads under noise—try again next turn."
            )
            wm = _signals_feedback_lines(active_conditions)
            wm += (
                "\n→ In real operations, analysts treat log deltas as weak signals that must be cross-checked with state."
                if not failed
                else "\n→ Retry observation when execution fails; the teaching goal is consistent reading practice."
            )
            return {"what_happened": wh, "why_it_happened": wy, "what_it_means": wm}

        if aid == "act_check_state":
            wh = (
                "→ You opened consolidated **State Signals** to see which defensive behaviors are marked on."
                if not failed
                else "→ The state read did not complete; signals may be unchanged this turn."
            )
            wy = (
                "→ State Signals summarize posture changes (validation, access, timing, etc.) in one glance."
                if not failed
                else "→ Transient failures happen; the panel still reflects the last coherent snapshot."
            )
            wm = _signals_feedback_lines(active_conditions)
            wm += "\n→ Next: match what you see to one **Identify** option that names the same pattern."
            return {"what_happened": wh, "why_it_happened": wy, "what_it_means": wm}

        if aid.startswith("act_beginner_identify_"):
            sig_key = _IDENTIFY_TO_SIGNAL.get(aid)
            if sig_key and sig_key in observed and not failed:
                return {
                    "what_happened": f"→ You labeled the situation as **{_SIGNAL_HUMAN.get(sig_key, sig_key)}**.",
                    "why_it_happened": "→ That label matches a signal the simulation recorded from defender reactions.",
                    "what_it_means": "→ You connected an observation to a named defensive pattern—"
                    "the same skill you will later phrase as a formal hypothesis in the next module.",
                }
            if sig_key and sig_key not in observed:
                return {
                    "what_happened": f"→ You chose **{_SIGNAL_HUMAN.get(sig_key, sig_key)}**, but State Signals have not shown that pattern yet.",
                    "why_it_happened": "→ Identification should track evidence, not guesswork—wait for logs/state after defender moves.",
                    "what_it_means": _signals_feedback_lines(active_conditions)
                    + "\n→ Re-read State Signals after the next **Observe logs** / **Check system state**.",
                }
            return {
                "what_happened": "→ Identification step did not complete.",
                "why_it_happened": "→ The action may have been interrupted; try again when available.",
                "what_it_means": "→ Ground labels in what State Signals currently show.",
            }

        wh = f"→ You ran `{alabel}` ({aid})." + (" It did not succeed." if failed else "")
        wy = (
            latest_event.get("message", "The system processed your action.")
            if latest_event
            else "The system updated internal state."
        )
        wy = f"→ {wy}"
        wm = _signals_feedback_lines(active_conditions)
        return {"what_happened": wh, "why_it_happened": wy, "what_it_means": wm}

    # Other beginner modules — richer than raw condition dumps
    if latest_action:
        action_name = latest_action.get("action_label") or latest_action.get("action_id", "action")
        action_failed = latest_action.get("actually_failed", False)
        what_happened = (
            f"→ You executed “{action_name}” and it "
            f"{'did not complete as intended' if action_failed else 'completed'} this turn."
        )
    else:
        what_happened = "→ No action has been executed yet in this module."

    if latest_event:
        why_happened = f"→ {latest_event.get('message', 'The system responded to your last interaction.')}"
    else:
        why_happened = "→ The system is waiting for your first guided step."

    if active_conditions:
        human = ", ".join(_SIGNAL_HUMAN.get(k, k) for k in active_conditions)
        what_it_means = (
            "→ Defensive patterns currently visible include: "
            f"{human}.\n→ Tie your next step to one concrete signal before claiming a full theory."
        )
    else:
        what_it_means = (
            "→ No behavioral signal flags are on yet—keep observing until the system shows a change, "
            "then explain what it implies for your next move."
        )

    next_available = [a for a in (available_actions or []) if getattr(a, "available", False)]
    if next_available:
        what_it_means += f"\n→ Suggested next action: {next_available[0].label}."

    return {
        "what_happened": what_happened,
        "why_it_happened": why_happened,
        "what_it_means": what_it_means,
    }
