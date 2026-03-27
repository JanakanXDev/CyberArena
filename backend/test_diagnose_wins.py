"""
Diagnose exactly which actions trigger which win states in each mode.
"""
import sys
sys.path.insert(0, '.')
import engine

print("=== ATTACKER WIN PATH ANALYSIS ===")
for attempt in range(5):
    state = engine.reset_game('attacker_campaign', 'medium', 'input_trust_failures')
    engine.configure_session_focus('attacker', 'web_server')
    actions = state.get('availableActions', [])
    print(f"\nAttempt {attempt+1}: initial pressure={state.get('pressure')}, stability={state.get('stability')}")
    print(f"  Actions: {[a['id'] for a in actions]}")
    
    # Try each escalate/pivot action one by one to find which reaches victory
    p_before = state.get('pressure')
    for act_id in ['act_execution_jump', 'act_noise_flood']:
        try:
            state2 = engine.reset_game('attacker_campaign', 'medium', 'input_trust_failures')
            engine.configure_session_focus('attacker', 'web_server')
            state2 = engine.process_action(act_id)
            ss = state2.get('scenarioState', 'active')
            failed = state2.get('actionHistory', [{}])[-1].get('actually_failed', False) if state2.get('actionHistory') else 'N/A'
            print(f"  {act_id}: state={ss}, actually_failed={failed}")
        except Exception as e:
            print(f"  {act_id}: ERROR {e}")
    
    if attempt >= 1:
        break

print()
print("=== GUIDED WIN PATH ANALYSIS ===")
state = engine.reset_game('guided_simulation', 'medium', 'input_trust_failures')
engine.configure_session_focus('attacker', 'web_server')

# Check the win conditions
win_conds = state.get('scenarioState', 'unknown')
hyps = state.get('hypotheses', [])
print(f"Initial state: {win_conds}")
print(f"Hypotheses: {[(h['id'], h.get('tested'), h.get('validated')) for h in hyps]}")

state = engine.process_action('act_map_boundaries')
hmatch = state.get('actionHistory', [])[-1] if state.get('actionHistory') else {}
print(f"After act_map_boundaries: failed={hmatch.get('actually_failed')}, pressure={state.get('pressure')}")

state = engine.process_action('act_trigger_exception')
state = engine.process_action('act_corrupt_session')
state = engine.process_action('hypothesis:hyp_validation_layer')
hyps2 = state.get('hypotheses', [])
vs = [(h['id'], h.get('validated')) for h in hyps2]
print(f"After hyp_validation_layer: hyp states={vs}, scenario={state.get('scenarioState')}")

state = engine.process_action('hypothesis:hyp_state_persistence')
ss_final = state.get('scenarioState')
hyps3 = state.get('hypotheses', [])
vs2 = [(h['id'], h.get('validated')) for h in hyps3]
print(f"After hyp_state_persistence: hyp states={vs2}, scenario={ss_final}")

print("\nDone.")
