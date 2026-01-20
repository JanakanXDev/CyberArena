import React, { useState, useEffect, useRef } from 'react';
import { Dashboard } from './Dashboard';
import { TutorialOverlay } from './components/game/TutorialOverlay';
import { GameState } from './types/game';

const API = "http://127.0.0.1:5000";

export const GameSession: React.FC = () => {
  const [state, setState] = useState<GameState | null>(null);
  const [actions, setActions] = useState<string[]>([]);
  const [mentorMessage, setMentorMessage] = useState<{ title: string; msg: string } | null>(null);
  const [started, setStarted] = useState(false);
  const seenEvents = useRef<Set<string>>(new Set());

  // Auto-login and start session on mount
  useEffect(() => {
    const initSession = async () => {
      try {
        // 1. Login
        await fetch(`${API}/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username: "alice" })
        });

        // 2. Start Session (Hardcoded to echo_chamber)
        const startRes = await fetch(`${API}/start`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            curriculum: {
              name: "Operation: Echo Chamber",
              steps: [
                { scenario_id: "echo_chamber", min_score_to_pass: 60 }
              ]
            },
            config: {
              attacker_strategy: "medium",
              max_turns: 20,
              feedback_level: "adaptive"
            }
          })
        });

        const startData = await startRes.json();
        if (startData.status === "session started") {
          setStarted(true);
          await refreshState();
        }
      } catch (err) {
        console.error("Failed to init session:", err);
      }
    };

    initSession();
  }, []);

  // Poll for state or just refresh after actions?
  // The existing backend is synchronous so refresh after action is enough.

  const refreshState = async () => {
    const res = await fetch(`${API}/state`);
    const data: GameState = await res.json();
    setState(data);
    if (data.allowed_actions) {
      setActions(data.allowed_actions);
    }
  };

  // Mentor Logic
  useEffect(() => {
    if (!state) return;

    const lastEvent = state.events[state.events.length - 1];
    if (!lastEvent) return;

    if (seenEvents.current.has(lastEvent.id)) return;
    seenEvents.current.add(lastEvent.id);

    // Logic
    if (lastEvent.title.includes("WAF BLOCKED") || lastEvent.description.includes("WAF BLOCKED")) {
      setMentorMessage({
        title: "OPSEC FAILURE",
        msg: "You triggered the WAF. Aggressive scans are noisy. Analyze the logs to understand WHY it was blocked, then try a stealthier payload."
      });
    } else if (lastEvent.title.includes("Hypothesis Rejected")) {
      setMentorMessage({
         title: "HYPOTHESIS INVALID",
         msg: "Don't guess. Look at the evidence in the logs. What distinguishes a WAF block from a SQL timeout?"
      });
    } else if (state.phase === 'RECON' && state.turn_count === 0 && state.events.length === 0) {
        // Intro
        setMentorMessage({
            title: "MISSION BRIEFING",
            msg: "Welcome to Operation Echo Chamber. We have reports of a data leak. Your goal is to diagnose the vulnerability, exploit it to confirm impact, and patch it. Start by analyzing the logs."
        });
    }

  }, [state]);

  const handleAction = async (action: string) => {
    await fetch(`${API}/action`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action })
    });
    await refreshState();
  };

  return (
    <>
      <Dashboard
        state={state}
        actions={actions}
        onAction={handleAction}
      />
      <TutorialOverlay
        visible={!!mentorMessage}
        title={mentorMessage?.title || ''}
        message={mentorMessage?.msg || ''}
        onClose={() => setMentorMessage(null)}
      />
    </>
  );
};
