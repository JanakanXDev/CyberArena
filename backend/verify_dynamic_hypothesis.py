import os
import sys

from engine import reset_game, process_action, configure_session_focus

def run_test():
    print("Initializing Game (No Focus)...")
    state = reset_game(mode="guided_simulation", difficulty="medium", scenario_id="input_trust_failures")
    
    actions = state.get("availableActions", [])
    hypotheses = state.get("hypotheses", [])
    print(f"Pre-Focus - Actions: {len(actions)}, Hypotheses: {len(hypotheses)}")
    
    print("\n--- Configuring Focus: Role=Attacker, Component=web_server ---")
    state = configure_session_focus("attacker", "web_server")
    
    actions = state.get("availableActions", [])
    hypotheses = state.get("hypotheses", [])
    visual_state = state.get("aiVisualState", {})
    
    print(f"Post-Focus - Actions: {len(actions)}, Hypotheses: {len(hypotheses)}")
    print(f"AI Visual State: Posture={visual_state.get('posture')}, Distance={visual_state.get('distance')}, Entropy={visual_state.get('entropy')}")
    
    if not hypotheses:
        print("ERROR: No hypotheses generated for focus!")
        return False
        
    test_hyp_id = hypotheses[0]["id"]
    test_hyp_label = hypotheses[0]["label"]
    
    print(f"\n--- Testing Hypothesis: {test_hyp_label} ({test_hyp_id}) ---")
    state = process_action(f"hypothesis:{test_hyp_id}")
    
    validated = None
    for h in state.get("hypotheses", []):
        if h["id"] == test_hyp_id:
            validated = h.get("validated")
            break
            
    print(f"Validation Result (dynamic server-side): {validated}")
    
    visual_state = state.get("aiVisualState", {})
    print(f"New AI Visual State: Posture={visual_state.get('posture')}, Distance={visual_state.get('distance')}, Entropy={visual_state.get('entropy')}")
    
    if visual_state.get("entropy", 0) <= 0:
        print("ERROR: AI Visual State entropy did not increase after testing hypothesis!")
        return False
        
    print("\nSUCCESS: Dynamic Hypothesis Evaluation and Visual State AI are functioning correctly.")
    return True

if __name__ == "__main__":
    run_test()
