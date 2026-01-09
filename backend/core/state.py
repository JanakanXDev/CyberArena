from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List

from backend.models.event import Event


class Phase(Enum):
    INIT = auto()
    RECON = auto()
    ATTACK = auto()
    DEFENSE = auto()
    RESOLUTION = auto()
    COMPLETE = auto()


class AttackStage(Enum):
    NONE = auto()
    DISCOVERY = auto()
    EXPLOITATION = auto()
    PERSISTENCE = auto()
    IMPACT = auto()


class DefenseLevel(Enum):
    WEAK = auto()
    MODERATE = auto()
    STRONG = auto()


@dataclass
class GameState:
    phase: Phase = Phase.INIT
    attack_stage: AttackStage = AttackStage.NONE
    defense_level: DefenseLevel = DefenseLevel.WEAK

    discovered_vectors: List[str] = field(default_factory=list)
    exposed_assets: List[str] = field(default_factory=list)

    risk_score: float = 0.0
    turn_count: int = 0

    is_compromised: bool = False
    is_secured: bool = False

    events: List[Event] = field(default_factory=list)

    def advance_turn(self):
        self.turn_count += 1

    def add_event(self, event: Event):
        self.events.append(event)
