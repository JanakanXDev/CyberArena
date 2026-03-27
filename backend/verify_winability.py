"""Consolidated winability verification for Attacker and Defender modes."""
import sys
import os
sys.path.insert(0, '.')
import engine

def test_defender_win():
    print("=== VERIFY: Defender Mode Winability ===")
    state = engine.reset_game('defender_campaign', 'medium', 'input_trust_failures')
    engine.configure_session_focus('defender', 'web_server')
    
    # Step 1: Run evidence-gathering action
    # Note: act_audit_cron is required for hyp_persistence_method
    print("  Executing 'act_audit_cron'...")
    state = engine.process_action('act_audit_cron')
    
    # Step 2: Validate the correct hypothesis
    print("  Testing 'hypothesis:hyp_persistence_method'...")
    state = engine.process_action('hypothesis:hyp_persistence_method')
    
    ss = state.get('scenarioState')
    print(f"  Defender result: {ss}")
    if ss == 'victory':
        print("  PASS: Defender victory achieved!")
    else:
        print(f"  FAIL: Expected victory, got {ss}")
        print("  System Events:", [e['message'] for e in state.get('system_events', [])])
        return False
    return True

def test_attacker_win():
    print("\n=== VERIFY: Attacker Mode Winability ===")
    state = engine.reset_game('attacker_campaign', 'medium', 'input_trust_failures')
    engine.configure_session_focus('attacker', 'web_server')
    
    # Executing an 'escalate' action wins the attacker campaign
    print("  Executing 'act_noise_flood' (escalate action)...")
    state = engine.process_action('act_noise_flood')
    
    ss = state.get('scenarioState')
    print(f"  Attacker result: {ss}")
    if ss == 'victory':
        print("  PASS: Attacker victory achieved!")
    else:
        print(f"  FAIL: Expected victory, got {ss}")
        return False
    return True

if __name__ == "__main__":
    def_ok = test_defender_win()
    att_ok = test_attacker_win()
    
    if def_ok and att_ok:
        print("\nSUCCESS: Both modes are winable!")
        sys.exit(0)
    else:
        print("\nFAILURE: One or more modes could not be won.")
        sys.exit(1)
