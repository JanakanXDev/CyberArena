"""Test the win condition for Attacker mode."""
import sys
import os
sys.path.insert(0, '.')
import engine

def test_attacker_win():
    print("=== TEST: Attacker Mode Winability ===")
    
    # Reset game to attacker campaign
    state = engine.reset_game('attacker_campaign', 'medium', 'input_trust_failures')
    engine.configure_session_focus('attacker', 'web_server')
    
    initial_ss = state.get('scenarioState')
    print(f"  Initial state: {initial_ss}")
    assert initial_ss == 'active'
    
    # Execute an 'escalate' action which is the win target for Attacker mode
    print("  Executing 'act_noise_flood' (escalate action)...")
    state = engine.process_action('act_noise_flood')
    
    ss = state.get('scenarioState')
    print(f"  After action: state={ss}")
    
    if ss == 'victory':
        print("  PASS: Attacker victory achieved!")
        debrief = state.get('strategicDebrief', {})
        print(f"  Score: {debrief.get('score')}, Grade: {debrief.get('grade')}")
    else:
        print(f"  FAIL: Expected victory, got {ss}")
        # Print action history to debug
        print("  Action History:", state.get('action_history'))
        sys.exit(1)

if __name__ == "__main__":
    test_attacker_win()
