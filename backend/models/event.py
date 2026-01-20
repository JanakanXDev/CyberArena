from dataclasses import dataclass, field
from enum import Enum, auto
import uuid


class EventType(Enum):
    INFO = auto()
    SUCCESS = auto()
    WARNING = auto()
    FAILURE = auto()
    LESSON = auto()


@dataclass
class Event:
    type: EventType
    title: str
    description: str
    impact: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
