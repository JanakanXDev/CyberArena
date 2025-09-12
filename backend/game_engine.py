# game_engine.py
import threading
import time
import random
from attacker_ai import AttackerAI

class CyberGame:
    """
    CyberGame runs a simulated attacker in background and keeps logs/state.
    All actions are simulated text outputs — no real network/host exploitation.
    """

    def __init__(self, stealth="medium"):
        self.attacker = AttackerAI()
        self.logs = []
        self.blocked = False
        self.lock = threading.Lock()
        self.stealth = stealth  # "low", "medium", "high"
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._attacker_loop, daemon=True)
        self._thread.start()

    def _get_interval(self):
        """Determine sleep interval based on stealth level."""
        if self.stealth == "low":
            return random.uniform(0.8, 3.5)
        if self.stealth == "medium":
            return random.uniform(4.5, 11.0)
        return random.uniform(12.0, 28.0)

    def _append_log(self, text):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{ts}] {text}"
        self.logs.append(entry)
        # cap logs to avoid memory growth
        if len(self.logs) > 5000:
            self.logs = self.logs[-2000:]

    def _attacker_loop(self):
        """Background loop performing attacker steps until stopped or blocked."""
        while not self._stop_event.is_set():
            with self.lock:
                if not self.blocked and not self.attacker.success:
                    log = self.attacker.launch_attack()
                    self._append_log(log)
            interval = self._get_interval()
            # jitter
            time.sleep(interval + random.uniform(-0.5, 0.5))

    # compatibility method: manual single step
    def tick(self):
        with self.lock:
            if self.blocked:
                return "Attacker already blocked."
            log = self.attacker.launch_attack()
            self._append_log(log)
            return log

    def set_stealth(self, level: str):
        if level in ("low", "medium", "high"):
            with self.lock:
                self.stealth = level
            return f"Stealth set to {level}"
        return "Invalid stealth level. Use 'low', 'medium', or 'high'."

    def set_mode(self, mode: str):
        ok = self.attacker.set_mode(mode)
        if ok:
            with self.lock:
                self._append_log(f"Scenario changed to '{mode}' (instructor action).")
            return f"Scenario mode set to {mode}"
        return "Invalid mode. Valid: bruteforce, sqli, xss, phishing, portscan."

    def defend(self, command: str):
        """
        Accept simple defense-like commands (simulated):
        - ufw deny from <ip> to any port <port>
        - tail (view logs)
        - set stealth <level>
        - set mode <mode>
        - reset
        """
        command = (command or "").strip()
        cmd_lower = command.lower()

        with self.lock:
            if cmd_lower.startswith("ufw deny") and str(self.attacker.target_port) in cmd_lower:
                self.blocked = True
                self.attacker.stop()
                self._append_log("✅ Firewall rule applied (simulated). Attacker blocked.")
                return "✅ Firewall rule applied. Attacker blocked."

            if cmd_lower == "tail":
                # return last 20 logs
                return "\n".join(self.logs[-20:]) if self.logs else "No logs yet."

            if cmd_lower.startswith("set stealth"):
                parts = cmd_lower.split()
                if len(parts) >= 3:
                    level = parts[2]
                    return self.set_stealth(level)
                return "Usage: set stealth <low|medium|high>"

            if cmd_lower.startswith("set mode"):
                parts = cmd_lower.split()
                if len(parts) >= 3:
                    mode = parts[2]
                    return self.set_mode(mode)
                return "Usage: set mode <bruteforce|sqli|xss|phishing|portscan>"

            if cmd_lower == "reset":
                # resets attacker and scenario
                self.blocked = False
                msg = self.attacker.reset()
                self._append_log("System reset by instructor/user (simulated).")
                return msg

            # if command not recognized
            return "❌ Unrecognized or ineffective command. Try 'tail', 'set stealth <level>', 'set mode <mode>', 'ufw deny ...', or 'reset'."

    def status(self):
        with self.lock:
            return {
                "blocked": self.blocked,
                "success": self.attacker.success,
                "attempts": self.attacker.attempts,
                "stealth": self.stealth,
                "mode": self.attacker.mode,
                "logs_tail": self.logs[-40:],
                "log_count": len(self.logs)
            }

    def stop(self):
        """Graceful stop (call only when shutting down)."""
        self._stop_event.set()
        self._thread.join(timeout=1)
