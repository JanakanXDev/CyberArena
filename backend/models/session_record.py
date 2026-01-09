from dataclasses import dataclass
from typing import Dict


@dataclass
class SessionRecord:
    user_id: int
    curriculum_name: str
    scenario_id: str
    result: Dict
