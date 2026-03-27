"""Targeted attacker win test."""
import sys
sys.path.insert(0, '.')
import engine

won_count = 0
fail_count = 0

for i in range(20):
    state = engine.reset_game('attacker_campaign', 'medium', 'input_trust_failures')
    cfg = engine.configure_session_focus('attacker', 'web_server')
    acts = cfg.get('availableActions', [])
    esc = [a for a in acts if a.get('type') == 'escalate']
    print(f"Run {i+1}: escalate actions={[a['id'] for a in esc]}, pressure={cfg.get('pressure')}")
    
    for a in esc:
        if state.get('scenarioState', 'active') != 'active':
            break
        state = engine.process_action(a['id'])
        ah = state.get('actionHistory', [])
        last = next((h for h in reversed(ah) if h.get('action_id') == a['id']), None)
        failed = last.get('actually_failed') if last else True
        ss = state.get('scenarioState', 'active')
        print(f"  {a['id']}: failed={failed}, state={ss}, pressure={state.get('pressure')}")
        if not failed and ss == 'victory':
            won_count += 1
            print("  WON!")
            break
        if ss == 'defeat':
            fail_count += 1
            print("  LOST!")
            break
    else:
        print(f"  Final state: {state.get('scenarioState')}")
    
    if won_count >= 3:
        print(f"\nConfirmed winnable (won {won_count} times in {i+1} attempts)")
        break

print(f"\nFinal: won={won_count}, lost={fail_count}")
