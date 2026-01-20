# CyberArena 2.0

AI-Powered Ethical Hacking Learning Platform (PvP-style simulator for cybersecurity education).

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+ & npm

### Installation

1.  **Backend Setup**
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

2.  **Frontend Setup**
    ```bash
    cd frontend
    npm install
    ```

## 🎮 How to Play

### 1. Start the Backend
Open a terminal and run:
```bash
cd backend
python -m app
```
The API will run on `http://127.0.0.1:5000`.

### 2. Start the Frontend
Open a **new** terminal and run:
```bash
cd frontend
npm start
```
The application will open at `http://localhost:3000`.

### 3. "Operation: Echo Chamber" Walkthrough
Once the Command Center loads:

1.  **Phase: RECON**
    *   Click **[DIAGNOSIS] Analyze Application Logs**.
    *   *Observation:* Note the "5000ms delay" in logs.
    *   **Do NOT** click "Check WAF Status" (It's a trap/distraction).
    *   After analyzing, a new hypothesis unlocks.
    *   Click **[HYPOTHESIS] Hypothesis: Blind SQL Injection**.

2.  **Phase: ATTACK**
    *   Click **[EXPLOITATION] Execute "Low & Slow" Extraction**.
    *   *Note:* "Aggressive Dump" will trigger the WAF and fail the mission.

3.  **Phase: DEFENSE**
    *   Click **[REMEDIATION] Implement Prepared Statements**.
    *   *Note:* "WAF Blocking Rule" is a temporary fix and not the root cause.

## 🧪 Testing
To verify the setup without running the UI:
```bash
# Verify backend logic
python3 -m backend.app
# (In another terminal) curl -X GET http://127.0.0.1:5000/state
```
