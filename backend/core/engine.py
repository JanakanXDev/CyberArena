from backend.core.state import GameState, Phase
from backend.scenarios.base import Scenario
from backend.core.scoring import ScoringEngine



class GameEngine:
    def __init__(self, attacker, scenario, config):
        self.state = GameState()
        self.attacker = attacker
        self.scenario = scenario
        self.config = config

    def get_result(self):
        return ScoringEngine.calculate(self.state)

    def start(self):
        if self.state.phase != Phase.INIT:
            raise RuntimeError("Game already started")
        self.state.phase = Phase.RECON
        self._update_allowed_actions()
    
    def _update_allowed_actions(self):
        self.state.allowed_actions = self.scenario.allowed_actions(self.state)

    def player_action(self, action: str):
        if self.state.turn_count >= self.config.max_turns:
            self.state.phase = Phase.COMPLETE
            return

        if self.state.phase == Phase.COMPLETE:
            raise RuntimeError("Game already completed")

        if action not in self.scenario.allowed_actions(self.state):
            raise ValueError(f"Action '{action}' not allowed in phase {self.state.phase}")

        self.scenario.apply_player_action(action, self.state)
        self.scenario.attacker_response(self.state)

        self.state.advance_turn()

        if self.scenario.is_complete(self.state):
            self.state.phase = Phase.COMPLETE
        elif self.scenario.should_advance_phase(self.state):
            self._advance_phase()

        self._update_allowed_actions()

    def _advance_phase(self):
        if self.state.phase == Phase.RECON:
            self.state.phase = Phase.ATTACK
        elif self.state.phase == Phase.ATTACK:
            self.state.phase = Phase.DEFENSE
        elif self.state.phase == Phase.DEFENSE:
            self.state.phase = Phase.RESOLUTION

    def get_state(self):
        return self.state
