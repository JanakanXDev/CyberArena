"""Minimal test that writes a simple one-result-per-line file."""
import sys
from pathlib import Path
sys.path.insert(0, '.')
import engine

results = []
def R(tag, msg): results.append(f"{tag}|{msg}")

MODES = ["guided_simulation", "attacker_campaign", "defender_campaign", "playground"]
SCENARIOS = ["level_0_tutorial", "input_trust_failures", "linux_privesc", "network_breach"]

# BOOT TEST
for mode in MODES:
    for scenario in SCENARIOS:
        try:
            state = engine.reset_game(mode, 'medium', scenario)
            ok = state and 'availableActions' in state
            R("BOOT-PASS" if ok else "BOOT-FAIL", f"{mode}|{scenario}")
        except Exception as e:
            R("BOOT-FAIL", f"{mode}|{scenario}|{str(e)[:60]}")

# TUTORIAL WIN TEST
for mode in MODES:
    won = False
    for _ in range(5):
        try:
            state = engine.reset_game(mode, 'medium', 'level_0_tutorial')
            engine.configure_session_focus('attacker', 'web_server')
            state = engine.process_action('act_gather_evidence')
            state = engine.process_action('hypothesis:hyp_tutorial')
            if state.get('scenarioState') == 'victory':
                won = True
                break
        except: pass
    R("TUT-PASS" if won else "TUT-FAIL", mode)

# GUIDED WIN TEST
won = False
for _ in range(10):
    try:
        state = engine.reset_game('guided_simulation', 'medium', 'input_trust_failures')
        engine.configure_session_focus('attacker', 'web_server')
        state = engine.process_action('act_map_boundaries')
        state = engine.process_action('act_trigger_exception')
        for j in range(5):
            state = engine.process_action('act_corrupt_session')
            ah = state.get('actionHistory', [])
            if any(h.get('action_id') == 'act_corrupt_session' and not h.get('actually_failed') for h in ah):
                break
        state = engine.process_action('hypothesis:hyp_validation_layer')
        state = engine.process_action('hypothesis:hyp_state_persistence')
        if state.get('scenarioState') == 'victory':
            won = True
            break
    except Exception as e:
        R("GUIDED-ERR", str(e)[:80])
        break
R("GUIDED-PASS" if won else "GUIDED-FAIL", "guided x broken_trust")

# ATTACKER WIN TEST
won = False
for i in range(15):
    try:
        state = engine.reset_game('attacker_campaign', 'medium', 'input_trust_failures')
        cfg = engine.configure_session_focus('attacker', 'web_server')
        for act in cfg.get('availableActions', []):
            if act.get('type') == 'escalate':
                state = engine.process_action(act['id'])
                ah = state.get('actionHistory', [])
                last = next((h for h in reversed(ah) if h.get('action_id') == act['id']), None)
                if last and not last.get('actually_failed') and state.get('scenarioState') == 'victory':
                    won = True
                    R("ATT-PASS", f"via {act['id']} on run {i+1}")
                    break
            if won or state.get('scenarioState') != 'active':
                break
        if won:
            break
    except Exception as e:
        R("ATT-ERR", str(e)[:80])
        break
if not won:
    state_focused = engine.configure_session_focus('attacker', 'web_server') if engine.current_engine else {}
    R("ATT-FAIL", f"attacker never won in 15 runs, last_state={engine.current_engine.state.scenario_state if engine.current_engine else 'N/A'}")

# DEFENDER WIN TEST
won = False
for _ in range(5):
    try:
        state = engine.reset_game('defender_campaign', 'medium', 'input_trust_failures')
        engine.configure_session_focus('defender', 'web_server')
        state = engine.process_action('act_audit_cron')
        state = engine.process_action('hypothesis:hyp_persistence_method')
        if state.get('scenarioState') == 'victory':
            won = True
            break
    except Exception as e:
        R("DEF-ERR", str(e)[:80])
        break
R("DEF-PASS" if won else "DEF-FAIL", "defender x broken_trust")

# PLAYGROUND TEST
try:
    state = engine.reset_game('playground', 'medium', 'input_trust_failures')
    engine.configure_session_focus('attacker', 'web_server')
    wc = engine.current_engine.state.win_conditions if engine.current_engine else ["unknown"]
    R("PG-PASS" if not wc else "PG-WARN", f"playground win_conditions={wc}")
except Exception as e:
    R("PG-FAIL", str(e)[:80])

# STRUCTURAL TEST
for s in ['linux_privesc', 'network_breach']:
    try:
        state = engine.reset_game('guided_simulation', 'medium', s)
        name = state.get('scenarioName', '')
        R("STRUCT-INFO", f"{s}='{name}'")
    except Exception as e:
        R("STRUCT-FAIL", str(e)[:80])

# Write and print results
content = "\n".join(results)
results_path = Path(__file__).with_name("test_minimal_results.txt")
with open(results_path, "w", encoding="ascii", errors="replace") as f:
    f.write(content + "\n")
    pass_count = sum(1 for r in results if '-PASS' in r)
    fail_count = sum(1 for r in results if '-FAIL' in r)
    warn_count = sum(1 for r in results if '-WARN' in r or '-ERR' in r or '-INFO' in r)
    f.write(f"\nSUMMARY: PASS={pass_count} FAIL={fail_count} OTHER={warn_count}\n")
    f.write("RESULT: " + ("ALL PASS" if fail_count == 0 else "SOME FAIL") + "\n")

for r in results:
    print(r)

sys.exit(0 if all('-FAIL' not in r and '-ERR' not in r for r in results) else 1)
