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
        
        print(f"Starting simulation: mode={mode}, scenario={scenario_id}, difficulty={difficulty}")
        
        # Reset game logic
        state = engine.reset_game(mode, difficulty, scenario_id, stage_index)
        return jsonify(state)
        
    except Exception as e:
        print("!!! SERVER CRASHED !!!")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/action', methods=['POST'])
def handle_action():
    try:
        data = request.json
        action_input = data.get('actionId') or data.get('command') or data.get('input')
        print(f"Processing action: {action_input}")
        new_state = engine.process_action(action_input)
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

if __name__ == '__main__':
    print("CyberArena Server running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)