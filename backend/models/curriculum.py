from dataclasses import dataclass
from typing import List, Dict


@dataclass
class CurriculumStep:
    scenario_id: str
    min_score_to_pass: int = 50


@dataclass
class Curriculum:
    name: str
    steps: List[CurriculumStep]
