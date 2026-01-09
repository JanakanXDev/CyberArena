from backend.models.event import Event, EventType


class FeedbackEngine:
    @staticmethod
    def exploit_success(reason: str, lesson: str):
        return Event(
            type=EventType.SUCCESS,
            title="Exploit Successful",
            description=reason,
            impact=lesson,
        )

    @staticmethod
    def defensive_mistake(reason: str, lesson: str):
        return Event(
            type=EventType.WARNING,
            title="Defensive Weakness",
            description=reason,
            impact=lesson,
        )

    @staticmethod
    def mitigation_applied(reason: str, lesson: str):
        return Event(
            type=EventType.INFO,
            title="Mitigation Applied",
            description=reason,
            impact=lesson,
        )
