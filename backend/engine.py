"""
Main Engine Interface for CyberArena
Integrates simulation engine, AI systems, and learning analytics
"""

import datetime
import logging
import traceback
from simulation_engine import SimulationEngine, LearningMode, Hypothesis, Phase, Action
from ai_systems import OpponentAI, MentorAI, AIPersona, AIDifficulty
from scenario_system import get_scenario_config
from learning_analytics import LearningAnalytics, LearningSession

# Global state
current_engine: SimulationEngine = None
current_mentor: MentorAI = None
current_analytics: LearningAnalytics = LearningAnalytics()
session_start_time: datetime.datetime = None
current_experience_mode: str = "advanced"

_eval_logger = logging.getLogger("cyberarena.hypothesis_eval")
if not _eval_logger.handlers:
    logging.basicConfig(level=logging.INFO)


def _normalize_experience_mode(mode: str) -> str:
    """Normalize UX/evaluation mode while preserving legacy behavior."""
    normalized = (mode or "advanced").strip().lower()
    if normalized in ("beginner", "intermediate", "advanced"):
        return normalized
    return "advanced"


def _is_clear_contradiction(verdict: dict) -> bool:
    """Only hard reject when no real signals were matched."""
    return len(verdict.get("matched_signals", [])) == 0


def _status_feedback_hint(
    status: str,
    feedback: str,
    matched_signals: list,
    mode: str
) -> dict:
    """Build additive hypothesis feedback envelope expected by UI/API."""
    gentle_prefix = "You're close, but " if mode == "beginner" else ""

    if status == "correct":
        hint = "Great read. Apply a confirming action to capitalize on this signal."
    elif status == "partial":
        hint = "Focus on timing, validation, or monitoring shifts and refine one missing detail."
    else:
        hint = "Re-check live system signals first, then restate your reasoning around observed behavior."

    if mode == "beginner":
        if status == "wrong":
            feedback_text = f"{gentle_prefix}this doesn't match the timing or validation behavior currently shown."
        elif status == "partial":
            feedback_text = f"{gentle_prefix}your reasoning tracks some real behavior, but one part is still off."
        else:
            feedback_text = "Nice work. Your reasoning matches the system's observed behavior."
    else:
        feedback_text = feedback

    return {
        "status": status,
        "feedback": feedback_text,
        "hint": hint,
        "matched_signals": matched_signals,
    }


def create_log(source: str, category: str, log_type: str, message: str, logs: list):
    """Create a log entry"""
    log_id = len(logs)
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    return {
        "id": f"log_{log_id}",
        "timestamp": timestamp,
        "source": source,
        "category": category,
        "type": log_type,
        "message": message
    }


def _mode_string_to_enum(mode_str: str) -> LearningMode:
    """Convert mode string to enum"""
    mode_map = {
        "guided_simulation": LearningMode.GUIDED_SIMULATION,
        "attacker_campaign": LearningMode.ATTACKER_CAMPAIGN,
        "defender_campaign": LearningMode.DEFENDER_CAMPAIGN,
        "playground": LearningMode.PLAYGROUND,
        "attacker": LearningMode.ATTACKER_CAMPAIGN,  # Legacy support
        "defender": LearningMode.DEFENDER_CAMPAIGN   # Legacy support
    }
    return mode_map.get(mode_str, LearningMode.GUIDED_SIMULATION)



