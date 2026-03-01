
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation_engine import LearningMode
from scenario_system import get_scenario_config

def verify_scenarios():
    print("Verifying Scenario Uniqueness across Modes...")
    
    modes = [
        LearningMode.GUIDED_SIMULATION,
        LearningMode.ATTACKER_CAMPAIGN,
        LearningMode.DEFENDER_CAMPAIGN,
        LearningMode.PLAYGROUND
    ]
    
    configs = {}
    
    for mode in modes:
        print(f"\nScanning Mode: {mode.value}")
        config = get_scenario_config("input_trust_failures", mode, "medium")
        configs[mode.value] = config
        
        # Print Hypotheses
        print("  Hypotheses:")
        for h in config.get("hypotheses", []):
            print(f"    - [{h['id']}] {h['label']}")
            
        # Print Actions
        print("  Actions:")
        for a in config.get("actions", []):
            print(f"    - [{a['id']}] {a['label']}")

    # Check for intersection
    print("\n--- Intersection Check ---")
    
    all_hyp_ids = []
    all_action_ids = []
    
    failed = False
    
    for mode_name, config in configs.items():
        hyp_ids = [h['id'] for h in config.get("hypotheses", [])]
        action_ids = [a['id'] for a in config.get("actions", [])]
        
        # Check if any ID has been seen before
        for hid in hyp_ids:
            if hid in all_hyp_ids:
                print(f"FAIL: Hypothesis ID reuse detected: {hid}")
                failed = True
            all_hyp_ids.append(hid)
            
        for aid in action_ids:
            if aid in all_action_ids:
                print(f"FAIL: Action ID reuse detected: {aid}")
                failed = True
            all_action_ids.append(aid)
            
    if not failed:
        print("\nSUCCESS: No content reuse detected across modes.")
    else:
        print("\nFAILURE: Reuse detected.")

if __name__ == "__main__":
    verify_scenarios()
