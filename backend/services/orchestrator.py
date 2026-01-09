from backend.services.session_service import SessionService
from backend.scenarios.registry import SCENARIO_REGISTRY
from backend.models.curriculum import Curriculum
from backend.db.session_repo import create_session
from backend.db.attempt_repo import save_attempt


class Orchestrator:
    def __init__(self, user, curriculum, base_config):
        if user.role.name != "STUDENT":
            raise PermissionError("Only students can start sessions")

        self.user = user
        self.curriculum = curriculum
        self.base_config = base_config
        self.current_index = 0
        self.session = SessionService()

    def start(self):
        self.session_id = create_session(
            user_id=self.user.id,
            curriculum_name=self.curriculum.name
        )
        self._start_current_scenario()


    def _start_current_scenario(self):
        step = self.curriculum.steps[self.current_index]

        scenario_class = SCENARIO_REGISTRY[step.scenario_id]

        config = dict(self.base_config)
        config["scenario_name"] = step.scenario_id

        self.session.start_session(config, scenario_class)

    def apply_action(self, action: str):
        self.session.apply_action(action)

        state = self.session.get_state()

        if state.phase.name == "COMPLETE":
            result = self.session.get_result()
            self._evaluate_and_advance(result)

    def _evaluate_and_advance(self, result: dict):
        step = self.curriculum.steps[self.current_index]

        save_attempt(
            session_id=self.session_id,
            scenario_id=step.scenario_id,
            result=result
        )

        if result["score"] >= step.min_score_to_pass:
            self.current_index += 1
            if self.current_index < len(self.curriculum.steps):
                self._start_current_scenario()

        # else: repeat same scenario

    def get_state(self):
        return self.session.get_state()

    def get_result(self):
        return self.session.get_result()
