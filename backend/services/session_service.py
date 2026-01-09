from backend.ai.attacker import AttackerAI
from backend.core.engine import GameEngine
from backend.scenarios.sql_injection import SQLInjectionScenario
from backend.models.session_config import SessionConfig


class SessionService:
    """
    Manages a single game session.
    (Later this becomes multi-user)
    """

    def __init__(self):
        self.engine = None

    def start_session(self, config_data: dict, scenario_class):
        config = SessionConfig(**config_data)

        attacker = AttackerAI(strategy=config.attacker_strategy)
        scenario = scenario_class(config)

        self.engine = GameEngine(attacker, scenario, config)
        self.engine.start()


    def apply_action(self, action: str):
        if not self.engine:
            raise RuntimeError("Session not started")

        self.engine.player_action(action)

    def get_state(self):
        return self.engine.get_state()

    def get_result(self):
        return self.engine.get_result()
