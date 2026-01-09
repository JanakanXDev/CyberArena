from backend.core.state import GameState, Phase
from backend.scenarios.base import Scenario


class GameEngine:
    def __init__(self, attacker, scenario: Scenario):
        self.state = GameState()
        self.attacker = attacker
        self.scenario = scenario

    def start(self):
        if self.state.phase != Phase.INIT:
            raise RuntimeError("Game already started")
        self.state.phase = Phase.RECON

    def player_action(self, action: str):
        if self.state.phase == Phase.COMPLETE:
            raise RuntimeError("Game already completed")

        if action not in self.scenario.allowed_actions(self.state):
            raise ValueError(f"Action '{action}' not allowed in phase {self.state.phase}")

        self.scenario.apply_player_action(action, self.state)
        self.scenario.attacker_response(self.state)

        self.state.advance_turn()

        if self.scenario.is_complete(self.state):
            self.state.phase = Phase.COMPLETE
        else:
            self._advance_phase()

    def _advance_phase(self):
        if self.state.phase == Phase.RECON:
            self.state.phase = Phase.ATTACK
        elif self.state.phase == Phase.ATTACK:
            self.state.phase = Phase.DEFENSE
        elif self.state.phase == Phase.DEFENSE:
            self.state.phase = Phase.RESOLUTION

    def get_state(self):
        return self.state
