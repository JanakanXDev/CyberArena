import sys
sys.path.append('.')
import engine

state = engine.reset_game('guided_simulation', 'medium', 'input_trust_failures')

print('--- Test 1: Baseline State ---')
print(f'Scenario State: {state.get("scenarioState")}')
print(f'Available Actions: {len(state.get("availableActions", []))}')

print('\n--- Test 2: Validating Core Hypothesis ---')
# Force validate the core hypotheses through the engine's standard input processing
core_hyps = [h_id for h_id, hd in engine.current_engine._hypotheses_config.items() if hd.get("correct")]
print(f"Core Hypotheses found: {core_hyps}")

# Ensure the AI isn't defensive or deceptive, which overrides 'correct=True' hypotheses in evaluate_hypothesis
for h_id in core_hyps:
    engine.current_engine.state.ai_visual_state.posture = "observing"
    engine.current_engine.state.ai_visual_state.distance = "distant"
    print(f"Testing {h_id}...")
    engine.process_action(f"hypothesis:{h_id}")
    
# Debug: Output hypotheses validity
print("--- Final Hypothesis States ---")
for h in engine.current_engine._get_state_dict().get("hypotheses", []):
    print(f"{h.get('id')}: tested={h.get('tested')}, validated={h.get('validated')}")

# We must run an action to trigger the terminal check loop
print("\n--- Test 3: Processing final action to trigger check ---")
s2, ai = engine.current_engine.process_action('tactical_fallback')

print(f'\n--- Test 4: Post-Action Terminal State ---')
print(f'Scenario State: {s2.get("scenario_state")}')
print(f'Available Actions (Should be 0): {len(s2.get("available_actions", []))}')
if s2.get("strategic_debrief"):
    print(f'Debrief Summary: {s2.get("strategic_debrief").get("summary")}')
    print(f'Raw Debrief Output: {s2.get("strategic_debrief")}')
else:
    print('Error: Debrief not generated!')
