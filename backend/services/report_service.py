class ReportService:
    @staticmethod
    def summarize(state):
        return {
            "turns": state.turn_count,
            "risk": state.risk_score,
            "mistakes": state.mistake_counter,
            "outcome": "compromised" if state.is_compromised else "secured",
            "events": [
                {
                    "title": e.title,
                    "description": e.description
                }
                for e in state.events
            ]
        }
