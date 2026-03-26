import asyncio
from engine import SimulationEngine
from simulation_engine import LearningMode
import traceback

async def test():
    try:
        print("Initializing Engine...")
        engine = SimulationEngine(mode=LearningMode.GUIDED_SIMULATION, scenario_id="level_0_tutorial", difficulty="medium")
        print("Engine Initialized")

        print("Testing Action...")
        res = engine.process_action("act_gather_evidence")
        print("Action Processed")

        print("Testing Hypothesis...")
        res = engine.process_action("hypothesis:hyp_tutorial")
        print("Hypothesis Processed")
        print("SUCCESS")
    except Exception as e:
        print("RUNTIME ERROR:")
        traceback.print_exc()

asyncio.run(test())
