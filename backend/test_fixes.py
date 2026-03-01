"""Test script to verify fix 1 (win condition) and fix 2 (playground actions)"""
import engine
import json

print("=== TEST 1: WIN CONDITION IN GUIDED SIMULATION ===")
state = engine.reset_game('guided_simulation', 'medium', 'input_trust_failures')
engine.configure_session_focus('attacker', 'web_server')

state2 = engine.process_action('hypothesis:hyp_validation_layer')
state3 = engine.process_action('hypothesis:hyp_state_persistence')
hyps3 = state3.get('hypotheses', [])

result = {
    "hypotheses": [{"id": h['id'], "tested": h['tested'], "validated": h['validated']} for h in hyps3],
    "scenarioState": state3.get('scenarioState'),
    "hasDebrief": state3.get('strategicDebrief') is not None,
    "debriefOutcome": (state3.get('strategicDebrief') or {}).get('outcome')
}

print("TEST 1 RESULT:", json.dumps(result, indent=2))

print()
print("=== TEST 2: PLAYGROUND ACTIONS ===")
state_pg = engine.reset_game('playground', 'medium', 'input_trust_failures')
engine.configure_session_focus('attacker', 'web_server')
actions = state_pg.get('availableActions', [])
result2 = [{"id": a['id'], "available": a['available']} for a in actions]
print("TEST 2 RESULT:", json.dumps(result2, indent=2))
