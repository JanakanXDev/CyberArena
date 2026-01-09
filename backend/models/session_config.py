from dataclasses import dataclass


@dataclass
class SessionConfig:
    scenario_name: str
    attacker_strategy: str = "medium"

    max_turns: int = 5
    feedback_level: str = "adaptive"  # basic | adaptive | strict

    allow_retry: bool = True
