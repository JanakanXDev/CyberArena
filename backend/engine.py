"""
Main Engine Interface for CyberArena
Integrates simulation engine, AI systems, and learning analytics
"""

import datetime
import traceback
from simulation_engine import SimulationEngine, LearningMode, Hypothesis, Phase
from ai_systems import OpponentAI, MentorAI, AIPersona, AIDifficulty
from scenario_system import get_scenario_config
from learning_analytics import LearningAnalytics, LearningSession

# Global state
current_engine: SimulationEngine = None
current_mentor: MentorAI = None
current_analytics: LearningAnalytics = LearningAnalytics()
session_start_time: datetime.datetime = None


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


def _engine_state_to_api_response(engine: SimulationEngine, mentor: MentorAI) -> dict:
    """Convert engine state to API response format"""
    state_dict = engine._get_state_dict()
    
    # Get logs from system state
    logs = []
    
    # Initial system log
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
    
    # System view logs (partial, noisy signals)
    for comp_id, comp_data in engine.state.system_components.items():
        if comp_data.get("monitoring"):
            logs.append(create_log(
                comp_id,
                "system_view",
                "info",
                f"Monitoring active on {comp_id}",
                logs
            ))
    
    # Event log (cause-effect traces)
    if engine.state.action_history:
        last_action = engine.state.action_history[-1]
        logs.append(create_log(
            "Operator",
            "event_log",
            "info",
            f"Action executed: {last_action.get('action_id', 'unknown')}",
            logs
        ))
    
    # Delayed consequences triggered
    for dc in engine.delayed_consequences:
        if dc.executed and dc.trigger_turn == engine.turn_count:
            logs.append(create_log(
                "System",
                "event_log",
                "warning",
                f"Delayed consequence: {dc.description}",
                logs
            ))
    
    # Contradictions
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
    
    # AI opponent activity
    if engine.ai_opponent:
        if engine.state.active_defenses:
            logs.append(create_log(
                "AI Defender" if engine.ai_opponent.persona == AIPersona.DEFENDER else "AI Attacker",
                "system_view",
                "warning",
                f"AI activity detected: {', '.join(engine.state.active_defenses[-2:])}",
                logs
            ))
        if engine.state.active_attacks:
            logs.append(create_log(
                "AI Attacker",
                "system_view",
                "error",
                f"Active attack: {', '.join(engine.state.active_attacks[-2:])}",
                logs
            ))
    
    # Mentor guidance (if enabled)
    mentor_guidance = None
    if mentor and mentor.enabled:
        last_action_obj = None
        if engine.state.action_history:
            last_action_id = engine.state.action_history[-1].get("action_id")
            last_action_obj = next((a for a in engine.available_actions if a.id == last_action_id), None)
        mentor_guidance = mentor.get_guidance(engine.state, last_action_obj)
    
    # Build response
    response = {
        "mode": engine.mode.value,
        "scenarioId": engine.scenario_id,
        "scenarioName": _get_scenario_name(engine.scenario_id),
        "turnCount": engine.turn_count,
        
        # Metrics (shown in state panel)
        "riskScore": engine.state.risk_score,
        "detectionLevel": engine.state.detection_level,
        "integrity": engine.state.integrity,
        "aiAggressiveness": engine.state.ai_aggressiveness,
        
        # Actions (hypothesis-based, no exploit names)
        "availableActions": state_dict["available_actions"],
        
        # Hypotheses
        "hypotheses": state_dict["hypotheses"],
        
        # Logs
        "logs": logs,
        
        # System state (for system view)
        "systemComponents": state_dict["system_components"],
        "vulnerabilities": state_dict["vulnerabilities"],
        
        # Learning data
        "userAssumptions": state_dict["user_assumptions"],
        "actionHistory": state_dict["action_history"],
        "contradictions": state_dict["contradictions"],
        
        # Mentor guidance
        "mentorGuidance": mentor_guidance,
        
        # No phase shown to user (internal only)
        # No completion flags (continuous simulation)
        "isGameOver": False,
        "missionComplete": False
    }
    
    return response


def _get_scenario_name(scenario_id: str) -> str:
    """Get scenario display name"""
    names = {
        "input_trust_failures": "Operation: Broken Trust",
        "linux_privesc": "Operation: Glass Ceiling",
        "network_breach": "Operation: Silent Echo"
    }
    return names.get(scenario_id, "Unknown Mission")


def reset_game(mode: str, difficulty: str, scenario_id: str, stage_index: int = 0):
    """Initialize new game session"""
    global current_engine, current_mentor, session_start_time
    
    try:
        # Convert mode string to enum
        mode_enum = _mode_string_to_enum(mode)
        
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
        initial_response = _engine_state_to_api_response(current_engine, current_mentor)
        print(f"Initial state - Actions: {len(initial_response.get('availableActions', []))}, Hypotheses: {len(initial_response.get('hypotheses', []))}")
        print(f"Available action IDs: {[a.get('id') for a in initial_response.get('availableActions', [])]}")
        return initial_response
        
    except Exception as e:
        print(f"Error in reset_game: {e}")
        traceback.print_exc()
        raise


def process_action(input_data: str):
    """Process user action or command"""
    global current_engine, current_mentor
    
    if not current_engine:
        raise ValueError("No active simulation. Call reset_game first.")
    
    try:
        # Handle hypothesis testing
        if input_data.startswith("hypothesis:"):
            theory_id = input_data.split(":")[1]
            
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
                # Validate hypothesis - check against config
                hyp_config = current_engine._hypotheses_config.get(theory_id)
                if hyp_config:
                    validated = hyp_config.get("correct", False)
                    current_engine.validate_hypothesis(theory_id, validated)
                else:
                    # If not in config, create from available hypotheses in state
                    state_dict = current_engine._get_state_dict()
                    hyp_data = next((h for h in state_dict.get("hypotheses", []) 
                                   if h.get("id") == theory_id), None)
                    if hyp_data:
                        # Create hypothesis object
                        hypothesis = Hypothesis(
                            id=hyp_data["id"],
                            label=hyp_data["label"],
                            description=hyp_data.get("description", ""),
                            timestamp=datetime.datetime.now()
                        )
                        current_engine.add_hypothesis(hypothesis)
                        # Try to validate
                        hyp_config = current_engine._hypotheses_config.get(theory_id)
                        if hyp_config:
                            validated = hyp_config.get("correct", False)
                            current_engine.validate_hypothesis(theory_id, validated)
        
        # Handle commands (for playground/advanced modes)
        elif input_data.startswith("command:"):
            command = input_data.split(":", 1)[1]
            # Process abstract command
            _process_command(command, current_engine)
        
        # Handle standard actions
        else:
            print(f"Processing action: {input_data}")
            current_engine.process_action(input_data)
        
        # Return updated state
        updated_response = _engine_state_to_api_response(current_engine, current_mentor)
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
    engine.process_action(action_id)


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
