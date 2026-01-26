"""
Scenario System for CyberArena
Supports four learning modes with appropriate scenario configurations
"""

from typing import Dict, List, Any
from simulation_engine import LearningMode, Phase
from ai_systems import AIPersona, AIDifficulty


def get_scenario_config(scenario_id: str, mode: LearningMode, difficulty: str) -> Dict[str, Any]:
    """Get scenario configuration based on mode and difficulty"""
    
    base_scenarios = {
        "input_trust_failures": {
            "title": "Operation: Broken Trust",
            "description": "Legacy admin portal with input validation flaws",
            "initial_state": {
                "risk": 5,
                "detection": 0,
                "integrity": 100
            },
            "vulnerabilities": {
                "sql_injection": {
                    "active": True,
                    "severity": "high",
                    "false_lead": False,
                    "interactions": ["input_validation"]
                },
                "xss_reflected": {
                    "active": True,
                    "severity": "medium",
                    "false_lead": True,  # This is a false lead
                    "interactions": ["input_validation"]
                },
                "input_validation": {
                    "active": True,
                    "severity": "high",
                    "false_lead": False,
                    "interactions": ["sql_injection", "xss_reflected"]
                }
            },
            "system_components": {
                "web_server": {
                    "status": "operational",
                    "monitoring": False,
                    "hardened": False
                },
                "database": {
                    "status": "operational",
                    "monitoring": False,
                    "hardened": False
                },
                "waf": {
                    "status": "operational",
                    "monitoring": False,
                    "hardened": False
                }
            }
        }
    }
    
    base = base_scenarios.get(scenario_id, base_scenarios["input_trust_failures"])
    
    # Configure based on mode
    if mode == LearningMode.GUIDED_SIMULATION:
        return _configure_guided_simulation(base, difficulty)
    elif mode == LearningMode.ATTACKER_CAMPAIGN:
        return _configure_attacker_campaign(base, difficulty)
    elif mode == LearningMode.DEFENDER_CAMPAIGN:
        return _configure_defender_campaign(base, difficulty)
    elif mode == LearningMode.PLAYGROUND:
        return _configure_playground(base, difficulty)
    
    return base


