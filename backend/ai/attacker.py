# attacker_ai.py
class AttackerAI:
    def __init__(self, strategy="medium"):
        self.strategy = strategy

    def decide(self, state):
        """
        Decide next attacker action based on current GameState.
        This is intentionally simple for now.
        """

        if self.strategy == "aggressive":
            return "exploit"

        if self.strategy == "medium":
            if state.defense_level.name == "WEAK":
                return "exploit"
            return "wait"

        if self.strategy == "stealth":
            return "wait"

        return "wait"
