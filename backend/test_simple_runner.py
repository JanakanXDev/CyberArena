"""Simple runner that writes results to a plain ASCII file."""
import sys
import os
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, 'backend')
import engine

MODES = ["guided_simulation", "attacker_campaign", "defender_campaign", "playground"]
SCENARIOS = ["level_0_tutorial", "input_trust_failures", "linux_privesc", "network_breach"]

results = []

def r(status, msg):
    results.append(f"[{status}] {msg}")

# TEST 1: Boot Stability
for mode in MODES:
    for scenario in SCENARIOS:
        label = f"{mode} x {scenario}"
        try:
            state = engine.reset_game(mode, 'medium', scenario)
            if state and 'availableActions' in state:
                r("PASS", f"BOOT: {label}")
            else:
                r("FAIL", f"BOOT: {label} - incomplete state")
        except Exception as e:
            r("FAIL", f"BOOT: {label} - {e}")

# TEST 2: Winability
# Tutorial (all modes)
for mode in MODES:
    label = f"{mode} x level_0_tutorial"
    try:
        state = engine.reset_game(mode, 'medium', 'level_0_tutorial')
        state = engine.process_action('act_gather_evidence')
        state = engine.process_action('hypothesis:hyp_tutorial')
        ss = state.get('scenarioState', 'unknown')
        if ss == 'victory':
            r("PASS", f"WIN: {label} -> VICTORY")
        else:
            r("WARN", f"WIN: {label} -> {ss}")
    except Exception as e:
        r("FAIL", f"WIN: {label} - {e}")

# Guided + Broken Trust
try:
    state = engine.reset_game('guided_simulation', 'medium', 'input_trust_failures')
    engine.configure_session_focus('attacker', 'web_server')
    state = engine.process_action('act_map_boundaries')
    state = engine.process_action('act_trigger_exception')
    state = engine.process_action('act_corrupt_session')
    state = engine.process_action('hypothesis:hyp_validation_layer')
    ss = state.get('scenarioState', 'unknown')
    if ss != 'victory':
        state = engine.process_action('hypothesis:hyp_state_persistence')
        ss = state.get('scenarioState', 'unknown')
    r("PASS" if ss == "victory" else "FAIL", f"WIN: guided x broken_trust -> {ss}")
except Exception as e:
    r("FAIL", f"WIN: guided x broken_trust - {e}")

# Attacker + Broken Trust (run 3x due to randomness)
att_won = False
for attempt in range(3):
    try:
        state = engine.reset_game('attacker_campaign', 'medium', 'input_trust_failures')
        engine.configure_session_focus('attacker', 'web_server')
        state = engine.process_action('act_noise_flood')
        ss = state.get('scenarioState', 'unknown')
        if ss == 'victory':
            att_won = True
            break
    except:
        pass
r("PASS" if att_won else "FAIL", f"WIN: attacker x broken_trust -> {'victory (after {0} attempts)'.format(attempt+1) if att_won else 'never won in 3 attempts'}")

# Defender + Broken Trust
try:
    state = engine.reset_game('defender_campaign', 'medium', 'input_trust_failures')
    engine.configure_session_focus('defender', 'web_server')
    state = engine.process_action('act_audit_cron')
    state = engine.process_action('hypothesis:hyp_persistence_method')
    ss = state.get('scenarioState', 'unknown')
    r("PASS" if ss == "victory" else "FAIL", f"WIN: defender x broken_trust -> {ss}")
except Exception as e:
    r("FAIL", f"WIN: defender x broken_trust - {e}")

# Playground
try:
    state = engine.reset_game('playground', 'medium', 'input_trust_failures')
    engine.configure_session_focus('attacker', 'web_server')
    state = engine.process_action('act_fuzz_all')
    ss = state.get('scenarioState', 'unknown')
    r("PASS" if ss in ("active", "defeat") else "WARN", f"WIN: playground x broken_trust -> {ss} (sandbox, no win expected)")
except Exception as e:
    r("FAIL", f"WIN: playground x broken_trust - {e}")

# TEST 3: Structural (fallback detection)
for scenario in ['linux_privesc', 'network_breach']:
    try:
        state = engine.reset_game('guided_simulation', 'medium', scenario)
        name = state.get('scenarioName', '')
        r("WARN", f"STRUCT: {scenario} -> scenarioName='{name}' (no unique backend config)")
    except Exception as e:
        r("FAIL", f"STRUCT: {scenario} - {e}")

# Write results
passes = sum(1 for r_ in results if r_.startswith("[PASS]"))
warns = sum(1 for r_ in results if r_.startswith("[WARN]"))
fails = sum(1 for r_ in results if r_.startswith("[FAIL]"))

output = []
output.append("CYBERARENA COMPREHENSIVE TEST RESULTS")
output.append("=" * 50)
output.append("")
for line in results:
    output.append(line)
output.append("")
output.append(f"PASSED: {passes}  WARNINGS: {warns}  FAILED: {fails}")
if fails == 0:
    output.append("RESULT: ALL TESTS PASSED" + (" (with warnings)" if warns else ""))
else:
    output.append("RESULT: SOME TESTS FAILED")

full_output = "\n".join(output)
print(full_output)

with open("backend/test_results.txt", "w", encoding="ascii", errors="replace") as f:
    f.write(full_output)