def _engine_state_to_api_response(
    engine: SimulationEngine,
    mentor: MentorAI,
    ai_actions: list = None,
    hypothesis_evaluation: dict = None
) -> dict:
    """Convert engine state to API response format"""
    state_dict = engine._get_state_dict()

    logs = []
    if ai_actions is None:
        ai_actions = []

    if engine.turn_count == 0:
        logs.append(create_log(
            "System",
            "event_log",
            "info",
            f"Simulation initialized: {engine.scenario_id}",
            logs
        ))
        logs.append(create_log(
            "System",
            "system_view",
            "info",
            "System components operational",
            logs
        ))

    for comp_id, comp_data in engine.state.system_components.items():
        if comp_data.get("monitoring"):
            logs.append(create_log(
                comp_id,
                "system_view",
                "info",
                f"Monitoring active on {comp_id}",
                logs
            ))

    if engine.state.action_history:
        last_action = engine.state.action_history[-1]
        logs.append(create_log(
            "Operator",
            "event_log",
            "info",
            f"Action executed: {last_action.get('action_id', 'unknown')}",
            logs
        ))

    for ai_action in ai_actions:
        persona_name = "AI Opponent"
        if engine.ai_opponent:
            persona_name = "AI Defender" if engine.ai_opponent.persona == AIPersona.DEFENDER else "AI Attacker"
        label   = ai_action.get("label", ai_action.get("name", "Unknown move"))
        sev     = ai_action.get("severity", "medium")
        sev_tag = {"low": "[LOW]", "medium": "[MED]", "high": "[HIGH]", "critical": "[CRIT]"}.\
                  get(sev, "")
        msg = f"{sev_tag} {label}: {ai_action.get('message', ai_action.get('description', 'Adversary action'))}"
        logs.append(create_log(persona_name, "event_log", "warning", msg, logs))

    for dc in engine.delayed_consequences:
        if dc.executed and dc.trigger_turn == engine.turn_count:
            logs.append(create_log(
                "System",
                "event_log",
                "warning",
                f"Delayed consequence: {dc.description}",
                logs
            ))

    if engine.state.contradictions:
        latest = engine.state.contradictions[-1]
        if latest.get("turn") == engine.turn_count:
            logs.append(create_log(
                "System",
                "event_log",
                "error",
                f"Contradiction detected: {latest.get('description', '')}",
                logs
            ))

    for event in engine.state.system_events:
        if event.get("turn") == engine.turn_count:
            logs.append(create_log(
                "System",
                "event_log",
                "warning" if event.get("level") == "warning" else "error" if event.get("level") == "error" else "info",
                event.get("message", "System behavior changed"),
                logs
            ))

    mentor_guidance = None
    if mentor and mentor.enabled:
        last_action_obj = None
        if engine.state.action_history:
            last_action_id = engine.state.action_history[-1].get("action_id")
            last_action_obj = next((a for a in engine.available_actions if a.id == last_action_id), None)
        mentor_guidance = mentor.get_guidance(engine.state, last_action_obj)

    response = {
        "mode": engine.mode.value,
        "experienceMode": current_experience_mode,
        "scenarioId": engine.scenario_id,
        "scenarioName": _get_scenario_name(engine.scenario_id),
        "turnCount": engine.turn_count,
        "availableActions": state_dict["available_actions"],
        "hypotheses": state_dict["hypotheses"],
        "logs": logs,
        "systemComponents": state_dict["system_components"],
        "systemConditions": state_dict.get("system_conditions", {}),
        "userAssumptions": state_dict["user_assumptions"],
        "actionHistory": state_dict["action_history"],
        "contradictions": state_dict["contradictions"],
        "mentorGuidance": mentor_guidance,
        "sessionStatus": state_dict.get("session_status", "active"),
        "collapseReason": state_dict.get("collapse_reason"),
        "collapseMessage": state_dict.get("collapse_message"),
        "aiVisualState": state_dict.get("ai_visual_state"),
        "missionComplete": state_dict.get("scenario_state") == "victory",
        "scenarioState": state_dict.get("scenario_state", "active"),
        "strategicDebrief": state_dict.get("strategic_debrief"),
        "pressure": state_dict.get("pressure", 0),
        "stability": state_dict.get("stability", 100),
        # AI last move — primary move shown in the Threat Feed panel
        "aiLastMove": ai_actions[0] if ai_actions else None,
        "aiMoveHistory": ai_actions,
        # Additive hypothesis evaluation envelope (present when a hypothesis is tested)
        "hypothesisEvaluation": hypothesis_evaluation,
    }

    if response["sessionStatus"] == "collapsed":
        response["reflectionSummary"] = current_analytics.generate_reflection_summary(
            engine.state,
            engine.hypotheses,
            engine.state.action_history
        )

    return response


