import sys
import json
sys.path.append('.')
import engine

state = engine.reset_game('guided_simulation', 'medium', 'input_trust_failures')

actions_to_take = ["act_map_boundaries", "act_fuzz_inputs", "act_bypass_controls", "act_overload_backend", "act_focused_attack_web_server"]
hypotheses_to_test = ["hyp_validation_layer", "hyp_error_oracle", "hyp_state_persistence"]

print(f"Initial Scenario State: {state.get('scenarioState')}")

for h_id in hypotheses_to_test:
    res = engine.process_action(f"hypothesis:{h_id}")
    s = engine.current_engine._get_state_dict()
    hyp = next((h for h in s['hypotheses'] if h['id'] == h_id), None)
    print(f"Testing hypothesis: {h_id} | Validated: {hyp.get('validated') if hyp else 'Not found'} | AI Space: {s.get('ai_visual_state', {}).get('posture')}")

for a_id in actions_to_take:
    res = engine.process_action(a_id)
    s = engine.current_engine._get_state_dict()
    print(f"Testing action: {a_id} | Scenario State: {s['scenario_state']} | Pressure: {s['pressure']} | Stability: {s['stability']}")

s = engine.current_engine._get_state_dict()
print(f"\nFinal Scenario State: {s['scenario_state']}")
print(f"Available Actions: {[a['id'] for a in s['available_actions']]}")
