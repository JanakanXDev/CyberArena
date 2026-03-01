import sys

target = """        # Mandatory strategy-punishment system
        if user_action:
            ai_actions.extend(self._punish_repetition(user_action, state, mode))
        
        return ai_actions"""

replacement = """        # Mandatory strategy-punishment system
        if user_action:
            ai_actions.extend(self._punish_repetition(user_action, state, mode))
            
        # Update Visual State
        if state and hasattr(state, "ai_visual_state"):
            state.ai_visual_state.entropy = min(100, state.ai_visual_state.entropy + len(ai_actions) * 2)
            if self.threat_level > 70:
                state.ai_visual_state.posture = "aggressive" if self.persona.value == "attacker" else "defensive"
                state.ai_visual_state.distance = "approaching" if self.persona.value == "attacker" else "closing"
            elif self.threat_level > 30:
                state.ai_visual_state.posture = "observing"
                state.ai_visual_state.distance = "middle"
        
        return ai_actions"""

with open("backend/ai_systems.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace normalizing newlines just in case
content_normalized = content.replace('\\r\\n', '\\n')
target_normalized = target.replace('\\r\\n', '\\n')
replacement_normalized = replacement.replace('\\r\\n', '\\n')

if target_normalized in content_normalized:
    new_content = content_normalized.replace(target_normalized, replacement_normalized)
    with open("backend/ai_systems.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Patched ai_systems.py")
else:
    print("Target not found.")
