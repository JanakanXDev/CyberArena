"""
Beginner learning path metadata and additive feedback helpers.
This module does not change simulation mechanics.
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
        "goal": "Read logs and system state signals before acting.",
        "prompt": "Inspect the system signal first, then form a simple observation.",
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


def is_beginner_module(scenario_id: str) -> bool:
    return scenario_id in BEGINNER_MODULES


def learning_path_payload(scenario_id: str) -> Dict[str, Any]:
    module = BEGINNER_MODULES.get(scenario_id)
    if not module:
        return {}
    module_index = BEGINNER_MODULE_ORDER.index(scenario_id)
    return {
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


def step_feedback_payload(state: Any, available_actions: List[Any], scenario_id: str) -> Dict[str, str]:
    if not is_beginner_module(scenario_id):
        return {}

    latest_action = state.action_history[-1] if getattr(state, "action_history", []) else None
    latest_event = state.system_events[-1] if getattr(state, "system_events", []) else None
    active_conditions = [k for k, v in getattr(state, "system_conditions", {}).items() if v]

    if latest_action:
        action_name = latest_action.get("action_id", "action")
        action_failed = latest_action.get("actually_failed", False)
        what_happened = (
            f"You executed '{action_name}' and it {'failed' if action_failed else 'completed'} this turn."
        )
    else:
        what_happened = "No action has been executed yet in this module."

    if latest_event:
        why_happened = latest_event.get("message", "The system responded to your last interaction.")
    else:
        why_happened = "The system is waiting for your first guided step."

    next_available = [a for a in (available_actions or []) if getattr(a, "available", False)]
    next_hint = next_available[0].label if next_available else "review your hypothesis panel"

    what_it_means = (
        f"Active signals now: {', '.join(active_conditions) if active_conditions else 'none'}. "
        f"Next guided step: {next_hint}."
    )

    return {
        "what_happened": what_happened,
        "why_it_happened": why_happened,
        "what_it_means": what_it_means,
    }
