"""Debug guided mode step by step."""
import sys
sys.path.insert(0, '.')
import engine

for attempt in range(5):
    state = engine.reset_game('guided_simulation', 'medium', 'input_trust_failures')
    engine.configure_session_focus('attacker', 'web_server')
    print(f"\nAttempt {attempt+1}:")
    
    # Step 1: act_map_boundaries (probe, low fail chance)
    state = engine.process_action('act_map_boundaries')
    ah = state.get('actionHistory', [])
    last = ah[-1] if ah else {}
    print(f"  act_map_boundaries: failed={last.get('actually_failed')}")
    
    # Step 2: act_trigger_exception (inspect, should succeed)
    state = engine.process_action('act_trigger_exception')
    ah = state.get('actionHistory', [])
    last = ah[-1] if ah else {}
    print(f"  act_trigger_exception: failed={last.get('actually_failed')}")
    
    # Step 3: act_corrupt_session (escalate, may fail)
    for j in range(5):
        state = engine.process_action('act_corrupt_session')
        ah = state.get('actionHistory', [])
        corrupt_successes = [h for h in ah if h.get('action_id') == 'act_corrupt_session' and not h.get('actually_failed')]
        if corrupt_successes:
            print(f"  act_corrupt_session: succeeded on inner try {j+1}")
            break
        else:
            print(f"  act_corrupt_session: failed (inner try {j+1}), pressure={state.get('pressure')}")
    
    # Step 4: validate hypotheses
    state = engine.process_action('hypothesis:hyp_validation_layer')
    hyps = state.get('hypotheses', [])
    for h in hyps:
        if h['id'] == 'hyp_validation_layer':
            print(f"  hyp_validation_layer: tested={h.get('tested')}, validated={h.get('validated')}")
    
    state = engine.process_action('hypothesis:hyp_state_persistence')
    hyps = state.get('hypotheses', [])
    for h in hyps:
        if h['id'] == 'hyp_state_persistence':
            print(f"  hyp_state_persistence: tested={h.get('tested')}, validated={h.get('validated')}")
    
    ss = state.get('scenarioState', 'unknown')
    print(f"  Final state: {ss}, pressure={state.get('pressure')}, stability={state.get('stability')}")
    
    if ss == 'victory':
        print("  *** WON! ***")
        break

print("\nDone.")
