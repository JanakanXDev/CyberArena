import traceback
from flask import Flask, jsonify, request
from flask_cors import CORS
import engine

app = Flask(__name__)
# Allow all origins to prevent CORS errors
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/start', methods=['POST'])
def start_game():
    try:
        data = request.json or {}
        mode = data.get('mode', 'guided_simulation')
        difficulty = data.get('difficulty', 'medium')
        scenario_id = data.get('scenarioId', 'input_trust_failures')
        stage_index = data.get('stageIndex', 0)
        experience_mode = data.get('experienceMode', 'advanced')
        
        print(f"Starting simulation: mode={mode}, scenario={scenario_id}, difficulty={difficulty}")
        
        # Reset game logic
        state = engine.reset_game(mode, difficulty, scenario_id, stage_index, experience_mode)
        return jsonify(state)
        
    except Exception as e:
        print("!!! SERVER CRASHED !!!")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/sim/select_focus', methods=['POST'])
def select_focus():
    try:
        data = request.json or {}
        role = data.get('role', 'attacker')
        component = data.get('component', 'web_server')
        
        print(f"Configuring focus: role={role}, component={component}")
        state = engine.configure_session_focus(role, component)
        return jsonify(state)
    except Exception as e:
        print("!!! FOCUS SELECTION CRASHED !!!")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/action', methods=['POST'])
def handle_action():
    try:
        data = request.json
        action_input = data.get('actionId') or data.get('command') or data.get('input')
        print(f"Processing action: {action_input}")
        new_state = engine.process_action(action_input, data)
        return jsonify(new_state)
    except Exception as e:
        print("!!! ACTION CRASHED !!!")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/mentor/toggle', methods=['POST'])
def toggle_mentor():
    try:
        enabled = engine.toggle_mentor()
        return jsonify({"enabled": enabled})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/mentor/analyze', methods=['POST'])
def get_mentor_analysis():
    """Get mentor analysis of current situation"""
    try:
        analysis = engine.get_mentor_analysis()
        return jsonify(analysis)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/learning/data', methods=['GET'])
def get_learning_data():
    try:
        data = engine.get_learning_data()
        return jsonify(data)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/mentor/chat', methods=['POST'])
def mentor_chat():
    """Chat with the AI mentor using Ollama, with full simulation context."""
    try:
        data = request.json or {}
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Gather current simulation state for context
        sim_context = ""
        if engine.current_engine:
            state = engine.current_engine.state
            hypotheses = engine.current_engine.hypotheses
            hyp_lines = []
            for h in hypotheses:
                status = "✓ Validated" if h.validated else ("✗ Invalidated" if h.tested else "Untested")
                hyp_lines.append(f"  - {h.label} [{status}]")
            
            config_hyps = engine.current_engine._hypotheses_config
            untested_lines = [f"  - {hd.get('label', h_id)}" for h_id, hd in config_hyps.items()
                              if not any(h.id == h_id for h in hypotheses)]
            
            all_actions = engine.current_engine._get_state_dict().get("available_actions", [])
            action_lines = [f"  - {a.get('label', '')} [{a.get('type','')}]" for a in all_actions if a.get('available')]
            
            sim_context = f"""
CURRENT SIMULATION STATE:
- Mode: {engine.current_engine.mode.value if engine.current_engine.mode else 'unknown'}
- Turn: {engine.current_engine.turn_count}
- Pressure: {state.pressure}% (higher = more AI detection risk)
- Stability: {state.stability}% (lower = system degrading)
- AI Posture: {state.ai_visual_state.posture} / Distance: {state.ai_visual_state.distance}
- Scenario State: {state.scenario_state}

HYPOTHESES TESTED:
{chr(10).join(hyp_lines) if hyp_lines else "  None tested yet"}

HYPOTHESES AVAILABLE TO TEST:
{chr(10).join(untested_lines) if untested_lines else "  All tested"}

ACTIONS CURRENTLY AVAILABLE:
{chr(10).join(action_lines) if action_lines else "  None (scenario may have ended)"}
"""
        
        # Build Ollama prompt
        system_prompt = """You are the Mentor AI inside CyberArena, a cybersecurity learning simulator. 
Your job is to guide a COMPLETE BEGINNER who has NO cybersecurity experience.
You must NEVER be condescending. Speak like a patient, encouraging teacher.

Rules:
- Explain concepts in simple English. No jargon without explanation.
- When the learner asks what to do next, give a CONCRETE, SPECIFIC suggestion (e.g., "Click the hypothesis that says '...' to test it first").
- When explaining WHY something happened, connect it to real-world cybersecurity concepts simply.
- Keep responses SHORT (3-5 sentences max). Be direct and actionable.
- If they seem lost, reassure them and give ONE clear next step.
- Hypotheses are beliefs/guesses about how the system works. Testing them produces evidence.
- Actions are experiments to gather more information or apply pressure.
"""
        
        full_prompt = f"""{system_prompt}

{sim_context}

The learner asks: {user_message}

Reply as the Mentor:"""
        
        # Call Ollama
        import requests as req
        try:
            response = req.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3:8b", "prompt": full_prompt, "stream": False},
                timeout=30
            )
            if response.status_code == 200:
                reply = response.json().get("response", "").strip()
            else:
                # Fallback if Ollama is down
                reply = _fallback_mentor_response(user_message, engine.current_engine)
        except Exception:
            reply = _fallback_mentor_response(user_message, engine.current_engine)
        
        return jsonify({"reply": reply})
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"reply": _fallback_mentor_response("help", engine.current_engine)})


