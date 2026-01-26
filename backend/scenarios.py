SCENARIOS = {
    "input_trust_failures": {
        "chapter_id": "input_trust_failures",
        "title": "Operation: Broken Trust",
        "description": "Live-fire exercise. Detection is active.",
        "stages": [
            # === PHASE 1: RECON ===
            {
                "stage_id": "recon",
                "title": "Phase 1: Analysis",
                "phase": "RECON",
                "objective": "Determine the injection vector type.",
                "initial_state": {"risk": 5, "detection": 0, "integrity": 100},
                "hypotheses": [
                    {
                        "id": "theory_error", 
                        "label": "Errors reveal database structure (Error-Based)", 
                        "correct": False,
                        "feedback": "INCORRECT. The WAF is suppressing detailed errors."
                    },
                    {
                        "id": "theory_boolean", 
                        "label": "True/False conditions alter response (Boolean-Blind)", 
                        "correct": True,
                        "feedback": "PLAUSIBLE. Response variance suggests boolean logic."
                    }
                ],
                "actions": [
                    {
                        "id": "fuzz_basic",
                        "label": "Send Probe (' )",
                        "cmd": "curl -d \"user='\"",
                        "description": "Test for syntax errors",
                        "consequence": {"outcome": "500 Error", "side_effect": "No Stack Trace", "stat_change": "Risk +5%"},
                        "simulation_re_run": [{"type": "error", "msg": "HTTP 500: Internal Server Error (No Stack Trace)"}]
                    },
                    {
                        "id": "inject_tautology",
                        "label": "Inject Tautology (' OR 1=1)",
                        "cmd": "payload --boolean",
                        "description": "Force TRUE condition",
                        "locked": True, 
                        "unlock_key": "theory_boolean", 
                        "consequence": {"outcome": "Bypass Successful", "stat_change": "Integrity -50%"},
                        "complete_stage": True,
                        "simulation_re_run": [{"type": "success", "msg": "Condition TRUE. Access Granted."}]
                    }
                ]
            },
            # === PHASE 2: EXPLOIT ===
            {
                "stage_id": "exploit",
                "title": "Phase 2: Weaponization",
                "phase": "EXPLOIT",
                "objective": "Extract data.",
                "actions": [
                    {
                        "id": "dump_db",
                        "label": "Dump Database",
                        "cmd": "sqlmap --dump",
                        "description": "Extract all user data",
                        "complete_stage": True,
                        "simulation_re_run": [{"type": "success", "msg": "Data Exfiltrated."}]
                    }
                ]
            },
            # === PHASE 3: DEFENSE ===
            {
                "stage_id": "defense",
                "title": "Phase 3: Remediation",
                "phase": "DEFENSE",
                "objective": "Close the hole.",
                "actions": [
                    {
                        "id": "patch_code",
                        "label": "Refactor Codebase",
                        "description": "Implement parameterized queries.",
                        "complete_stage": True,
                        "root_cause_fixed": True
                    },
                     {
                        "id": "block_ip",
                        "label": "Block IP",
                        "description": "Firewall rule.",
                        "complete_stage": True,
                        "root_cause_fixed": False
                    }
                ]
            }
        ]
    }
}