def _get_scenario_name(scenario_id: str) -> str:
    """Get scenario display name"""
    names = {
        "level_0_tutorial": "Level 0: The Evidence Loop",
        "beginner_input_basics": "Beginner: Input Validation Basics",
        "beginner_rate_limit_basics": "Beginner: Rate Limit Basics",
        "beginner_auth_basics": "Beginner: Authentication Basics",
        "intermediate_signal_fusion": "Intermediate: Signal Fusion",
        "input_trust_failures": "Operation: Broken Trust",
        "linux_privesc": "Operation: Glass Ceiling",
        "network_breach": "Operation: Silent Echo"
    }
    return names.get(scenario_id, "Unknown Mission")


def reset_game(mode: str, difficulty: str, scenario_id: str, stage_index: int = 0, experience_mode: str = "advanced"):
    """Initialize new game session"""
    global current_engine, current_mentor, session_start_time, current_experience_mode
    
    try:
        # Convert mode string to enum
        mode_enum = _mode_string_to_enum(mode)
        current_experience_mode = _normalize_experience_mode(experience_mode)
        
        # Get scenario configuration
        scenario_config = get_scenario_config(scenario_id, mode_enum, difficulty)
        
        # Create simulation engine
        current_engine = SimulationEngine(mode_enum, difficulty, scenario_id)
        current_engine.initialize(scenario_config)
        
        # Initialize AI opponent if needed
        if "ai_persona" in scenario_config:
            persona = scenario_config["ai_persona"]
            ai_difficulty = scenario_config.get("ai_difficulty", AIDifficulty.ADAPTIVE)
            current_engine.ai_opponent = OpponentAI(persona, ai_difficulty)
        
        # Initialize mentor (disabled by default)
        current_mentor = MentorAI()
        
        # Record session start
        session_start_time = datetime.datetime.now()
        
        # Return initial state
        initial_response = _engine_state_to_api_response(current_engine, current_mentor, [])
        
        # Backward compatibility for out-of-the-box frontend experience
        available = initial_response.get('availableActions', [])
        is_only_fallback = len(available) == 1 and available[0].get('id') == "tactical_fallback"
        
        if (not available or is_only_fallback) and not initial_response.get('hypotheses'):
            current_engine.configure_session("attacker", "web_server")
            initial_response = _engine_state_to_api_response(current_engine, current_mentor, [])
            
        print(f"Initial state - Actions: {len(initial_response.get('availableActions', []))}, Hypotheses: {len(initial_response.get('hypotheses', []))}")
        print(f"Available action IDs: {[a.get('id') for a in initial_response.get('availableActions', [])]}")
        return initial_response
        
    except Exception as e:
        print(f"Error in reset_game: {e}")
        traceback.print_exc()
        raise


def configure_session_focus(role: str, component: str):
    """Configure active simulation session with role and component focus"""
    global current_engine, current_mentor
    
    if not current_engine:
        raise ValueError("No active simulation to configure.")
        
    current_engine.configure_session(role, component)
    return _engine_state_to_api_response(current_engine, current_mentor, [])