def _configure_guided_simulation(base: Dict[str, Any], difficulty: str) -> Dict[str, Any]:
    """Configure for Guided Simulation Mode"""
    config = base.copy()
    
    # Actions are hypothesis-based, no exploit names
    config["actions"] = [
        {
            "id": "probe_input_boundaries",
            "label": "Probe input validation boundaries",
            "description": "Test how the system handles unexpected input patterns",
            "type": "probe",
            "risk_delta": 5,
            "detection_delta": 2,
            "immediate_effect": {
                "component_modified": "web_server",
                "modification": {"monitoring": True}
            },
            "delayed_effects": [
                {
                    "turn_delay": 2,
                    "description": "Previous probe triggered logging",
                    "detection_delta": 5
                }
            ]
        },
        {
            "id": "inspect_evaluation_paths",
            "label": "Inspect how inputs are evaluated",
            "description": "Examine the flow of user input through system components",
            "type": "inspect",
            "risk_delta": 0,
            "detection_delta": 1,
            "hypothesis_required": "theory_input_flow"
        },
        {
            "id": "test_boolean_conditions",
            "label": "Test boolean condition manipulation",
            "description": "Attempt to alter logical conditions in system queries",
            "type": "escalate",
            "risk_delta": 15,
            "detection_delta": 5,
            "integrity_delta": -20,
            "hypothesis_required": "theory_boolean_logic",
            "immediate_effect": {
                "vulnerability_exploited": "sql_injection"
            },
            "delayed_effects": [
                {
                    "turn_delay": 3,
                    "description": "Exploitation detected by anomaly detection",
                    "detection_delta": 15
                }
            ]
        },
        {
            "id": "isolate_vulnerable_component",
            "label": "Isolate vulnerable component",
            "description": "Restrict access to the component showing anomalous behavior",
            "type": "isolate",
            "risk_delta": -10,
            "detection_delta": 0,
            "integrity_delta": 10,
            "immediate_effect": {
                "component_modified": "web_server",
                "modification": {"hardened": True}
            }
        },
        {
            "id": "restrict_execution_context",
            "label": "Restrict execution context",
            "description": "Limit the execution environment for user inputs",
            "type": "restrict",
            "risk_delta": -15,
            "detection_delta": 0,
            "integrity_delta": 15,
            "immediate_effect": {
                "component_modified": "web_server",
                "modification": {"hardened": True}
            },
            "delayed_effects": [
                {
                    "turn_delay": 1,
                    "description": "Restriction exposed new attack surface",
                    "risk_delta": 5
                }
            ]
        }
    ]
    
    # Hypotheses (user must form and test)
    config["hypotheses"] = [
        {
            "id": "theory_input_flow",
            "label": "Input flows directly into database queries",
            "description": "User input is concatenated into SQL queries without sanitization"
        },
        {
            "id": "theory_boolean_logic",
            "label": "Boolean conditions can be manipulated",
            "description": "The system evaluates boolean expressions that can be altered"
        },
        {
            "id": "theory_error_based",
            "label": "Errors reveal system structure",
            "description": "Error messages expose database schema or system internals",
            "correct": False  # This is wrong - WAF suppresses errors
        }
    ]
    
    # Delayed consequences
    config["delayed_consequences"] = [
        {
            "id": "dc_success_fails",
            "trigger_action_id": "test_boolean_conditions",
            "trigger_turn": 4,
            "description": "Previous successful action now fails due to system changes",
            "risk_delta": 10,
            "detection_delta": 5
        }
    ]
    
    # Contradictions
    config["contradictions"] = [
        {
            "id": "contr_error_suppression",
            "assumption_id": "theory_error_based",
            "condition_type": "assumption_validated",
            "description": "Error-based approach fails - WAF suppresses detailed errors",
            "trigger_failure": "previous_success_fails"
        }
    ]
    
    return config


def _configure_attacker_campaign(base: Dict[str, Any], difficulty: str) -> Dict[str, Any]:
    """Configure for Attacker Campaign (user attacks, AI defends)"""
    config = base.copy()
    
    # AI defender is active
    config["ai_persona"] = AIPersona.DEFENDER
    config["ai_difficulty"] = AIDifficulty.ADAPTIVE if difficulty == "medium" else (
        AIDifficulty.DECEPTIVE if difficulty == "hard" else AIDifficulty.RULE_BASED
    )
    
    # Attacker-focused actions
    config["actions"] = [
        {
            "id": "probe_stealthily",
            "label": "Probe system boundaries stealthily",
            "description": "Gather information without triggering alerts",
            "type": "probe",
            "risk_delta": 3,
            "detection_delta": 1
        },
        {
            "id": "escalate_privileges",
            "label": "Attempt privilege escalation",
            "description": "Try to gain elevated access",
            "type": "escalate",
            "risk_delta": 20,
            "detection_delta": 10,
            "integrity_delta": -15
        },
        {
            "id": "pivot_attack",
            "label": "Pivot to different attack vector",
            "description": "Change approach when detected",
            "type": "pivot",
            "risk_delta": 5,
            "detection_delta": -5
        },
        {
            "id": "establish_persistence",
            "label": "Establish persistence mechanism",
            "description": "Create backdoor for continued access",
            "type": "persist",
            "risk_delta": 15,
            "detection_delta": 5,
            "integrity_delta": -25
        }
    ]
    
    return config


