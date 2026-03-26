"""
Scenario System for CyberArena
Supports four learning modes with appropriate scenario configurations.
Enforces strict mental model separation between modes.
"""

from typing import Dict, Any
from simulation_engine import LearningMode
from ai_systems import AIPersona, AIDifficulty
import random


def get_scenario_config(scenario_id: str, mode: LearningMode, difficulty: str) -> Dict[str, Any]:
    """Get scenario configuration based on mode and difficulty"""

    # Base Architecture Model (Scenario Specific)
    # Scenario: input_trust_failures
    # Model: Legacy Admin Portal (Java/Tomcat style) behind a WAF.
    # Architecture: User -> WAF -> WebApp -> Logic -> DB.
    # Trust Assumption: "WAF handles security, so WebApp logic trusts the input."
    
    base_scenarios = {
        "level_0_tutorial": {
            "title": "Level 0: The Evidence Loop",
            "description": "Tutorial: Learn how to gather evidence before forming hypotheses.",
            "initial_state": {
                "pressure": 0,
                "stability": 100
            },
            "system_components": {
                "tutorial_system": {"status": "operational", "monitoring": False, "hardened": False}
            },
            "vulnerabilities": {}
        },
        "input_trust_failures": {
            "title": "Operation: Broken Trust",
            "description": "Legacy admin portal with brittle input handling",
            "initial_state": {
                "pressure": 5,
                "stability": 100
            },
            "system_components": {
                "web_server": {"status": "operational", "monitoring": False, "hardened": False},
                "database": {"status": "operational", "monitoring": False, "hardened": False},
                "waf": {"status": "operational", "monitoring": False, "hardened": False}
            },
            "vulnerabilities": {
                "decision_path_influence": {
                    "active": True, 
                    "severity": "high", 
                    "false_lead": False, 
                    "interactions": ["input_boundary"]
                },
                "reflection_surface": {
                    "active": True, 
                    "severity": "medium", 
                    "false_lead": True, 
                    "interactions": ["input_boundary"]
                },
                "input_boundary": {
                    "active": True, 
                    "severity": "high", 
                    "false_lead": False, 
                    "interactions": ["decision_path_influence", "reflection_surface"]
                }
            }
        }
    }

    base = base_scenarios.get(scenario_id, base_scenarios["input_trust_failures"])

    # Phase 1: BREAK DETERMINISM (Randomize boot state parameters)
    if scenario_id != "level_0_tutorial":
        # Randomize baseline pressure
        base["initial_state"]["pressure"] = max(0, base["initial_state"]["pressure"] + random.randint(-5, 10))
        
        # Randomize secondary vulnerabilities
        if "reflection_surface" in base.get("vulnerabilities", {}):
            base["vulnerabilities"]["reflection_surface"]["active"] = random.choice([True, False])
            
        # Randomize baseline monitoring
        if "waf" in base.get("system_components", {}):
            base["system_components"]["waf"]["monitoring"] = random.choice([True, False])

    if scenario_id == "level_0_tutorial":
        return _configure_tutorial_scenario(base, mode)

    # Configure strictly based on mode to enforce distinct mental environments
    if mode == LearningMode.GUIDED_SIMULATION:
        return _configure_guided_simulation_trust(base, difficulty)
    if mode == LearningMode.ATTACKER_CAMPAIGN:
        return _configure_attacker_campaign_trust(base, difficulty)
    if mode == LearningMode.DEFENDER_CAMPAIGN:
        return _configure_defender_campaign_trust(base, difficulty)
    if mode == LearningMode.PLAYGROUND:
        return _configure_playground_trust(base, difficulty)

    return base


