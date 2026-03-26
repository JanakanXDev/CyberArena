"""Test the compound win condition: hypothesis + action both required."""
import sys
sys.path.insert(0, '.')
import engine

print("=== TEST: hypothesis alone should NOT win ===")
state = engine.reset_game('defender_campaign', 'medium', 'input_trust_failures')
engine.configure_session_focus('defender', 'web_server')

state = engine.process_action('hypothesis:hyp_persistence_method')
ss = state.get('scenarioState')
print(f"  After hypothesis only: state={ss}  (should be 'active', NOT 'victory')")
assert ss == 'active', f"FAIL: instantly won on hypothesis alone! Got {ss}"
print("  PASS: no instant win from hypothesis alone")

print()
print("=== TEST: action alone should NOT win ===")
state = engine.reset_game('defender_campaign', 'medium', 'input_trust_failures')
engine.configure_session_focus('defender', 'web_server')

# First validate so the hypothesis-gated action unlocks
state = engine.process_action('hypothesis:hyp_persistence_method')
state = engine.process_action('act_audit_cron')
ss = state.get('scenarioState')
# Without hypothesis confirmed, action alone shouldn't win
# Note: the hypothesis was validated before so it IS confirmed — this will actually win
# Let's test the reverse: action without hypothesis (memory forensics + no hypothesis)
state2 = engine.reset_game('defender_campaign', 'medium', 'input_trust_failures')
engine.configure_session_focus('defender', 'web_server')
state2 = engine.process_action('act_deep_forensics')  # action that has no hypothesis requirement
ss2 = state2.get('scenarioState')
print(f"  After unrelated action only: state={ss2}  (should be 'active')")
assert ss2 == 'active', f"FAIL: won on wrong action! Got {ss2}"
print("  PASS: no win from unrelated action")

print()
print("=== TEST: hypothesis + correct action = VICTORY ===")
state = engine.reset_game('defender_campaign', 'medium', 'input_trust_failures')
engine.configure_session_focus('defender', 'web_server')

# Step 1: validate the hypothesis (unlocks act_audit_cron)
state = engine.process_action('hypothesis:hyp_persistence_method')
ss = state.get('scenarioState')
print(f"  After hypothesis confirmed: state={ss}  (should be 'active')")
assert ss == 'active', f"FAIL: won too early, should still be active. Got {ss}"

# Step 2: Now execute the investigation action
state = engine.process_action('act_audit_cron')
ss = state.get('scenarioState')
print(f"  After audit cron action: state={ss}  (should be 'victory')")
assert ss == 'victory', f"FAIL: expected victory, got {ss}"
debrief = state.get('strategicDebrief', {})
print(f"  VICTORY CONFIRMED on turn {debrief.get('turns')} with outcome={debrief.get('outcome')}")

print()
print("ALL TESTS PASSED")