def _configure_defender_campaign(base: Dict[str, Any], difficulty: str) -> Dict[str, Any]:
    """Configure for Defender Campaign (user defends, AI attacks)"""
    config = base.copy()
    
    # AI attacker is active
    config["ai_persona"] = AIPersona.ATTACKER
    config["ai_difficulty"] = AIDifficulty.ADAPTIVE if difficulty == "medium" else (
        AIDifficulty.DECEPTIVE if difficulty == "hard" else AIDifficulty.RULE_BASED
    )
    
    # Start with some attacks already in progress
    config["initial_state"]["risk"] = 20
    config["initial_state"]["detection"] = 15
    
    # Defender-focused actions
    config["actions"] = [
        {
            "id": "monitor_anomalies",
            "label": "Monitor system for anomalies",
            "description": "Enable enhanced monitoring and logging",
            "type": "monitor",
            "risk_delta": -5,
            "detection_delta": 10
        },
        {
            "id": "isolate_compromised_component",
            "label": "Isolate potentially compromised component",
            "description": "Restrict network access to suspicious component",
            "type": "isolate",
            "risk_delta": -10,
            "detection_delta": 5,
            "integrity_delta": 10
        },
        {
            "id": "restrict_execution",
            "label": "Restrict execution capabilities",
            "description": "Limit what can be executed in the system",
            "type": "restrict",
            "risk_delta": -15,
            "detection_delta": 0,
            "integrity_delta": 15
        },
        {
            "id": "patch_vulnerability",
            "label": "Apply security patch",
            "description": "Fix identified vulnerability",
            "type": "patch",
            "risk_delta": -20,
            "detection_delta": 0,
            "integrity_delta": 20
        },
        {
            "id": "incident_response",
            "label": "Initiate incident response",
            "description": "Begin formal incident response procedures",
            "type": "respond",
            "risk_delta": -10,
            "detection_delta": 15
        }
    ]
    
    return config


def _configure_playground(base: Dict[str, Any], difficulty: str) -> Dict[str, Any]:
    """Configure for Playground Mode (no fixed objectives, full freedom)"""
    config = base.copy()
    
    # Multiple vulnerabilities active simultaneously
    config["vulnerabilities"].update({
        "command_injection": {
            "active": True,
            "severity": "high",
            "false_lead": False,
            "interactions": ["input_validation"]
        },
        "path_traversal": {
            "active": True,
            "severity": "medium",
            "false_lead": False,
            "interactions": ["input_validation"]
        }
    })
    
    # AI opponent is optional
    config["ai_opponent_optional"] = True
    config["ai_difficulty"] = difficulty
    
    # Expanded action set for playground
    config["actions"] = [
        {
            "id": "probe_flows",
            "label": "Probe data flows",
            "description": "Examine how data moves through the system",
            "type": "probe",
            "risk_delta": 2,
            "detection_delta": 1
        },
        {
            "id": "inspect_evaluation_paths",
            "label": "Inspect evaluation paths",
            "description": "Trace how inputs are evaluated",
            "type": "inspect",
            "risk_delta": 0,
            "detection_delta": 1
        },
        {
            "id": "alter_boundaries",
            "label": "Alter system boundaries",
            "description": "Modify access controls and boundaries",
            "type": "alter",
            "risk_delta": 10,
            "detection_delta": 5,
            "integrity_delta": -10
        },
        {
            "id": "escalate_context",
            "label": "Escalate execution context",
            "description": "Attempt to gain higher privileges",
            "type": "escalate",
            "risk_delta": 20,
            "detection_delta": 10,
            "integrity_delta": -20
        },
        {
            "id": "isolate_components",
            "label": "Isolate system components",
            "description": "Separate components to prevent lateral movement",
            "type": "isolate",
            "risk_delta": -10,
            "detection_delta": 0,
            "integrity_delta": 10
        },
        {
            "id": "restrict_execution",
            "label": "Restrict execution capabilities",
            "description": "Limit what can be executed",
            "type": "restrict",
            "risk_delta": -15,
            "detection_delta": 0,
            "integrity_delta": 15
        },
        {
            "id": "monitor_anomalies",
            "label": "Monitor for anomalies",
            "description": "Enable monitoring and alerting",
            "type": "monitor",
            "risk_delta": -5,
            "detection_delta": 10
        },
        {
            "id": "destroy_integrity",
            "label": "Test system destruction",
            "description": "Intentionally break system to test recovery",
            "type": "destroy",
            "risk_delta": 30,
            "detection_delta": 20,
            "integrity_delta": -50
        }
    ]
    
    # No fixed objectives, no fail screens
    config["no_objectives"] = True
    config["allow_destruction"] = True
    
    return config
