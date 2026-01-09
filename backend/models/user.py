from dataclasses import dataclass
from enum import Enum, auto


class Role(Enum):
    STUDENT = auto()
    INSTRUCTOR = auto()


@dataclass
class User:
    id: int
    username: str
    role: Role
