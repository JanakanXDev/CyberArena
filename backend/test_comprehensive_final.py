"""
FINAL CyberArena Comprehensive Test Suite - v2
Handles randomness by using smarter win strategies.
"""
import sys
sys.path.insert(0, '.')
import engine

PASS_COUNT = 0
FAIL_COUNT = 0
WARN_COUNT = 0
log = []

def ok(msg):
    global PASS_COUNT
    PASS_COUNT += 1
    log.append(f"[PASS] {msg}")

def fail(msg):
    global FAIL_COUNT
    FAIL_COUNT += 1
    log.append(f"[FAIL] {msg}")

def warn(msg):
    global WARN_COUNT
    WARN_COUNT += 1
    log.append(f"[WARN] {msg}")

def note(msg):
    log.append(f"[INFO] {msg}")

MODES = ["guided_simulation", "attacker_campaign", "defender_campaign", "playground"]
SCENARIOS = ["level_0_tutorial", "input_trust_failures", "linux_privesc", "network_breach"]

# ─────────────────────────────────
# TEST 1: Boot Stability
# ─────────────────────────────────
note("TEST 1: BOOT STABILITY (16 combos)")
for mode in MODES:
    for scenario in SCENARIOS:
        label = f"{mode} x {scenario}"
        try:
            state = engine.reset_game(mode, 'medium', scenario)
            if state and 'availableActions' in state:
                ok(f"boot: {label}")
            else:
                fail(f"boot: {label} -- missing availableActions")
        except Exception as e:
            fail(f"boot: {label} -- CRASHED: {e}")

# ─────────────────────────────────
# TEST 2: Content Quality
# ─────────────────────────────────
note("TEST 2: CONTENT QUALITY")
for mode in MODES:
    for scenario in SCENARIOS:
        label = f"{mode} x {scenario}"
        try:
            state = engine.reset_game(mode, 'medium', scenario)
            acts = len(state.get('availableActions', []))
            hyps = len(state.get('hypotheses', []))
            if acts > 0 and hyps > 0:
                ok(f"content: {label} -- {acts} actions, {hyps} hyps")
            elif acts == 0 and hyps == 0:
                warn(f"content: {label} -- no actions or hyps (needs focus config)")
            else:
                warn(f"content: {label} -- {acts} actions, {hyps} hyps")
        except Exception as e:
            fail(f"content: {label} -- CRASHED: {e}")

# ─────────────────────────────────
# TEST 3: Winability with smart strategies
# ─────────────────────────────────
note("TEST 3: WINABILITY")

# --- Tutorial (all modes share same config) ---
note("  Tutorial scenario (all modes)")
for mode in MODES:
    label = f"{mode} x tutorial"
    won = False
    for attempt in range(5):
        try:
            state = engine.reset_game(mode, 'medium', 'level_0_tutorial')
            engine.configure_session_focus('attacker', 'web_server')
            state = engine.process_action('act_gather_evidence')
            state = engine.process_action('hypothesis:hyp_tutorial')
            ss = state.get('scenarioState', 'unknown')
            if ss == 'victory':
                won = True
                ok(f"win: {label} on attempt {attempt+1}")
                break
        except Exception as e:
            fail(f"win: {label} -- CRASHED: {e}")
            break
    if not won:
        fail(f"win: {label} -- never won in 5 attempts")

# --- Guided Simulation: validate all core hypotheses ---
note("  Guided Simulation x Broken Trust")
won = False
for attempt in range(8):
    try:
        state = engine.reset_game('guided_simulation', 'medium', 'input_trust_failures')
        engine.configure_session_focus('attacker', 'web_server')
        
        # Run evidence-gathering actions; retry escalate type until it succeeds
        state = engine.process_action('act_map_boundaries')  # probe type, high success
        
        # act_trigger_exception (inspect type, high success)
        state = engine.process_action('act_trigger_exception')
        
        # act_corrupt_session (escalate type, can randomly fail) — retry up to 5x
        for _ in range(5):
            state = engine.process_action('act_corrupt_session')
            history = state.get('actionHistory', [])
            last = next((h for h in reversed(history) if h.get('action_id') == 'act_corrupt_session'), None)
            if last and not last.get('actually_failed'):
                break  # success
        
        # Now validate the core hypotheses
        state = engine.process_action('hypothesis:hyp_validation_layer')
        state = engine.process_action('hypothesis:hyp_state_persistence')
        ss = state.get('scenarioState', 'unknown')
        if ss == 'victory':
            won = True
            ok(f"win: guided x broken_trust on attempt {attempt+1}")
            break
        else:
            note(f"  guided attempt {attempt+1}: final state={ss}")
    except Exception as e:
        fail(f"win: guided x broken_trust -- CRASHED: {e}")
        break
if not won:
    fail(f"win: guided x broken_trust -- never won in 8 attempts")


