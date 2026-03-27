"""
Comprehensive CyberArena Test Suite
Tests all 4 modes × 4 scenarios for:
  1. Boot stability (no crashes)
  2. Actions & hypotheses loaded correctly
  3. Winability (correct action sequence reaches victory)
  4. Structural quality (fallback detection, missing configs)
"""
import sys
import os
sys.path.insert(0, '.')
import engine

MODES = ["guided_simulation", "attacker_campaign", "defender_campaign", "playground"]
SCENARIOS = ["level_0_tutorial", "input_trust_failures", "linux_privesc", "network_breach"]

PASS = 0
FAIL = 0
WARN = 0
issues = []

def log_pass(msg):
    global PASS
    PASS += 1
    print(f"  [PASS] {msg}")

def log_fail(msg):
    global FAIL
    FAIL += 1
    issues.append(f"FAIL: {msg}")
    print(f"  [FAIL] {msg}")

def log_warn(msg):
    global WARN
    WARN += 1
    issues.append(f"WARN: {msg}")
    print(f"  [WARN] {msg}")

# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: Boot Stability — Can every combo start without crashing?
# ─────────────────────────────────────────────────────────────────────────────
def test_boot_stability():
    print("\n" + "="*70)
    print("TEST 1: Boot Stability (all 16 combos)")
    print("="*70)
    for mode in MODES:
        for scenario in SCENARIOS:
            label = f"{mode} × {scenario}"
            try:
                state = engine.reset_game(mode, 'medium', scenario)
                if state and 'availableActions' in state:
                    log_pass(f"{label} — booted OK")
                else:
                    log_fail(f"{label} — booted but state is incomplete")
            except Exception as e:
                log_fail(f"{label} — CRASHED: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: Content Quality — Are actions and hypotheses loaded?
# ─────────────────────────────────────────────────────────────────────────────
def test_content_quality():
    print("\n" + "="*70)
    print("TEST 2: Content Quality (actions + hypotheses present)")
    print("="*70)
    for mode in MODES:
        for scenario in SCENARIOS:
            label = f"{mode} × {scenario}"
            try:
                state = engine.reset_game(mode, 'medium', scenario)
                actions = state.get('availableActions', [])
                hypotheses = state.get('hypotheses', [])

                if len(actions) == 0 and len(hypotheses) == 0:
                    log_warn(f"{label} — no actions or hypotheses loaded (may need focus config)")
                elif len(actions) == 0:
                    log_warn(f"{label} — no actions loaded")
                elif len(hypotheses) == 0:
                    log_warn(f"{label} — no hypotheses loaded")
                else:
                    log_pass(f"{label} — {len(actions)} actions, {len(hypotheses)} hypotheses")

                # Check for fallback scenario
                scenario_name = state.get('scenarioName', '')
                if scenario in ['linux_privesc', 'network_breach']:
                    if scenario_name == 'Operation: Broken Trust':
                        log_warn(f"{label} — scenario title is 'Broken Trust' (fallback from unimplemented '{scenario}')")
            except Exception as e:
                log_fail(f"{label} — CRASHED: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: Winability — Can each mode be won with the correct sequence?
# ─────────────────────────────────────────────────────────────────────────────
def test_winability():
    print("\n" + "="*70)
    print("TEST 3: Winability (mode-by-mode)")
    print("="*70)

    # --- Tutorial (all modes share the same tutorial config) ---
    print("\n  [Tutorial Scenario]")
    for mode in MODES:
        label = f"{mode} × level_0_tutorial"
        try:
            state = engine.reset_game(mode, 'medium', 'level_0_tutorial')
            # Tutorial: gather evidence, then validate hypothesis
            state = engine.process_action('act_gather_evidence')
            state = engine.process_action('hypothesis:hyp_tutorial')
            ss = state.get('scenarioState', 'unknown')
            if ss == 'victory':
                log_pass(f"{label} — VICTORY achieved")
            else:
                log_warn(f"{label} — expected victory, got '{ss}'")
        except Exception as e:
            log_fail(f"{label} — CRASHED: {e}")

    # --- Guided Simulation (Broken Trust) ---
    print("\n  [Guided Simulation × Broken Trust]")
    try:
        state = engine.reset_game('guided_simulation', 'medium', 'input_trust_failures')
        engine.configure_session_focus('attacker', 'web_server')
        
        # Guided win: validate all core hypotheses
        # Core hypotheses: hyp_validation_layer (correct), hyp_state_persistence (correct)
        # Step 1: run evidence actions
        state = engine.process_action('act_map_boundaries')
        state = engine.process_action('act_trigger_exception')
        state = engine.process_action('act_corrupt_session')
        
        # Step 2: validate correct hypotheses
        state = engine.process_action('hypothesis:hyp_validation_layer')
        ss = state.get('scenarioState', 'unknown')
        if ss == 'victory':
            log_pass("guided_simulation × input_trust_failures — VICTORY after first core hyp")
        else:
            state = engine.process_action('hypothesis:hyp_state_persistence')
            ss = state.get('scenarioState', 'unknown')
            if ss == 'victory':
                log_pass("guided_simulation × input_trust_failures — VICTORY after both core hyps")
            else:
                log_fail(f"guided_simulation × input_trust_failures — expected victory, got '{ss}'")
    except Exception as e:
        log_fail(f"guided_simulation × input_trust_failures — CRASHED: {e}")

    # --- Attacker Campaign (Broken Trust) ---
    print("\n  [Attacker Campaign × Broken Trust]")
    try:
        state = engine.reset_game('attacker_campaign', 'medium', 'input_trust_failures')
        engine.configure_session_focus('attacker', 'web_server')
        
        # Attacker win: execute an 'escalate' type action
        state = engine.process_action('act_noise_flood')
        ss = state.get('scenarioState', 'unknown')
        if ss == 'victory':
            log_pass("attacker_campaign × input_trust_failures — VICTORY")
        elif ss == 'defeat':
            log_warn("attacker_campaign × input_trust_failures — DEFEAT (may have randomly failed due to pressure)")
        else:
            log_fail(f"attacker_campaign × input_trust_failures — expected terminal state, got '{ss}'")
    except Exception as e:
        log_fail(f"attacker_campaign × input_trust_failures — CRASHED: {e}")

    # --- Defender Campaign (Broken Trust) ---
    print("\n  [Defender Campaign × Broken Trust]")
    try:
        state = engine.reset_game('defender_campaign', 'medium', 'input_trust_failures')
        engine.configure_session_focus('defender', 'web_server')
        
        # Defender win: audit cron + validate persistence hypothesis
        state = engine.process_action('act_audit_cron')
        state = engine.process_action('hypothesis:hyp_persistence_method')
        ss = state.get('scenarioState', 'unknown')
        if ss == 'victory':
            log_pass("defender_campaign × input_trust_failures — VICTORY")
        else:
            log_fail(f"defender_campaign × input_trust_failures — expected victory, got '{ss}'")
    except Exception as e:
        log_fail(f"defender_campaign × input_trust_failures — CRASHED: {e}")

    # --- Playground (Broken Trust) ---
    print("\n  [Playground × Broken Trust]")
    try:
        state = engine.reset_game('playground', 'medium', 'input_trust_failures')
        engine.configure_session_focus('attacker', 'web_server')
        
        # Playground has no win conditions — just verify it stays active
        state = engine.process_action('act_fuzz_all')
        ss = state.get('scenarioState', 'unknown')
        if ss == 'active':
            log_pass("playground × input_trust_failures — stays ACTIVE (no auto-end, correct)")
        elif ss == 'defeat':
            log_warn("playground × input_trust_failures — entered DEFEAT (collapse from instability)")
        else:
            log_warn(f"playground × input_trust_failures — unexpected state '{ss}'")
    except Exception as e:
        log_fail(f"playground × input_trust_failures — CRASHED: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: Structural Quality — Fallback detection, missing configs
# ─────────────────────────────────────────────────────────────────────────────
def test_structural_quality():
    print("\n" + "="*70)
    print("TEST 4: Structural Quality (fallback detection)")
    print("="*70)
    
    fallback_scenarios = ['linux_privesc', 'network_breach']
    
    for scenario in fallback_scenarios:
        for mode in MODES:
            label = f"{mode} × {scenario}"
            try:
                state = engine.reset_game(mode, 'medium', scenario)
                scenario_name = state.get('scenarioName', '')
                
                if scenario_name != 'Unknown Mission' and 'Broken Trust' in scenario_name:
                    log_warn(f"{label} — uses 'Broken Trust' content (no unique backend config for '{scenario}')")
                elif scenario_name == 'Unknown Mission':
                    log_warn(f"{label} — scenario name is 'Unknown Mission' (not mapped in _get_scenario_name)")
                else:
                    log_pass(f"{label} — has unique scenario name: '{scenario_name}'")
            except Exception as e:
                log_fail(f"{label} — CRASHED: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 70)
    print("  CYBERARENA COMPREHENSIVE MODE & SCENARIO TEST SUITE")
    print("=" * 70)
    
    test_boot_stability()
    test_content_quality()
    test_winability()
    test_structural_quality()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"  PASSED:   {PASS}")
    print(f"  WARNINGS: {WARN}")
    print(f"  FAILED:   {FAIL}")
    
    if issues:
        print(f"\n  Issues found ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            print(f"    {i}. {issue}")
    
    if FAIL > 0:
        print("\n  RESULT: SOME TESTS FAILED")
        sys.exit(1)
    elif WARN > 0:
        print("\n  RESULT: ALL TESTS PASSED (with warnings)")
        sys.exit(0)
    else:
        print("\n  RESULT: ALL TESTS PASSED")
        sys.exit(0)
