# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from game_engine import CyberGame

app = Flask(__name__)
CORS(app)

# single game instance (for demo/prototype). In production, you'd support multiple sessions.
game = CyberGame(stealth="medium")

@app.route("/attack", methods=["GET"])
def attack():
    """Manual single-step attack (keeps compatibility)."""
    result = game.tick()
    return jsonify({"message": result, "status": game.status()})

@app.route("/defend", methods=["POST"])
def defend():
    """
    Accept JSON: { "command": "ufw deny from 192.168.1.50 to any port 22" }
    or { "command": "set stealth high" } etc.
    """
    data = request.get_json(force=True, silent=True) or {}
    command = data.get("command", "")
    result = game.defend(command)
    return jsonify({"message": result, "status": game.status()})

@app.route("/status", methods=["GET"])
def status():
    """Return current game status and recent logs."""
    return jsonify(game.status())

@app.route("/set_stealth", methods=["POST"])
def set_stealth():
    data = request.get_json(force=True, silent=True) or {}
    level = data.get("stealth")
    result = game.set_stealth(level)
    return jsonify({"message": result, "status": game.status()})

@app.route("/set_mode", methods=["POST"])
def set_mode():
    data = request.get_json(force=True, silent=True) or {}
    mode = data.get("mode")
    result = game.set_mode(mode)
    return jsonify({"message": result, "status": game.status()})

@app.route("/reset", methods=["POST"])
def reset():
    result = game.defend("reset")
    return jsonify({"message": result, "status": game.status()})

@app.route("/shutdown", methods=["POST"])
def shutdown():
    """
    Safe shutdown endpoint for local testing only. In production protect this route.
    """
    game.stop()
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
        return jsonify({"message": "Server shutting down."})
    return jsonify({"message": "Shutdown not supported."}), 400

if __name__ == "__main__":
    # NOTE: debug True is OK for development. For production use a proper WSGI server.
    app.run(host="0.0.0.0", port=5000, debug=True)