def _configure_guided_simulation_trust(base: Dict[str, Any], difficulty: str) -> Dict[str, Any]:
    """
    Scenario: Input Trust Failures
    Mode: Guided Simulation
    Mental Model: "The Analyst" - Understanding how data flows and where trust breaks.
    Hypotheses: System behavior and architecture.
    """
    config = base.copy()
    config["ai_persona"] = AIPersona.DEFENDER
    config["ai_difficulty"] = AIDifficulty.RULE_BASED

    config["hypotheses"] = [
        {
            "id": "hyp_validation_layer",
            "label": "Validation occurs at the WAF, leaving the app exposed",
            "description": "The logic layer might assume all input is clean if it passes the gateway.",
            "correct": True,
            "evidence_required": ["act_map_boundaries"],
            "why_correct": "✓ Correct. The WAF filters traffic first, and the app trusts whatever gets through. This is the core flaw — the backend never re-validates input, so anything that slips past the WAF reaches the logic layer unchecked.",
            "why_wrong": "✗ Wrong. Validation is actually applied server-side as well — the WAF alone isn't the last checkpoint."
        },
        {
            "id": "hyp_error_oracle",
            "label": "Verbose errors indicate internal logic flow",
            "description": "Stack traces or messages might reveal the decision tree structure.",
            "correct": False,
            "evidence_required": ["act_trigger_exception"],
            "why_correct": "✓ This turned out to be true here — the error messages do leak stack traces. But be careful: this is a lucky find, not a reliable technique.",
            "why_wrong": "✗ Incorrect. The application suppresses detailed errors before they reach the client. You're seeing generic failure messages, not actual stack traces. This was a decoy path — verbose error leakage is a real vulnerability but it's not present here."
        },
        {
            "id": "hyp_state_persistence",
            "label": "Session state persists across invalid requests",
            "description": "Failed inputs might still alter the session context for subsequent requests.",
            "correct": True,
            "evidence_required": ["act_corrupt_session"],
            "why_correct": "✓ Correct. The server commits partial session changes before the request fully validates. A failed login still writes a partial auth token to the session — meaning your next request arrives with elevated context the server didn't intend to grant.",
            "why_wrong": "✗ Wrong. Session state is rolled back completely on failed requests; each new attempt starts from a clean slate."
        }
    ]

    # ACTIONS (Exploratory Experiments)
    config["actions"] = [
        {
            "id": "act_map_boundaries",
            "label": "Map input size constraints",
            "description": "Send varying lengths to define the accepted window.",
            "type": "probe",
            "pressure_delta": 2,
            "delayed_effects": [{"turn_delay": 3, "description": "WAF calibrates to request size", "pressure_delta": 3}]
        },
        {
            "id": "act_trigger_exception",
            "label": "Induce type mismatch",
            "description": "Send arrays where strings are expected to observe handling.",
            "type": "inspect",
            "pressure_delta": 4,
            "immediate_effect": {"component_modified": "web_server", "modification": {"monitoring": True}}
        },
        {
            "id": "act_corrupt_session",
            "label": "Inject state marker",
            "description": "Attempt to plant a marker in session storage via failed login.",
            "type": "escalate",
            "pressure_delta": 5,
            "stability_delta": -2,
            "immediate_effect": {"vulnerability_exploited": "decision_path_influence"}
        },
        {
            "id": "act_observe_signals",
            "label": "Passive traffic observation",
            "description": "Watch for timing anomalies without interacting.",
            "type": "monitor",
            "pressure_delta": 1,
            "visible": True
        }
    ]
    
    # Note: AI reactions in Guided are subtle (logging, monitoring)
    return config


