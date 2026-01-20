from backend.scenarios.sql_injection import SQLInjectionScenario
from backend.scenarios.echo_chamber import EchoChamberScenario


SCENARIO_REGISTRY = {
    "sql_injection": SQLInjectionScenario,
    "echo_chamber": EchoChamberScenario,
    # future:
    # "xss": XSSScenario,
    # "phishing": PhishingScenario,
}
