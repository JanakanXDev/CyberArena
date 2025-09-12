CyberArena backend (Flask) - simulated attacker prototype

Requirements:
- Python 3.9+ recommended
- install dependencies:
    pip install -r requirements.txt

Files:
- app.py         : Flask server
- game_engine.py : Game logic + attacker scheduler
- attacker_ai.py : Simulated attacker behaviors

Run locally:
    python app.py

API:
- GET  /status               -> returns game status and recent logs
- GET  /attack               -> manual single attack step
- POST /defend               -> JSON {"command": "..."} to send defense commands (tail, ufw deny ..., set stealth ..., set mode ..., reset)
- POST /set_stealth          -> JSON {"stealth":"low"|"medium"|"high"}
- POST /set_mode             -> JSON {"mode":"bruteforce"|"sqli"|"xss"|"phishing"|"portscan"}
- POST /reset                -> resets attacker/scenario
- POST /shutdown             -> shuts down server (local dev only)

Important:
- All attacker actions are simulated text logs. No real exploitation or network attacks are performed.
- Keep this server on an isolated machine or local dev environment for safety/testing.
