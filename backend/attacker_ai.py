# attacker_ai.py
import random
import time

class AttackerAI:
    """
    Simulated attacker. Does NOT perform real attacks.
    It simulates steps and writes human-readable log messages describing actions.
    """

    def __init__(self):
        self.active = True
        self.attempts = 0
        self.success = False
        self.target_port = 22
        self.mode = "bruteforce"  # default scenario
        # small password list for simulation only
        self.password_list = ["12345", "qwerty", "password", "letmein", "admin", "root123"]
        # small dictionary of SQLi-like payload fragments for simulation (non-executable)
        self.sqli_fragments = ["' OR '1'='1", "'; --", "' OR 'a'='a"]
        # small XSS-like fragment examples (shown as strings only)
        self.xss_fragments = ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>"]
        # phishing templates (will be combined with context)
        self.phish_templates = [
            "Urgent: Please verify your account at {url} immediately to avoid suspension.",
            "Payroll issue: confirm bank details here {url} so we can process your salary.",
            "Action required: You have a file waiting at {url}. Please review."
        ]
        self.scenario_context = {
            "company": "AcmeCorp",
            "service": "Employee Portal",
            "url": "http://example.local/verify"  # placeholder; not a real external target
        }

    def set_mode(self, mode: str):
        """Set scenario mode: bruteforce, sqli, xss, phishing, portscan"""
        allowed = ("bruteforce", "sqli", "xss", "phishing", "portscan")
        if mode in allowed:
            self.mode = mode
            return True
        return False

    def launch_attack(self):
        """Return a descriptive log line describing one attacker action."""
        if not self.active or self.success:
            return "Attacker is idle."

        self.attempts += 1

        if self.mode == "bruteforce":
            pw = random.choice(self.password_list)
            # small chance of simulated success
            if random.random() < 0.05:
                self.success = True
                return f"Attacker SUCCESS: simulated login using password '{pw}' (simulated)."
            return f"Attacker tried login with password '{pw}' (simulated attempt)."

        if self.mode == "sqli":
            payload = random.choice(self.sqli_fragments)
            # simulated detection probability
            if random.random() < 0.04:
                self.success = True
                return f"Attacker SUCCESS: simulated SQL injection payload '{payload}' appeared to bypass filters (simulated)."
            return f"Attacker attempted SQLi-like payload '{payload}' against /login (simulated)."

        if self.mode == "xss":
            payload = random.choice(self.xss_fragments)
            if random.random() < 0.03:
                self.success = True
                return f"Attacker SUCCESS: simulated XSS payload '{payload}' executed in simulated context."
            return f"Attacker injected XSS-like string '{payload}' into a form field (simulated)."

        if self.mode == "phishing":
            tpl = random.choice(self.phish_templates)
            msg = tpl.format(url=self.scenario_context.get("url", "http://example.local/"))
            # phishing success simulated very rarely
            if random.random() < 0.02:
                self.success = True
                return f"Attacker SUCCESS: a simulated recipient clicked a malicious link. Email: \"{msg}\""
            return f"Attacker sent phishing email: \"{msg}\" (simulated)."

        if self.mode == "portscan":
            port = random.choice([22, 80, 443, 3306, 8080])
            return f"Attacker probed port {port} (simulated)."

        # fallback
        return "Attacker performed an unknown simulated action."

    def stop(self):
        self.active = False
        return "Attacker stopped (simulated)."

    def reset(self):
        self.active = True
        self.attempts = 0
        self.success = False
        self.mode = "bruteforce"
        return "Attacker reset (simulated)."
