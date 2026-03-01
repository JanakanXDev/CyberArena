import sys
sys.path.append('.')
import engine

state = engine.reset_game('playground', 'hard', 'linux_privesc')

print('--- Test 1: Baseline State ---')
print(f'Scenario State: {state.get("scenarioState")}')
print(f'Win Conditions: {engine.current_engine.state.win_conditions}')

print("\n--- Test 2: Triggering extreme pressure ---")
# Manually crank pressure past 100 to see if the playground mode "loses"
engine.current_engine.state.pressure = 150
s2, ai = engine.current_engine.process_action('tactical_fallback')

print(f'\n--- Test 3: Post-Action Terminal State ---')
print(f'Scenario State: {s2.get("scenario_state")}')
if s2.get("scenario_state") == "active":
    print("SUCCESS: Playground mode ignored the pressure threshold and remained active.")
else:
    print("FAILURE: Playground mode ended!")
