"""Quick targeted debug to find exact failure reasons."""
import sys
sys.path.insert(0, '.')
import engine

print("--- Guided Simulation Win Debug ---")
state = engine.reset_game('guided_simulation', 'medium', 'input_trust_failures')
engine.configure_session_focus('attacker', 'web_server')

hyps = state.get('hypotheses', [])
acts = state.get('availableActions', [])
print(f"Actions: {[a['id'] for a in acts]}")
print(f"Hyps: {[h['id'] for h in hyps]}")

# Run all evidence-gathering actions
for act_id in ['act_map_boundaries', 'act_trigger_exception', 'act_corrupt_session']:
    state = engine.process_action(act_id)
    hist = state.get('actionHistory', [])
    if hist:
        last = hist[-1]
        print(f"  {act_id}: failed={last.get('actually_failed')}")

# Now validate hypotheses
for hyp_id in ['hyp_validation_layer', 'hyp_state_persistence']:
    state = engine.process_action(f'hypothesis:{hyp_id}')
    hyps2 = state.get('hypotheses', [])
    hyp_state = {h['id']: h.get('validated') for h in hyps2}
    ss = state.get('scenarioState', 'unknown')
    print(f"After hypothesis:{hyp_id} -> validated={hyp_state.get(hyp_id)}, scenario={ss}")

print(f"Final scenario state: {state.get('scenarioState')}")
eng = engine.current_engine
if eng:
    print(f"Win conditions: {eng.state.win_conditions}")
    core_hyps = [h_id for h_id, hd in eng._hypotheses_config.items() if hd.get('correct')]
    print(f"Core hyps (correct=True): {core_hyps}")
    for h in eng.hypotheses:
        print(f"  {h.id}: tested={h.tested}, validated={h.validated}")

print("Done")
