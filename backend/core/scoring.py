from backend.core.state import GameState
from backend.models.event import EventType


class ScoringEngine:
    @staticmethod
    def calculate(state: GameState) -> dict:
        score = 100

        # Risk penalty
        score -= int(state.risk_score * 10)

        # Turn penalty (discourage brute force)
        score -= state.turn_count * 5

        # Outcome
        if state.is_compromised:
            score -= 30
        elif state.is_secured:
            score += 20

        # Learning bonus / penalty
        for event in state.events:
            if event.type == EventType.LESSON:
                score += 5
            if event.type == EventType.FAILURE:
                score -= 5
        # Penalty for repeated mistakes
        for count in state.mistake_counter.values():
            if count > 1:
                score -= (count - 1) * 5
                

        return {
            "score": max(score, 0),
            "turns": state.turn_count,
            "risk": state.risk_score,
            "outcome": "compromised" if state.is_compromised else "secured"
        }
