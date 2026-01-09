from dataclasses import dataclass
from enum import Enum, auto


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
