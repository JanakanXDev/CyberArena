from backend.scenarios.base import Scenario
from backend.core.state import GameState, Phase, AttackStage, DefenseLevel
from backend.models.event import Event, EventType

class EchoChamberScenario(Scenario):
    def __init__(self, config):
        super().__init__(config)
        self.phase_complete = False

    def allowed_actions(self, state: GameState) -> list[str]:
        actions = []
        if state.phase == Phase.RECON:
            # Initial actions
            if "logs_analyzed" not in state.discovered_vectors:
                actions.append("analyze_logs")
            if "waf_checked" not in state.discovered_vectors:
                actions.append("check_waf")

            # Hypotheses unlock after some investigation
            if "logs_analyzed" in state.discovered_vectors or "waf_checked" in state.discovered_vectors:
                actions.append("hypothesis_blind_sqli")
                actions.append("hypothesis_waf")

        elif state.phase == Phase.ATTACK:
            actions.append("low_and_slow")
            actions.append("aggressive_dump")

        elif state.phase == Phase.DEFENSE:
            actions.append("prepared_statements")
            actions.append("waf_rule")

        return actions

    def apply_player_action(self, action: str, state: GameState) -> None:
        self.phase_complete = False # Reset flag

        if state.phase == Phase.RECON:
            if action == "analyze_logs":
                state.discovered_vectors.append("logs_analyzed")
                state.add_event(Event(
                    type=EventType.INFO,
                    title="Logs Analyzed",
                    description="App logs show constant 5000ms delay on queries with `id=1' AND SLEEP(5)--`. DB logs show 'Query Timeout'.",
                    impact="Potential Blind SQL Injection detected."
                ))
            elif action == "check_waf":
                state.discovered_vectors.append("waf_checked")
                state.risk_score += 0.5
                state.add_event(Event(
                    type=EventType.WARNING,
                    title="WAF Check",
                    description="WAF logs are clean. No blocked requests found.",
                    impact="You wasted time checking a functioning WAF."
                ))
            elif action == "hypothesis_blind_sqli":
                state.add_event(Event(
                    type=EventType.SUCCESS,
                    title="Hypothesis Confirmed",
                    description="Evidence supports Blind SQL Injection. The delays correlate with the injected SLEEP commands.",
                    impact="Proceed to Exploitation."
                ))
                self.phase_complete = True
            elif action == "hypothesis_waf":
                state.risk_score += 1.0
                state.record_mistake("wrong_hypothesis")
                state.add_event(Event(
                    type=EventType.FAILURE,
                    title="Hypothesis Rejected",
                    description="WAF logs contradict this. If it were the WAF, you'd see 403 Forbidden, not 500 errors or timeouts.",
                    impact="Review the logs again."
                ))

        elif state.phase == Phase.ATTACK:
            if action == "low_and_slow":
                state.attack_stage = AttackStage.EXPLOITATION
                state.add_event(Event(
                    type=EventType.SUCCESS,
                    title="Data Extraction Successful",
                    description="Using bit-by-bit extraction (Low & Slow), you retrieved the admin hash without triggering alarms.",
                    impact="Hash: 5f4dcc3b5aa765d61d8327deb882cf99"
                ))
                self.phase_complete = True
            elif action == "aggressive_dump":
                state.risk_score += 2.0
                state.record_mistake("noisy_attack")
                state.add_event(Event(
                    type=EventType.FAILURE,
                    title="WAF BLOCKED!",
                    description="Aggressive 'UNION SELECT' triggered the WAF immediately. Your IP is now throttled.",
                    impact="Attack failed. Try a stealthier approach."
                ))

        elif state.phase == Phase.DEFENSE:
            if action == "prepared_statements":
                state.defense_level = DefenseLevel.STRONG
                state.is_secured = True
                state.add_event(Event(
                    type=EventType.SUCCESS,
                    title="Vulnerability Patched",
                    description="You implemented Prepared Statements (Parameterized Queries). The SQL interpreter now treats input as data, not code.",
                    impact="Root cause fixed."
                ))
                self.phase_complete = True
            elif action == "waf_rule":
                state.risk_score += 1.5
                state.defense_level = DefenseLevel.MODERATE
                state.record_mistake("weak_mitigation")
                state.add_event(Event(
                    type=EventType.WARNING,
                    title="Temporary Fix",
                    description="The WAF rule blocked the specific payload, but attackers quickly bypassed it using encoding.",
                    impact="Root cause remains. Fix the code."
                ))

    def attacker_response(self, state: GameState) -> None:
        pass

    def should_advance_phase(self, state: GameState) -> bool:
        return self.phase_complete

    def is_complete(self, state: GameState) -> bool:
        return state.is_secured
