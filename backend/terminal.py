# backend/terminal.py

DEFAULT_FS = {
    "files": ["todo.txt", "instructions.txt"],
    "content": {
        "todo.txt": "1. Scan network\n2. Get coffee",
        "instructions.txt": "Follow the Cyber Kill Chain: Recon -> Enum -> Exploit."
    }
}

class TerminalEngine:
    def __init__(self):
        self.current_dir = "/home/hacker"

    def parse_command(self, user_input, scenario):
        cmd = user_input.strip()
        parts = cmd.split()
        if not parts: return "No command entered."
        
        base = parts[0].lower()
        args = parts[1:]

        # 1. SYSTEM COMMANDS (Always available)
        if base == "ls":
            fs = scenario.get("file_system", DEFAULT_FS)
            return "  ".join(fs.get("files", []))
        
        elif base == "cat":
            if not args: return "Usage: cat <filename>"
            fs = scenario.get("file_system", DEFAULT_FS)
            return fs.get("content", {}).get(args[0], f"cat: {args[0]}: No such file or directory")
        
        elif base == "whoami":
            return "root" if "privesc" in scenario["id"] else "kali"
        
        elif base == "pwd":
            return self.current_dir
        
        elif base == "help":
            return "Available tools: nmap, gobuster, sqlmap, hydra, nc, ssh, ping, ls, cat..."
        
        elif base == "clear":
            return "CLEAR_LOGS" # This string is caught by engine.py to clear the log array

        # 2. HACKER TOOLS (Sandbox Simulation)
        # We check if "sandbox" is IN the ID (handles sandbox_corp, sandbox_bank, etc.)
        if "sandbox" in scenario["id"]:
            return self._handle_sandbox(base, args)

        # 3. LESSON OBJECTIVE VALIDATION
        return self._check_objective(base, cmd, scenario)

    def _handle_sandbox(self, tool, args):
        """Simulates tool output for open-world mode"""
        if tool == "nmap": 
            return "Starting Nmap 7.92... \nPORT   STATE SERVICE\n21/tcp open  ftp\n22/tcp open  ssh\n80/tcp open  http"
        
        if tool == "ping": 
            target = args[0] if args else "target"
            return f"PING {target} (127.0.0.1): 56 data bytes\n64 bytes from 127.0.0.1: icmp_seq=0 ttl=64 time=0.1 ms"
        
        if tool == "sqlmap": 
            return "[*] testing connection... done\n[+] heuristics detected: SQL injection\n[+] dumped table 'users': admin, user1"
        
        if tool == "hydra": 
            return "[DATA] attacking target ftp://10.10.10.5\n[STATUS] 16.00 tries/min\n[DATA] login: admin   password: password123"
        
        if tool == "gobuster":
            return "/images (Status: 301)\n/assets (Status: 301)\n/admin (Status: 200)\n/login.php (Status: 200)"
            
        return f"{tool}: command executed. (Sandbox Simulation Mode)"

    def _check_objective(self, tool, full_cmd, scenario):
        """Checks if the command matches the current lesson's required action"""
        
        # Look through all defined actions for this specific scenario
        for action in scenario.get("actions", []):
            # We look for the main command match. 
            # In a pro version, we'd regex the flags, but for now we check startsWith
            required_cmd = action["cmd"]
            
            # Simple check: Does the user's command start with the tool required?
            # And does it contain key flags if specified?
            required_parts = required_cmd.split()
            tool_name = required_parts[0]

            if full_cmd.startswith(tool_name):
                # If it's the right tool, we assume success for this demo level.
                # (You can add stricter checking here later if needed)
                return {
                    "success": True, 
                    "unlocks": action["unlocks"], 
                    "msg": f"Command Successful: {full_cmd}",
                    "visual": action.get("visual")
                }
        
        # If no match found
        return f"{tool}: Command executed, but it didn't match the current mission objective.\nTry checking the briefing."

# Singleton instance to be imported by engine.py
terminal = TerminalEngine()