def _configure_attacker_campaign_trust(base: Dict[str, Any], difficulty: str) -> Dict[str, Any]:
    """
    Scenario: Input Trust Failures
    Mode: Attacker Campaign
    Mental Model: "The Infiltrator" - Evasion, stealth, and bypassing active countermeasures.
    Hypotheses: Defense adaptation and blind spots.
    """
    config = base.copy()
    config["ai_persona"] = AIPersona.DEFENDER
    config["ai_difficulty"] = AIDifficulty.ADAPTIVE

    # HYPOTHESES (Defense Reaction)
    config["hypotheses"] = [
        {
            "id": "hyp_rate_limiting",
            "label": "Defenses trigger on frequency, not content",
            "description": "Slow, complex attacks might bypass the automated blocks.",
            "correct": True,
            "evidence_required": ["act_slow_drip"],
            "why_correct": "✓ Correct. The WAF uses request-rate thresholds, not deep payload analysis. Spreading your requests out over time avoids the trigger window entirely — the defender only sees noise, not a pattern.",
            "why_wrong": "✗ Wrong. Content inspection is actually active here — payload patterns are being matched regardless of rate."
        },
        {
            "id": "hyp_honeypot_detection",
            "label": "The admin login is a decoy endpoint",
            "description": "Obvious entry points are likely monitored traps.",
            "correct": False,
            "evidence_required": ["act_identify_outliers"],
            "why_correct": "✓ You were right to be suspicious — this endpoint does have elevated logging.",
            "why_wrong": "✗ Wrong. The admin endpoint is real, not a honeypot — just heavily monitored. Touching it triggered an alert. Don't confuse 'being watched' with 'being fake'."
        },
        {
            "id": "hyp_log_saturation",
            "label": "High noise levels will mask injection attempts",
            "description": "Flooding logs might hide the specific successful exploit.",
            "correct": False,
            "evidence_required": ["act_noise_flood"],
            "why_correct": "✓ In this case noise helped mask the timing.",
            "why_wrong": "✗ Wrong — and costly. The AI correlates log volume spikes as attack indicators. Flooding actually made you MORE visible, not less. The defender's system flagged the unusual request rate and hardened the WAF in response."
        }
    ]

    # ACTIONS (Stealth and Evasion)
    config["actions"] = [
        {
            "id": "act_slow_drip",
            "label": "Inject payload over multiple requests",
            "description": "Fragment the payload to evade signature detection.",
            "type": "stealth_probe",
            "pressure_delta": 1,
            "delayed_effects": [{"turn_delay": 5, "description": "Correlation engine reconstructs fragments", "pressure_delta": 8}]
        },
        {
            "id": "act_identify_outliers",
            "label": "Fingerprint response timing",
            "description": "Find endpoints that deviate from the decoy timing profile.",
            "type": "inspect",
            "pressure_delta": 2
        },
        {
            "id": "act_noise_flood",
            "label": "Generate background traffic",
            "description": "Flood valid requests to mask the attack signal. (Costs 2 actions)",
            "type": "escalate",
            "pressure_delta": 15,
            "time_cost": 2,
            "stability_delta": -5,
            "immediate_effect": {"component_modified": "waf", "modification": {"hardened": True}}
            # This action will likely trigger Antigravity Strategy Spamming/Tunnel Vision analysis
        },
        {
            "id": "act_execution_jump",
            "label": "Pivot to underlying shell",
            "description": "Use the trust failure to exit the application context.",
            "type": "pivot",
            "pressure_delta": 10,
            "stability_delta": -10,
            "immediate_effect": {"vulnerability_exploited": "input_boundary"}
        }
    ]
    
    # AI will aggressively patch vulnerabilities if noise is detected
    config["delayed_consequences"] = [
        {
            "id": "dc_adaptive_block",
            "trigger_action_id": "act_noise_flood",
            "trigger_turn": 1, 
            "description": "IP range blocked by adaptive firewall",
            "pressure_delta": 20
        }
    ]

    return config


