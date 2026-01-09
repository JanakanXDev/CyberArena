from backend.scenarios.sql_injection import SQLInjectionScenario


SCENARIO_REGISTRY = {
    "sql_injection": SQLInjectionScenario,
    # future:
    # "xss": XSSScenario,
    # "phishing": PhishingScenario,
}
