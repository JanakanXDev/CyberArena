import requests
import time

modes = ["guided_simulation", "attacker_campaign", "defender_campaign", "playground"]
scenarios = ["input_trust_failures", "linux_privesc", "network_breach"]
difficulties = ["recruit", "veteran", "elite"]

print("Starting Comprehensive Platform Verification...")

success_count = 0
fail_count = 0

for mode in modes:
    for scenario in scenarios:
        for difficulty in difficulties:
            payload = {
                "mode": mode,
                "scenarioId": scenario,
                "difficulty": difficulty
            }
            try:
                res = requests.post("http://127.0.0.1:5000/start", json=payload, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    # Check if valid state returned
                    if "scenarioState" in data or "sessionStatus" in data:
                        print(f"[OK] Mode: {mode:20} | Scenario: {scenario:22} | Diff: {difficulty:10}")
                        success_count += 1
                    else:
                        print(f"[WARN] Invalid state returned for {mode}, {scenario}, {difficulty}")
                        print(data.keys())
                        fail_count += 1
                else:
                    print(f"[ERR] Status {res.status_code} for {mode}, {scenario}, {difficulty}")
                    fail_count += 1
            except Exception as e:
                print(f"[FATAL] Connection error for {mode}, {scenario}, {difficulty}: {e}")
                fail_count += 1
            
            # small delay
            time.sleep(0.1)

print(f"\nVerification Complete. Success: {success_count}, Failures: {fail_count}")