def _configure_defender_campaign_trust(base: Dict[str, Any], difficulty: str) -> Dict[str, Any]:
    """
    Scenario: Input Trust Failures
    Mode: Defender Campaign
    Mental Model: "The SRE/SecOps" - Containment, stability, and forensic analysis.
    Hypotheses: Attack persistence and impact.
    """
    config = base.copy()
    config["ai_persona"] = AIPersona.ATTACKER
    config["ai_difficulty"] = AIDifficulty.DECEPTIVE
    
    # Pre-breached state
    config["initial_state"]["pressure"] = 40
    config["initial_state"]["stability"] = 70

    # HYPOTHESES (Attack Persistence)
    config["hypotheses"] = [
        {
            "id": "hyp_persistence_method",
            "label": "Attacker is using scheduled tasks for return",
            "description": "The instability correlates with specific time windows.",
            "correct": True,
            "evidence_required": ["act_audit_cron"],
            "why_correct": "✓ Correct. The attacker planted a cron job during initial compromise. It re-runs payloads every few hours. This is why instability comes in waves — it's not human, it's automated recurrence.",
            "why_wrong": "✗ Wrong. The instability is continuous, not time-windowed — it's an active session, not a scheduled task."
        },
        {
            "id": "hyp_data_exfiltration",
            "label": "Outbound database traffic is exfiltration",
            "description": "Volume anomalies suggest data theft in progress.",
            "correct": False,
            "evidence_required": ["act_deep_forensics"],
            "why_correct": "✓ The traffic pattern does suggest exfiltration.",
            "why_wrong": "✗ Wrong. The traffic is a resource exhaustion attack (DoS), not exfiltration. The attacker is hammering the database to cause service failure, not to steal data. Throttling outbound bandwidth simply caused a queue backup and crashed the service."
        },
        {
            "id": "hyp_breach_scope",
            "label": "Web server is the only compromised asset",
            "description": "Database logs show no direct unauthorized access.",
            "correct": False,
            "why_correct": "✓ You correctly inferred the web server as the entry point.",
            "why_wrong": "✗ Wrong. Lateral movement already occurred. The attacker pivoted from the web server to the database host using the app's service account credentials — which the database logs as legitimate access. This is why the logs look clean: the attacker is hiding inside trusted traffic."
        }
    ]

    # ACTIONS (Detection and Response)
    config["actions"] = [
        {
            "id": "act_audit_cron",
            "label": "Audit scheduled jobs",
            "description": "Execute once — scans system schedulers for unauthorized cron entries. After clicking, go test the 'Attacker is using scheduled tasks' hypothesis to confirm what you found.",
            "type": "inspect",
            "pressure_delta": 2
        },
        {
            "id": "act_traffic_shaping",
            "label": "Throttle database outbound",
            "description": "Execute once — restricts bandwidth on database outbound connections. Warning: if the outbound traffic isn't exfiltration, this may cause other problems.",
            "type": "restrict",
            "pressure_delta": 5,
            "stability_delta": 5,
            # This is a trap action: fixing the wrong problem (DoS, not exfil) triggers DoS escalation
            "delayed_effects": [{"turn_delay": 2, "description": "Service crashes due to queue backup (DoS successful)", "stability_delta": -20}]
        },
        {
            "id": "act_quarantine_web",
            "label": "Isolate web server",
            "description": "Execute once — cuts all network access to the web tier. Use after confirming the attacker is using scheduled tasks, to prevent re-entry.",
            "type": "isolate",
            "pressure_delta": -10,
            "stability_delta": -5,
            "hypothesis_required": "hyp_persistence_method"
        },
        {
            "id": "act_deep_forensics",
            "label": "Memory forensics",
            "description": "Execute once — dumps and analyzes RAM to find resident malware. Useful at any time. Raises pressure slightly but may reveal hidden processes. (Costs 3 actions)",
            "type": "monitor",
            "time_cost": 3,
            "pressure_delta": 5
        }
    ]

    return config




def _configure_playground_trust(base: Dict[str, Any], difficulty: str) -> Dict[str, Any]:
    """
    Scenario: Input Trust Failures
    Mode: Playground
    Mental Model: "The Chaos Engineer" - Unlimited testing, high risk, high consequence.
    Hypotheses: Optional, emergent.
    """
    config = base.copy()
    config["ai_opponent_optional"] = True
    config["no_objectives"] = True
    config["allow_destruction"] = True

    # HYPOTHESES (Emergent / Optional)
    config["hypotheses"] = [
        {
            "id": "hyp_chaos_theory",
            "label": "System stability is inversely proportional to input entropy",
            "description": "Maximum randomness will eventually find a crash dump.",
            "correct": True
        }
    ]

    # ACTIONS (Unrestricted / Risky)
    config["actions"] = [
        {
            "id": "act_fuzz_all",
            "label": "Fuzz all endpoints concurrently",
            "description": "Maximum throughput random input generation. (Costs 2 actions)",
            "type": "stress",
            "available": True,
            "time_cost": 2,
            "pressure_delta": 30,
            "stability_delta": -40,
            "immediate_effect": {"vulnerability_exploited": "input_boundary"}
        },
        {
            "id": "act_bypass_controls",
            "label": "Disable local validation mechanisms",
            "description": "Strip client-side checks to send raw payloads.",
            "type": "alter",
            "available": True,
            "pressure_delta": 10
        },
        {
            "id": "act_overload_backend",
            "label": "Trigger race conditions",
            "description": "Send concurrent conflicting state updates.",
            "type": "escalate",
            "available": True,
            "pressure_delta": 20,
            "stability_delta": -30,
            "delayed_effects": [{"turn_delay": 1, "description": "Database Deadlock", "stability_delta": -50}]
        }
    ]

    return config

