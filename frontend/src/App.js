import { useState } from "react";

const API = "http://127.0.0.1:5000";

export default function App() {
  const [user, setUser] = useState(null);
  const [started, setStarted] = useState(false);
  const [state, setState] = useState(null);
  const [result, setResult] = useState(null);

  async function login() {
    const res = await fetch(`${API}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: "alice" })
    });
    const data = await res.json();
    setUser(data);
  }

  async function startSession() {
  const res = await fetch(`${API}/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      curriculum: {
        name: "Web Security Basics",
        steps: [
          { scenario_id: "sql_injection", min_score_to_pass: 60 }
        ]
      },
      config: {
        attacker_strategy: "medium",
        max_turns: 3,
        feedback_level: "adaptive"
      }
    })
  });

  const data = await res.json();

  if (data.status !== "session started") {
    alert("Session failed to start");
    return;
  }

  setStarted(true);
  await refreshState();   // IMPORTANT
}


  async function act(action) {
    await fetch(`${API}/action`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action })
    });
    refreshState();
    refreshResult();
  }

  async function refreshState() {
    const res = await fetch(`${API}/state`);
    setState(await res.json());
  }

  async function refreshResult() {
    const res = await fetch(`${API}/result`);
    setResult(await res.json());
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>CyberArena</h2>

      {!user && <button onClick={login}>Login</button>}

      {user && !started && (
        <button onClick={startSession}>Start Session</button>
      )}

      {started && state && !state.is_secured && !state.is_compromised && (
        <>
          <h3>Actions</h3>
          <button onClick={() => act("scan_inputs")}>Scan Inputs</button>
          <button onClick={() => act("test_payload")}>Test Payload</button>
          <button onClick={() => act("dump_db")}>Dump DB</button>
        </>
      )}


      {state && (
        <>
          <h3>Live State</h3>
          <pre>{JSON.stringify(state, null, 2)}</pre>
        </>
      )}

      {result && (
        <>
          <h3>Result</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </>
      )}
    </div>
  );
}
