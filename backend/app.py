from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.models.curriculum import Curriculum, CurriculumStep
from backend.services.session_service import SessionService
from backend.services.auth_service import AuthService
from backend.services.orchestrator import Orchestrator
active_orchestrator = None
active_user = None

app = Flask(__name__)
CORS(app)


@app.route("/login", methods=["POST"])
def login():
    global active_user
    username = request.json["username"]
    active_user = AuthService.authenticate(username)
    return jsonify({"status": "logged_in", "role": active_user.role.name})


@app.route("/start", methods=["POST"])
def start():
    global active_orchestrator, active_user

    if not active_user:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json

    # 1️⃣ Extract curriculum JSON
    curriculum_data = data["curriculum"]

    # 2️⃣ Convert steps (JSON → domain objects)
    steps = [
        CurriculumStep(**step)
        for step in curriculum_data["steps"]
    ]

    curriculum = Curriculum(
        name=curriculum_data["name"],
        steps=steps
    )

    # 3️⃣ Extract base config
    base_config = data["config"]

    # 4️⃣ Create orchestrator
    active_orchestrator = Orchestrator(
        user=active_user,
        curriculum=curriculum,
        base_config=base_config
    )

    active_orchestrator.start()

    return jsonify({"status": "session started"})
@app.route("/action", methods=["POST"])
def action():
    if not active_orchestrator:
        return jsonify({"error": "Session not started"}), 400

    data = request.json

    try:
        active_orchestrator.apply_action(data["action"])
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"status": "action applied"})

@app.route("/state", methods=["GET"])
def state():
    if not active_orchestrator:
        return jsonify({"error": "Session not started"}), 400

    return jsonify(active_orchestrator.get_state().to_dict())



@app.route("/result", methods=["GET"])
def result():
    if not active_orchestrator:
        return jsonify({"error": "Session not started"}), 400

    return jsonify(active_orchestrator.get_result())

if __name__ == "__main__":
    app.run(debug=True)