def _fallback_mentor_response(message: str, eng) -> str:
    """Fallback mentor response when Ollama is unavailable."""
    msg = message.lower()
    mode = eng.mode.value if eng and eng.mode else ''

    # How many clicks / enough?
    if any(w in msg for w in ["enough", "how many", "how much", "times", "how often", "repeat"]):
        return ("One click is always enough. Actions in CyberArena execute completely in a single click — "
                "there's no accumulation or grind. After clicking an action, your next step is to test the "
                "related hypothesis in the panel above to confirm what the action revealed.")

    # Audit / evidence specific
    if any(w in msg for w in ["audit", "scheduled", "cron", "evidence", "collect", "gather"]):
        return ("You only need to click 'Audit Scheduled Jobs' once. That executes a full scan. "
                "After clicking it, look at the Hypotheses panel above and click the hypothesis "
                "'Attacker is using scheduled tasks for return' to test whether your audit confirmed it. "
                "The hypothesis result will tell you exactly what was found.")

    # What to do next
    if any(w in msg for w in ["what", "next", "do", "move", "help", "lost", "stuck"]):
        if eng and eng.hypotheses:
            untested = [h for h in eng.hypotheses if not h.tested]
            if untested:
                return (f"Your next step: click the hypothesis '{untested[0].label}' in the top panel. "
                        f"This tests whether your belief about the system is true. "
                        f"You only need to click it once — the result will appear immediately.")
        if mode == 'defender_campaign':
            return ("In Defender mode, the loop is: 1) Click an action once to gather evidence. "
                    "2) Test the related hypothesis above to confirm what you found. "
                    "3) Execute a response action based on what was confirmed. Don't repeat actions — each one completes fully.")
        return ("Start by testing one of the hypotheses in the top panel. Click it once — "
                "the system will immediately tell you if your belief holds true.")

    # Hypothesis questions
    if any(w in msg for w in ["hypothesis", "hyp", "belief", "test"]):
        return ("A hypothesis is your belief about what's happening. Click it once to test it. "
                "The system immediately evaluates if you're right and shows you exactly why. "
                "Correct hypotheses unlock new actions.")

    # Action questions
    if any(w in msg for w in ["action", "button", "click", "execute"]):
        return ("Each action executes completely with one click — no need to repeat. "
                "Action types tell you the risk: 'inspect' = safe and slow, "
                "'escalate' = fast but raises pressure, 'isolate' = cuts access (use carefully).")

    # Win condition
    if any(w in msg for w in ["win", "victory", "complete", "finish"]):
        if mode == 'defender_campaign':
            return ("To win in Defender mode: validate the TRUE hypotheses (persistence method is real), "
                    "then take the correct response actions. Avoid the trap actions tied to false hypotheses.")
        return ("To win: test and validate the correct hypotheses. The system triggers Mission Victory "
                "automatically when you've confirmed the right beliefs.")

    # Lose condition
    if any(w in msg for w in ["lose", "defeat", "fail", "pressure"]):
        return ("You lose if pressure hits 100%. Risky actions like 'escalate' push it up fast. "
                "In Defender mode, stability dropping to 0% also loses — so avoid trap actions.")

    return ("I'm your guide in CyberArena. Try asking: 'What should I do next?' or "
            "'How many times do I need to click?' and I'll give you a specific answer.")



if __name__ == '__main__':
    print("CyberArena Server running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)