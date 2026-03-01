
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation_engine import SimulationEngine, LearningMode, Phase, SystemState, Action

def verify_antigravity():
    print("Initializing SimulationEngine with Antigravity AI...")
    engine = SimulationEngine(LearningMode.PLAYGROUND, "adaptive", "test_scenario")
    
    # Mock scenario config
    scenario_config = {
        "initial_state": {"pressure": 0},
        "actions": [
            {
                "id": "probe_input", 
                "label": "Probe Input", 
                "type": "probe", 
                "pressure_delta": 5,
                "available": True
            },
            {
                "id": "escalate_priv",
                "label": "Escalate Privileges",
                "type": "escalate",
                "pressure_delta": 10,
                "available": True
            }
        ],
        "contradictions": [
            {
                "id": "contra_1",
                "assumption_id": "safe_input",
                "condition_type": "action_taken",
                "action_id": "escalate_priv",
                "description": "System state mutated despite 'safe_input' assumption.",
                "trigger_failure": "previous_success_fails"
            }
        ], 
        "system_conditions": {
            "timing_jitter": True # Active signal
        }
    }
    
    engine.initialize(scenario_config)
    
    print("\n--- TEST 1: Strategy Spamming & Tunnel Vision ---")
    # User spams 'probe_input' while ignoring 'timing_jitter' signal
    for i in range(4):
        print(f"Turn {i+1}: Executing 'Probe Input'...")
        engine.process_action("probe_input")
        
    # Now simulate a failure (e.g. system locks action - manual override for test)
    # In a real run, the AI opponent would lock it. Here we just force the feedback check logic.
    # We'll create a dummy "failed" action event to trigger analysis
    print("Turn 5: Action Fails (Simulated)")
    engine.state.action_history[-1]["actually_failed"] = True
    feedback = engine.antigravity.analyze_failure("action_failed", {"action": engine.available_actions[0]})
    
    if feedback:
        print("\n[Antigravity Feedback Generated]")
        print(f"Insight: {feedback.get('insight')}")
        print(f"Reasoning Gap: {feedback.get('reasoning_gap')}")
    else:
        print("FAILED: No feedback generated for strategy spamming.")

    print("\n--- TEST 2: Contradiction ---")
    # Reset engine for clean state if needed, but we can continue
    # Trigger contradiction by taking 'escalate_priv'
    print("Turn 6: Executing 'Escalate Privileges' (Triggers Contradiction)...")
    state_dict, _ = engine.process_action("escalate_priv")
    
    # The contradiction logic in engine should have fired and called antigravity
    if state_dict.get("antigravity_feedback"):
        fb = state_dict.get("antigravity_feedback")
        print("\n[Antigravity Feedback Generated]")
        print(f"Trigger: {fb.get('trigger')}")
        print(f"Insight: {fb.get('insight')}")
    else:
        print("FAILED: No feedback generated for contradiction.")

if __name__ == "__main__":
    verify_antigravity()
