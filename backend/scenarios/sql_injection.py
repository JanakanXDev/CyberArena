from backend.scenarios.base import Scenario
from backend.core.feedback import FeedbackEngine

from backend.core.state import (
    GameState,
    Phase,
    AttackStage,
    DefenseLevel,
)


class SQLInjectionScenario(Scenario):

    def allowed_actions(self, state: GameState) -> list[str]:
        if state.phase == Phase.RECON:
            return ["scan_inputs"]

        if state.phase == Phase.ATTACK:
            return ["test_payload", "dump_db"]

        if state.phase == Phase.DEFENSE:
            return ["patch_query", "enable_waf"]

        return []

    def apply_player_action(self, action: str, state: GameState) -> None:
        if action == "scan_inputs":
            state.discovered_vectors.append("login_form")
            state.attack_stage = AttackStage.DISCOVERY
            state.risk_score += 0.5

        elif action == "test_payload":
            if "login_form" in state.discovered_vectors:
                state.attack_stage = AttackStage.EXPLOITATION
                state.risk_score += 1.0
            else:
                state.risk_score += 0.3

        elif action == "dump_db":
            if state.attack_stage == AttackStage.EXPLOITATION:
                state.is_compromised = True
                state.risk_score += 2.0
                state.add_event(
                    FeedbackEngine.exploit_success(
                        reason="Unsanitized input allowed SQL payload execution.",
                        lesson="Parameterized queries prevent SQL injection."
                    )
                )


        elif action == "patch_query":
            state.defense_level = DefenseLevel.MODERATE
            state.risk_score -= 0.5
            state.add_event(
                FeedbackEngine.mitigation_applied(
                    reason="Query logic updated to validate inputs.",
                    lesson="Input validation is the first defense against SQLi."
                )
            )

        elif action == "enable_waf":
            state.defense_level = DefenseLevel.STRONG
            state.risk_score -= 1.0

    def attacker_response(self, state: GameState) -> None:
        if state.defense_level == DefenseLevel.WEAK and state.attack_stage == AttackStage.EXPLOITATION:
            state.is_compromised = True
            state.risk_score += 1.5
            state.add_event(
                FeedbackEngine.defensive_mistake(
                    reason="No WAF or query hardening blocked the exploit.",
                    lesson="Defense-in-depth reduces attack success probability."
                )
            )

    def is_complete(self, state: GameState) -> bool:
        return state.is_compromised or state.defense_level == DefenseLevel.STRONG
