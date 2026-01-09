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
class FeedbackEngine:
        # existing methods stay

    @staticmethod
    def adaptive_warning(state, key, base_reason, lesson, level="adaptive"):
        state.record_mistake(key)

        if level == "basic":
            description = base_reason

        elif level == "adaptive":
            count = state.mistake_counter.get(key, 0)
            if count == 1:
                description = base_reason
            elif count == 2:
                description = base_reason + " This mistake is recurring."
            else:
                description = base_reason + " You are repeatedly ignoring this risk."

        else:  # strict
            description = "Critical strategic error detected."

        return Event(
            type=EventType.WARNING,
            title="Strategic Mistake",
            description=description,
            impact=lesson,
        )
