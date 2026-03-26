import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def play_session():
    print("--- Starting Learner Session ---")
    
    # 1. Start Game
    print("\n[Learner]: Starting Guided Simulation on Broken Trust...")
    res = requests.post(f"{BASE_URL}/start", json={
        "mode": "guided_simulation",
        "scenarioId": "input_trust_failures",
        "difficulty": "recruit"
    }).json()
    
    # Look at hypotheses
    hyps = res.get("hypotheses", [])
    print(f"[System]: {len(hyps)} hypotheses available.")
    for h in hyps:
        print(f"  - {h['label']} (ID: {h['id']})")
        
    # 2. Ask Mentor for help
    print("\n[Learner]: Asking Mentor for help...")
    mentor_res = requests.post(f"{BASE_URL}/mentor/chat", json={
        "message": "I am a complete beginner. I'm looking at these hypotheses like 'Input flows directly into database queries'. What should I do first?"
    }).json()
    print(f"[Mentor]: {mentor_res.get('reply')}")
    
    time.sleep(1)
    
    # 3. Test a Hypothesis
    hyp_to_test = hyps[0]['id'] if hyps else "direct_db_input"
    print(f"\n[Learner]: Testing hypothesis: {hyp_to_test}...")
    action_res = requests.post(f"{BASE_URL}/action", json={"actionId": f"hypothesis:{hyp_to_test}"}).json()
    
    for h in action_res.get("hypotheses", []):
        if h['id'] == hyp_to_test:
            print(f"[System]: Hypothesis '{h['label']}' -> Validated: {h['validated']}, Tested: {h['tested']}")
            
    # Look at available actions
    actions = action_res.get("availableActions", [])
    action_to_take = None
    for a in actions:
        if a['available'] and a['type'] != 'hypothesis':
            action_to_take = a['id']
            break
            
    if action_to_take:
        print(f"\n[Learner]: Acknowledged. Taking action: {action_to_take}...")
        action_res = requests.post(f"{BASE_URL}/action", json={"actionId": action_to_take}).json()
        
        # Check event logs
        print("[System Event Logs]:")
        for log in action_res.get('logs', [])[-3:]:
            print(f"  > {log['source']} ({log['type']}): {log['message']}")
            
    # 4. Get Learning Data
    print("\n[Learner]: Session complete. Gathering learning data...")
    learning_data = requests.get(f"{BASE_URL}/learning/data").json()
    print("\n--- Analytics Report ---")
    print(json.dumps(learning_data, indent=2))
        
if __name__ == "__main__":
    play_session()