def process_action(input_data: str, action_context: dict = None):
    """Process user action or command"""
    global current_engine, current_mentor, current_experience_mode
    
    if not current_engine:
        raise ValueError("No active simulation. Call reset_game first.")
    
    try:
        action_context = action_context or {}
        if current_engine.state.session_status == "collapsed":
            return _engine_state_to_api_response(current_engine, current_mentor, [])
        ai_actions = []
        ai_intent = None
        hypothesis_evaluation = None
        # Handle free-text NLP hypothesis testing (Hybrid Validation Pipeline)
        if input_data.startswith("hypothesis_text:"):
            from ai_systems import InputFilter, OllamaValidator, EngineValidator
            user_text = input_data.split(":", 1)[1].strip()

            # ── Layer 1: Anti-Abuse Input Filter ──
            filter_result = InputFilter.validate(user_text)
            if not filter_result["valid"]:
                current_engine._record_system_event(
                    f"Input Rejected: {filter_result['reason']}", "warning"
                )
                return _engine_state_to_api_response(current_engine, current_mentor, [])

            current_engine._record_system_event(
                f"Analyzing hypothesis: '{user_text}' via hybrid validation...", "info"
            )

            # ── Layer 2: LLM Intent Parsing (LLM does NOT decide truth) ──
            # Build label list without correctness info
            hypothesis_labels = [
                {"id": h_id, "label": h_data.get("label", h_id)}
                for h_id, h_data in current_engine._hypotheses_config.items()
            ]
            intent = OllamaValidator.parse_intent(
                user_text,
                hypothesis_labels,
                experience_mode=current_experience_mode
            )

            current_engine._record_system_event(
                f"Intent parsed: target='{intent.get('target')}', "
                f"claim='{intent.get('claim')}', "
                f"LLM confidence={intent.get('confidence', 0):.0%}",
                "info"
            )

            # ── Layer 3: Engine Truth Validation (Engine is source of truth) ──
            verdict = EngineValidator.evaluate(
                intent, current_engine._hypotheses_config, current_engine.state
            )
            classification = verdict["classification"]
            matched_id = verdict.get("matched_hypothesis_id")
            feedback = verdict.get("contradiction_feedback", "")
            matched_signals = verdict.get("matched_signals", [])

            # Stability-first wrapper: beginner/intermediate are more forgiving.
            # Advanced mode keeps legacy strictness.
            if current_experience_mode != "advanced":
                if classification != "correct" and matched_signals:
                    classification = "partial"
                if classification == "incorrect":
                    classification = "wrong"
            else:
                classification = "wrong" if classification == "incorrect" else classification

            _eval_logger.info(
                "hyp_eval user_input=%r mode=%s target=%r claim=%r class=%s matched_id=%r matched_signals=%s reason=%r",
                user_text,
                current_experience_mode,
                intent.get("target"),
                intent.get("claim"),
                classification,
                matched_id,
                matched_signals,
                feedback,
            )

            if classification == "correct" and matched_id:
                current_engine._record_system_event(
                    f"✓ Hypothesis Validated ({verdict['confidence']:.0%}): {feedback}",
                    "info"
                )
                hypothesis_evaluation = _status_feedback_hint(
                    "correct",
                    feedback,
                    matched_signals,
                    current_experience_mode
                )
                # Fall through to process as structured hypothesis test
                input_data = f"hypothesis:{matched_id}"
            elif classification == "partial":
                # Partial credit: small penalty, hint provided
                current_engine.state.pressure = min(100, current_engine.state.pressure + 5)
                current_engine._record_system_event(
                    f"⚠ Partial Match ({verdict['confidence']:.0%}): {feedback}",
                    "warning"
                )
                hypothesis_evaluation = _status_feedback_hint(
                    "partial",
                    feedback,
                    matched_signals,
                    current_experience_mode
                )
                if current_engine.ai_opponent:
                    import uuid
                    pseudo_action = Action(
                        id=f"nlp_partial_{uuid.uuid4()}",
                        label="Partial NLP Hypothesis",
                        description=user_text,
                        type="hypothesis"
                    )
                    ai_intent = current_engine.ai_opponent.evaluate_intent(pseudo_action)
                    ai_actions = current_engine.ai_opponent.react_to_action(
                        pseudo_action, current_engine.state,
                        current_engine.available_actions, ai_intent, current_engine.mode
                    )
                    current_engine.apply_ai_actions(ai_actions)
                return _engine_state_to_api_response(
                    current_engine,
                    current_mentor,
                    ai_actions,
                    hypothesis_evaluation=hypothesis_evaluation
                )
            else:
                # Hard rejection only when clearly contradictory to current state.
                if current_experience_mode != "advanced" and not _is_clear_contradiction(verdict):
                    current_engine.state.pressure = min(100, current_engine.state.pressure + 5)
                    current_engine._record_system_event(
                        f"⚠ Partial Match ({verdict['confidence']:.0%}): {feedback}",
                        "warning"
                    )
                    hypothesis_evaluation = _status_feedback_hint(
                        "partial",
                        feedback,
                        matched_signals,
                        current_experience_mode
                    )
                    return _engine_state_to_api_response(
                        current_engine,
                        current_mentor,
                        ai_actions,
                        hypothesis_evaluation=hypothesis_evaluation
                    )

                # Wrong/contradictory: full penalty
                current_engine.state.pressure = min(100, current_engine.state.pressure + 10)
                current_engine._record_system_event(
                    f"✗ Hypothesis Rejected ({verdict['confidence']:.0%}): {feedback}",
                    "error"
                )
                hypothesis_evaluation = _status_feedback_hint(
                    "wrong",
                    feedback,
                    matched_signals,
                    current_experience_mode
                )
                if current_engine.ai_opponent:
                    import uuid
                    pseudo_action = Action(
                        id=f"nlp_reject_{uuid.uuid4()}",
                        label="Invalid NLP Hypothesis",
                        description=user_text,
                        type="hypothesis"
                    )
                    ai_intent = current_engine.ai_opponent.evaluate_intent(pseudo_action)
                    ai_actions = current_engine.ai_opponent.react_to_action(
                        pseudo_action, current_engine.state,
                        current_engine.available_actions, ai_intent, current_engine.mode
                    )
                    current_engine.apply_ai_actions(ai_actions)
                return _engine_state_to_api_response(
                    current_engine,
                    current_mentor,
                    ai_actions,
                    hypothesis_evaluation=hypothesis_evaluation
                )

        # Handle structured hypothesis testing
        if input_data.startswith("hypothesis:"):
            theory_id = input_data.split(":", 1)[1]
            
            # Find hypothesis
            hypothesis = next((h for h in current_engine.hypotheses if h.id == theory_id), None)
            if not hypothesis:
                # Create new hypothesis from available hypotheses
                available_hypotheses = current_engine._get_state_dict().get("hypotheses", [])
                hyp_data = next((h for h in available_hypotheses if h["id"] == theory_id), None)
                if hyp_data:
                    hypothesis = Hypothesis(
                        id=hyp_data["id"],
                        label=hyp_data["label"],
                        description=hyp_data.get("description", ""),
                        timestamp=datetime.datetime.now()
                    )
                    current_engine.add_hypothesis(hypothesis)
            
            if hypothesis:
                # Check for evidence-gating
                hyp_config = current_engine._hypotheses_config.get(theory_id)
                
                # If not in root config, try state dict
                if not hyp_config:
                    state_dict = current_engine._get_state_dict()
                    hyp_config = next((h for h in state_dict.get("hypotheses", [])
                                   if h.get("id") == theory_id), None)
                    if hyp_config:
                        # Ensure hypothesis is officially created
                        if hypothesis not in current_engine.hypotheses:
                            hypothesis = Hypothesis(
                                id=hyp_config["id"],
                                label=hyp_config["label"],
                                description=hyp_config.get("description", ""),
                                timestamp=datetime.datetime.now()
                            )
                            current_engine.add_hypothesis(hypothesis)
                
                evidence_req = hyp_config.get("evidence_required", []) if hyp_config else []
                has_evidence = True
                if evidence_req:
                    for req_id in evidence_req:
                        found = False
                        for hist_action in current_engine.state.action_history:
                            if hist_action.get("action_id") == req_id and not hist_action.get("actually_failed"):
                                found = True
                                break
                        if not found:
                            has_evidence = False
                            break

                if not has_evidence:
                    # Apply penalty for blind guessing
                    current_engine.state.pressure = min(100, current_engine.state.pressure + 15)
                    hypothesis.tested = True
                    hypothesis.validated = False
                    
                    # Update assumption tracking so UI doesn't break
                    for assumption in current_engine.state.user_assumptions:
                        if assumption["id"] == theory_id:
                            assumption["validated"] = False
                            
                    current_engine._record_system_event(
                        "Hypothesis Rejected: Insufficient Evidence. AI capitalized on reckless guess.",
                        "error"
                    )
                    hypothesis_evaluation = _status_feedback_hint(
                        "wrong",
                        "Insufficient evidence for this hypothesis at the current turn.",
                        [],
                        current_experience_mode
                    )
                else:
                    if hyp_config:
                        validated = current_engine.evaluate_hypothesis(theory_id)
                        current_engine.validate_hypothesis(theory_id, validated)
                        current_signals = [
                            key for key, val in current_engine.state.system_conditions.items() if val
                        ]
                        status = "correct" if validated else "wrong"
                        feedback_text = (
                            hyp_config.get("why_correct", "Hypothesis validated by current state.")
                            if validated
                            else hyp_config.get("why_wrong", "This does not match current system behavior.")
                        )
                        hypothesis_evaluation = _status_feedback_hint(
                            status,
                            feedback_text,
                            current_signals,
                            current_experience_mode
                        )
                        _eval_logger.info(
                            "hyp_eval user_input=%r mode=%s structured_id=%r status=%s matched_signals=%s reason=%r",
                            action_context.get("reasoning", f"hypothesis:{theory_id}"),
                            current_experience_mode,
                            theory_id,
                            status,
                            current_signals,
                            feedback_text,
                        )
                
                # Always check terminal state after hypothesis validation
                # (win condition in Guided Simulation is validating all core hypotheses)
                current_engine._evaluate_terminal_state()
            
            # AI loop step 1: evaluate intent (hypothesis test)
            if current_engine.ai_opponent:
                label = hypothesis.label if hypothesis else theory_id
                pseudo_action = Action(
                    id=f"hypothesis_test:{theory_id}",
                    label=label,
                    description="Hypothesis test",
                    type="hypothesis"
                )
                ai_intent = current_engine.ai_opponent.evaluate_intent(
                    pseudo_action,
                    hypothesis_id=theory_id,
                    hypothesis_label=label
                )
                # AI loop step 3: choose counter-actions based on updated state
                ai_actions = current_engine.ai_opponent.react_to_action(
                    pseudo_action,
                    current_engine.state,
                    current_engine.available_actions,
                    ai_intent,
                    current_engine.mode
                )
                # AI loop step 4: apply counter-actions (observable effects)
                current_engine.apply_ai_actions(ai_actions)
        
        # Handle commands (for playground/advanced modes)
        elif input_data.startswith("command:"):
            command = input_data.split(":", 1)[1]
            # Process abstract command
            _, ai_actions = _process_command(command, current_engine)
            
            # AI loop for command-based action
            if current_engine.ai_opponent:
                last_action_id = None
                if current_engine.state.action_history:
                    last_action_id = current_engine.state.action_history[-1].get("action_id")
                action_obj = next((a for a in current_engine.available_actions if a.id == last_action_id), None)
                cost = getattr(action_obj, "time_cost", 1) if action_obj else 1
                for _ in range(cost):
                    if current_engine.state.scenario_state != "active":
                        break
                    ai_intent = current_engine.ai_opponent.evaluate_intent(action_obj)
                    new_actions = current_engine.ai_opponent.react_to_action(
                        action_obj,
                        current_engine.state,
                        current_engine.available_actions,
                        ai_intent,
                        current_engine.mode
                    )
                    ai_actions.extend(new_actions)
                    current_engine.apply_ai_actions(new_actions)
        
        # Handle standard actions
        else:
            print(f"Processing action: {input_data}")
            _, ai_actions = current_engine.process_action(input_data)
            
            # AI loop step 1: evaluate intent from action
            if current_engine.ai_opponent:
                action_obj = next((a for a in current_engine.available_actions if a.id == input_data), None)
                cost = getattr(action_obj, "time_cost", 1) if action_obj else 1
                for _ in range(cost):
                    if current_engine.state.scenario_state != "active":
                        break
                    ai_intent = current_engine.ai_opponent.evaluate_intent(action_obj)
                    # AI loop step 3: choose counter-actions based on updated state
                    new_actions = current_engine.ai_opponent.react_to_action(
                        action_obj,
                        current_engine.state,
                        current_engine.available_actions,
                        ai_intent,
                        current_engine.mode
                    )
                    ai_actions.extend(new_actions)
                    # AI loop step 4: apply counter-actions (observable effects)
                    current_engine.apply_ai_actions(new_actions)
        
        # Return updated state
        updated_response = _engine_state_to_api_response(
            current_engine,
            current_mentor,
            ai_actions,
            hypothesis_evaluation=hypothesis_evaluation
        )
        print(f"After action - Actions: {len(updated_response.get('availableActions', []))}, Turn: {updated_response.get('turnCount', 0)}")
        return updated_response
        
    except Exception as e:
        print(f"Error in process_action: {e}")
        traceback.print_exc()
        raise


