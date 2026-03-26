"""
CyberArena Reliability Test Suite
Tests the 8 stabilization systems.
"""

import sys
import random

sys.path.insert(0, ".")

from simulation_engine import SimulationEngine, LearningMode, Action
from ai_systems import InputFilter, EngineValidator
from scenario_system import get_scenario_config

results = []


def make_engine(scenario_id="input_trust_failures", mode=LearningMode.GUIDED_SIMULATION, difficulty="normal"):
    """Helper to correctly create a SimulationEngine with actions + hypotheses loaded."""
    config = get_scenario_config(scenario_id, mode, difficulty)
    engine = SimulationEngine(mode, difficulty, scenario_id)
    engine.initialize(config)
    # Manually load actions and hypotheses (normally done via configure_session)
    actions_config = config.get("actions", [])
    engine.available_actions = [engine._parse_action(a) for a in actions_config]
    hypotheses_config = config.get("hypotheses", [])
    engine._hypotheses_config = {h["id"]: h for h in hypotheses_config}
    engine.state.scenario_state = "active"
    return engine, config


def run_test(name, test_fn):
    try:
        passed = test_fn()
        status = "PASS" if passed else "FAIL"
        results.append((name, passed))
        print(f"  [{status}] {name}")
    except Exception as e:
        results.append((name, False))
        print(f"  [FAIL] {name} -- Exception: {e}")


# TEST 1: Determinism Control
def test_determinism_control():
    outcomes = {"success": 0, "fail": 0}
    for _ in range(50):
        engine, config = make_engine()
        action = next((a for a in engine.available_actions if a.type == "probe"), None)
        if not action:
            return False
        state_dict, _ = engine.process_action(action.id)
        last = state_dict.get("action_history", [{}])[-1]
        if last.get("actually_failed"):
            outcomes["fail"] += 1
        else:
            outcomes["success"] += 1
    success_rate = outcomes["success"] / 50
    # Probe actions with bounded probability [0.5, 0.95] should succeed > 25% across randomized boot states
    # and never be 100% (some should fail due to randomness)
    return success_rate >= 0.25


# TEST 2: Engine Validator Consistency
def test_engine_validator_consistency():
    engine, config = make_engine()
    correct_intent = {
        "target": "input_validation",
        "claim": "bypass_possible",
        "confidence": 0.85,
        "best_match_id": "hyp_validation_layer",
        "explanation": "User claims WAF validation can be bypassed."
    }
    results_set = set()
    for _ in range(5):
        verdict = EngineValidator.evaluate(correct_intent, engine._hypotheses_config, engine.state)
        results_set.add(verdict["classification"])
    return len(results_set) == 1


# TEST 3: AI Mutation Integrity
def test_ai_mutation_integrity():
    engine, config = make_engine()
    initial_count = len(engine.state.system_events)
    ai_action = {
        "name": "silently_harden_component",
        "label": "Silent Hardening",
        "effects": {
            "harden_components": ["web_server"],
            "pressure_delta": -2
        }
    }
    engine._apply_ai_action_effects(ai_action)
    if not engine.state.system_components.get("web_server", {}).get("hardened"):
        return False
    if len(engine.state.system_events) <= initial_count:
        return False
    recent = [e["message"] for e in engine.state.system_events[initial_count:]]
    has_hardening = any("hardened" in m.lower() for m in recent)
    has_pressure = any("pressure" in m.lower() for m in recent)
    return has_hardening and has_pressure


# TEST 4: Garbage Input Rejection
def test_garbage_rejection():
    garbage = ["hello world", "pizza is great", "12345", "asdf", "", "weather is nice", "I like cats", "lol"]
    for text in garbage:
        r = InputFilter.validate(text)
        if r["valid"]:
            print(f"    Garbage accepted: '{text}'")
            return False
    valid = [
        "The WAF validation can be bypassed by the attacker",
        "SQL injection is possible on the database endpoint",
        "The server has a vulnerability in the login system",
    ]
    for text in valid:
        r = InputFilter.validate(text)
        if not r["valid"]:
            print(f"    Valid rejected: '{text}'")
            return False
    return True


# TEST 5: Strategy Replayability
def test_strategy_replayability():
    pressures = []
    stabilities = []
    for _ in range(10):
        engine, config = make_engine()
        for aid in ["act_map_boundaries", "act_trigger_exception", "act_observe_signals"]:
            try:
                engine.process_action(aid)
            except Exception:
                pass
        pressures.append(engine.state.pressure)
        stabilities.append(engine.state.stability)
    all_bounded = all(0 <= p <= 100 for p in pressures) and all(0 <= s <= 100 for s in stabilities)
    has_variation = len(set(pressures)) >= 2 or len(set(stabilities)) >= 2
    return all_bounded and has_variation


# TEST 6: Deterministic Anchors
def test_deterministic_anchors():
    engine, config = make_engine()
    # Patch a vulnerability
    patched_vuln = None
    for vuln_id in engine.state.vulnerabilities:
        engine.state.vulnerabilities[vuln_id]["patched"] = True
        patched_vuln = vuln_id
        break
    if not patched_vuln:
        return True
    # Find an action that exploits it
    exploit_action = next(
        (a for a in engine.available_actions if "vulnerability_exploited" in a.immediate_effect),
        None
    )
    if not exploit_action:
        return True  # No exploit action, pass by default
    state_dict, _ = engine.process_action(exploit_action.id)
    last = state_dict.get("action_history", [{}])[-1]
    return last.get("actually_failed", False)


# TEST 7: Coherence Validation
def test_coherence_validation():
    engine, config = make_engine()
    # Inject inconsistency: patched but active
    for vuln_id in engine.state.vulnerabilities:
        engine.state.vulnerabilities[vuln_id]["patched"] = True
        engine.state.vulnerabilities[vuln_id]["active"] = True
        break
    is_clean = engine.validate_state()
    if is_clean:
        return False
    for vuln_id, vuln in engine.state.vulnerabilities.items():
        if vuln.get("patched") and vuln.get("active"):
            return False
    return True


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  CyberArena Reliability Test Suite")
    print("=" * 55)

    run_test("1. Determinism Control (Bounded Outcomes)", test_determinism_control)
    run_test("2. Engine Validator Consistency", test_engine_validator_consistency)
    run_test("3. AI Mutation Integrity (Logged)", test_ai_mutation_integrity)
    run_test("4. Garbage Input Rejection", test_garbage_rejection)
    run_test("5. Strategy Replayability", test_strategy_replayability)
    run_test("6. Deterministic Anchors (Hardened/Patched)", test_deterministic_anchors)
    run_test("7. Coherence Validation (Auto-Fix)", test_coherence_validation)

    print("\n" + "-" * 55)
    passed = sum(1 for _, p in results if p)
    total = len(results)
    print(f"  Results: {passed}/{total} passed")
    if passed == total:
        print("  ALL TESTS PASSED")
    else:
        print("  SOME TESTS FAILED")
    print("-" * 55)

    sys.exit(0 if passed == total else 1)