def get_focused_content(scenario_id: str, mode: LearningMode, role: str, component: str) -> Dict[str, Any]:
    """Get dynamically generated content focused on a specific role and component"""
    # Get the base configuration for the mode
    base_config = get_scenario_config(scenario_id, mode, "medium")
    
    focused_actions = []
    for a in base_config.get("actions", []):
        # Adapt the label to mention the component to ensure it's component-specific
        new_action = a.copy()
        if f"[{component.upper()}]" not in new_action["label"]:
            new_action["label"] = f"[{component.upper()}] {new_action['label']}"
        focused_actions.append(new_action)
    
    focused_hypotheses = []
    for h in base_config.get("hypotheses", []):
        new_hyp = h.copy()
        if "Focus:" not in new_hyp["label"]:
            new_hyp["label"] = f"{new_hyp['label']} (Focus: {component})"
        focused_hypotheses.append(new_hyp)
        
    # Ensure role-specific actions are always available (preventing dead states)
    if role == "attacker":
        focused_actions.append({
            "id": f"act_focused_attack_{component}",
            "label": f"[{component.upper()}] Launch directed exploit",
            "description": f"Test edge-case vulnerabilities specifically on {component}",
            "type": "escalate",
            "pressure_delta": 10,
            "stability_delta": -5
        })
    elif role == "defender":
        focused_actions.append({
            "id": f"act_focused_defend_{component}",
            "label": f"[{component.upper()}] Heighten surveillance",
            "description": f"Enact strict validation and monitoring specifically on {component}",
            "type": "monitor",
            "pressure_delta": 2,
            "stability_delta": 5
        })
        
        
    win_conditions = []
    loss_conditions = []
    max_phase = 5
    
    if mode == LearningMode.GUIDED_SIMULATION:
        win_conditions = [{"type": "hypothesis_validated", "target": "all_core_hypotheses"}]
        loss_conditions = [{"type": "pressure_threshold", "target": 100}]
        max_phase = 3
    elif mode == LearningMode.ATTACKER_CAMPAIGN:
        win_conditions = [{"type": "objective_achieved", "target": "escalate"}]
        loss_conditions = [{"type": "detection_threshold", "target": "critical"}]
        max_phase = 4
    elif mode == LearningMode.DEFENDER_CAMPAIGN:
        win_conditions = [{
            "type": "hypothesis_and_action",
            "hypothesis_id": "hyp_persistence_method",
            "action_id": "act_audit_cron"
        }]
        loss_conditions = [
            {"type": "pressure_threshold", "target": 90},
            {"type": "stability_threshold", "target": 15},
        ]
        max_phase = 5
    elif mode == LearningMode.PLAYGROUND:
        win_conditions = [] # Sandbox mode never auto-ends intentionally
        loss_conditions = []
        max_phase = 99
        
    return {
        "actions": focused_actions,
        "hypotheses": focused_hypotheses,
        "win_conditions": win_conditions,
        "loss_conditions": loss_conditions,
        "max_phase": max_phase
    }

def _configure_tutorial_scenario(base: Dict[str, Any], mode: LearningMode) -> Dict[str, Any]:
    """
    Tutorial Scenario: The Evidence Loop
    Teaches the player they must gather evidence before clicking hypotheses.
    """
    config = base.copy()
    from ai_systems import AIPersona, AIDifficulty
    config["ai_persona"] = AIPersona.DEFENDER
    config["ai_difficulty"] = AIDifficulty.RULE_BASED
    
    config["hypotheses"] = [
        {
            "id": "hyp_tutorial",
            "label": "I must gather evidence before concluding",
            "description": "Clicking this before 'Gather Evidence' will result in a penalty.",
            "correct": True,
            "evidence_required": ["act_gather_evidence"],
            "why_correct": "✓ Excellent! You learned that Hypotheses require Evidence Actions to be performed first.",
            "why_wrong": ""
        }
    ]
    
    config["actions"] = [
        {
            "id": "act_gather_evidence",
            "label": "Gather Evidence",
            "description": "Always execute actions like this first to uncover evidence and unlock hypotheses.",
            "type": "inspect",
            "pressure_delta": 0,
            "time_cost": 1
        }
    ]
    
    # Simple win condition: validate the tutorial hypothesis
    config["win_conditions"] = [{
        "type": "hypothesis_validated",
        "hypothesis_id": "hyp_tutorial"
    }]
    
    return config