def _process_command(command: str, engine: SimulationEngine):
    """Process abstract conceptual command"""
    # Map commands to actions
    command_map = {
        "probe_flows": "probe_flows",
        "inspect_evaluation_paths": "inspect_evaluation_paths",
        "alter_boundaries": "alter_boundaries",
        "escalate_context": "escalate_context",
        "isolate_components": "isolate_components",
        "restrict_execution": "restrict_execution",
        "monitor_anomalies": "monitor_anomalies"
    }
    
    action_id = command_map.get(command, command)
    return engine.process_action(action_id)


def toggle_mentor():
    """Toggle mentor AI on/off"""
    global current_mentor
    if current_mentor:
        if current_mentor.enabled:
            current_mentor.disable()
        else:
            current_mentor.enable()
    return current_mentor.enabled if current_mentor else False


def get_mentor_analysis():
    """Get mentor analysis of current situation"""
    global current_engine, current_mentor
    
    if not current_engine:
        raise ValueError("No active simulation")
    
    # Get last action object if available
    last_action_obj = None
    if current_engine.state.action_history:
        last_action_id = current_engine.state.action_history[-1].get("action_id")
        last_action_obj = next((a for a in current_engine.available_actions if a.id == last_action_id), None)
    
    # Get available actions (filter visible ones)
    available_actions = [a for a in current_engine.available_actions if a.visible]
    
    # Get mentor analysis with full context
    guidance = current_mentor.get_guidance(
        current_engine.state,
        last_action_obj,
        current_engine.state.action_history,
        available_actions,
        current_engine.hypotheses
    )
    
    return guidance


def get_learning_data():
    """Extract learning data from current session"""
    global current_engine, current_analytics, session_start_time
    
    if not current_engine:
        return None
    
    # Extract learning data
    learning_data = current_analytics.extract_learning_data(
        current_engine.state,
        current_engine.hypotheses,
        current_engine.state.action_history
    )
    
    # Calculate session duration
    duration = 0
    if session_start_time:
        duration = int((datetime.datetime.now() - session_start_time).total_seconds())
    
    # Create session record
    session = LearningSession(
        session_id=f"session_{datetime.datetime.now().timestamp()}",
        mode=current_engine.mode.value,
        scenario_id=current_engine.scenario_id,
        duration=duration,
        assumptions=learning_data["assumptions"],
        strategies=learning_data["strategies"],
        failures=learning_data["failures"],
        concepts_touched=learning_data["concepts"],
        revisions=learning_data["revisions"],
        final_state=current_engine._get_state_dict()
    )
    
    # Record session
    current_analytics.record_session(session)
    
    return {
        "learning_data": learning_data,
        "recommendations": current_analytics.recommend_scenarios(),
        "curriculum_adjustment": current_analytics.get_curriculum_adjustment()
    }