# --- Attacker Campaign: find and try all escalate type actions --- 
note("  Attacker Campaign x Broken Trust")
won = False
for attempt in range(12):
    try:
        state = engine.reset_game('attacker_campaign', 'medium', 'input_trust_failures')
        cfg_state = engine.configure_session_focus('attacker', 'web_server')
        
        # Collect escalate-type action IDs AFTER session is configured
        acts = cfg_state.get('availableActions', [])
        escalate_ids = [a['id'] for a in acts if a.get('type') in ('escalate',)]
        if 'act_focused_attack_web_server' not in escalate_ids:
            escalate_ids.append('act_focused_attack_web_server')
        
        note(f"  attacker attempt {attempt+1}: escalate_ids={escalate_ids}, pressure={cfg_state.get('pressure')}")
        
        # Try each escalate action until one succeeds and triggers win
        for act_id in escalate_ids:
            if state.get('scenarioState', 'active') != 'active':
                break
            state = engine.process_action(act_id)
            ah = state.get('actionHistory', [])
            last = next((h for h in reversed(ah) if h.get('action_id') == act_id), None)
            act_failed = last.get('actually_failed') if last else True
            note(f"    {act_id}: failed={act_failed}, state={state.get('scenarioState')}, pressure={state.get('pressure')}")
            if not act_failed:
                ss = state.get('scenarioState', 'unknown')
                if ss == 'victory':
                    won = True
                    ok(f"win: attacker x broken_trust via {act_id} on attempt {attempt+1}")
                    break
        
        if won:
            break
        ss = state.get('scenarioState', 'unknown')
        if ss == 'defeat':
            note(f"  attacker attempt {attempt+1}: defeat, retrying")
            continue
    except Exception as e:
        fail(f"win: attacker x broken_trust -- CRASHED: {e}")
        break
if not won:
    fail(f"win: attacker x broken_trust -- never won in 12 attempts")




# --- Defender Campaign: audit cron + validate persistence hypothesis ---
note("  Defender Campaign x Broken Trust")
won = False
for attempt in range(5):
    try:
        state = engine.reset_game('defender_campaign', 'medium', 'input_trust_failures')
        engine.configure_session_focus('defender', 'web_server')
        state = engine.process_action('act_audit_cron')
        state = engine.process_action('hypothesis:hyp_persistence_method')
        ss = state.get('scenarioState', 'unknown')
        if ss == 'victory':
            won = True
            ok(f"win: defender x broken_trust on attempt {attempt+1}")
            break
    except Exception as e:
        fail(f"win: defender x broken_trust -- CRASHED: {e}")
        break
if not won:
    fail(f"win: defender x broken_trust -- never won in 5 attempts")

# --- Playground: sandbox with no win condition ---
note("  Playground x Broken Trust (sandbox)")
try:
    state = engine.reset_game('playground', 'medium', 'input_trust_failures')
    engine.configure_session_focus('attacker', 'web_server')
    win_conds = engine.current_engine.state.win_conditions if engine.current_engine else []
    if not win_conds:
        ok("win: playground x broken_trust -- correctly has NO win conditions (sandbox)")
    else:
        warn(f"win: playground x broken_trust -- has {len(win_conds)} win conditions (unexpected)")
except Exception as e:
    fail(f"win: playground x broken_trust -- CRASHED: {e}")

# ─────────────────────────────────
# TEST 4: Structural Quality
# ─────────────────────────────────
note("TEST 4: STRUCTURAL QUALITY")
for scenario in ['linux_privesc', 'network_breach']:
    try:
        state = engine.reset_game('guided_simulation', 'medium', scenario)
        name = state.get('scenarioName', '')
        if 'Broken Trust' in name or name == 'Unknown Mission':
            warn(f"struct: '{scenario}' has no dedicated backend config (uses '{name}')")
        else:
            ok(f"struct: '{scenario}' has its own config ('{name}')")
    except Exception as e:
        fail(f"struct: {scenario} -- CRASHED: {e}")

# ─────────────────────────────────
# SUMMARY
# ─────────────────────────────────
result_txt = [
    "=" * 60,
    "CYBERARENA COMPREHENSIVE TEST RESULTS",
    "=" * 60,
    ""
] + [f"  {l}" for l in log] + [
    "",
    f"  PASSED:   {PASS_COUNT}",
    f"  WARNINGS: {WARN_COUNT}",
    f"  FAILED:   {FAIL_COUNT}",
    "",
    "  RESULT: " + ("PASSED" if FAIL_COUNT == 0 else "SOME TESTS FAILED")
]

for line in result_txt:
    print(line)

with open("backend/test_final_v2.txt", "w", encoding="ascii", errors="replace") as f:
    f.write("\n".join(result_txt))

sys.exit(0 if FAIL_COUNT == 0 else 1)
