from abc import ABC, abstractmethod
from backend.core.state import GameState


class Scenario(ABC):
    def __init__(self, config):
        self.config = config


    @abstractmethod
    def allowed_actions(self, state: GameState) -> list[str]:
        pass

    @abstractmethod
    def apply_player_action(self, action: str, state: GameState) -> None:
        pass

    @abstractmethod
    def attacker_response(self, state: GameState) -> None:
        pass

    @abstractmethod
    def is_complete(self, state: GameState) -> bool:
        pass

    def should_advance_phase(self, state: GameState) -> bool:
        """
        Determines if the engine should automatically advance to the next phase.
        Default is True to maintain backward compatibility with simple scenarios.
        """
        return True
