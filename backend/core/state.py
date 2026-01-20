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
    allowed_actions: List[str] = field(default_factory=list)

    risk_score: float = 0.0
    turn_count: int = 0

    is_compromised: bool = False
    is_secured: bool = False

    events: List[Event] = field(default_factory=list)
    mistake_counter: dict[str, int] = field(default_factory=dict)
    def record_mistake(self, key: str):
        self.mistake_counter[key] = self.mistake_counter.get(key, 0) + 1

    def advance_turn(self):
        self.turn_count += 1

    def add_event(self, event: Event):
        self.events.append(event)
    def to_dict(self):
        serialized_events = []
        for e in self.events:
            # Handle object vs dict
            if isinstance(e, dict):
                title = e.get("title", "Unknown Event")
                # Check for description, msg, message
                description = e.get("description") or e.get("msg") or e.get("message") or "No description provided."
                evt_type = e.get("type", "INFO")
                # Handle enum if it's in the dict as enum object
                if hasattr(evt_type, "name"):
                    evt_type = evt_type.name

                evt_id = e.get("id", "no-id")
            else:
                title = e.title
                description = e.description
                evt_type = e.type.name
                evt_id = e.id

            serialized_events.append({
                "id": evt_id,
                "type": evt_type,
                "title": title,
                "description": description
            })

        return {
            "phase": self.phase.name,
            "attack_stage": self.attack_stage.name,
            "defense_level": self.defense_level.name,
            "discovered_vectors": self.discovered_vectors,
            "exposed_assets": self.exposed_assets,
            "allowed_actions": self.allowed_actions,
            "risk_score": self.risk_score,
            "turn_count": self.turn_count,
            "is_compromised": self.is_compromised,
            "is_secured": self.is_secured,
            "events": serialized_events
        }
        
