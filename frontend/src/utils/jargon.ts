/**
 * Jargon dictionary for CyberArena inline tooltips.
 * Keys are lowercased for matching; values are plain-English definitions.
 */
export const JARGON: Record<string, string> = {
    // Core game mechanics
    'hypothesis': 'A belief you form about how the system works. Test it to find out if you\'re right.',
    'hypotheses': 'Beliefs you form about how the system works. Test each one to confirm or rule out.',
    'validated': 'Confirmed as true. A validated hypothesis unlocks related actions.',
    'invalidated': 'Confirmed as false. The system showed this belief doesn\'t hold.',
    'pressure': 'How stressed the system is. At 100%, you lose — the defender detects you.',
    'stability': 'How intact the system is. High stability = healthy. Low = things breaking.',
    'escalate': 'A high-risk action that moves fast but raises pressure and alerts defenders.',
    'probe': 'A careful, low-noise action that gathers information without triggering alerts.',
    'monitor': 'A passive action that watches for changes without interacting directly.',
    'inspect': 'A targeted action that examines a specific component more closely.',

    // Web security and networking
    'waf': 'Web Application Firewall — a security gate that filters traffic before it reaches the app. Everything that passes through it is "trusted".',
    'web application firewall': 'A security gate that filters malicious traffic before it reaches the web server. Most apps trust input that passes through it.',
    'session': 'The server\'s memory of a specific user. Sessions track who you are across multiple requests.',
    'session state': 'The data the server stores about your current connection — like whether you\'re logged in.',
    'input boundary': 'The limit of what the system considers "valid" input. Crossing it can cause unexpected behavior.',
    'sql injection': 'A technique where attackers insert database commands into input fields to manipulate or read the database.',
    'xss': 'Cross-Site Scripting — injecting malicious scripts into a web page that other users\' browsers will run.',
    'csrf': 'Cross-Site Request Forgery — tricking a logged-in user\'s browser into making unauthorized requests.',
    'payload': 'The actual data or code you\'re sending to try to exploit the system.',
    'endpoint': 'A URL or network address where a service accepts requests. Like a door into the system.',
    'api': 'Application Programming Interface — a defined way for programs to talk to each other, like a menu at a restaurant.',

    // System components
    'web server': 'The component that handles incoming HTTP requests and serves responses. Often the first target.',
    'database': 'Stores persistent data — user records, credentials, application state. High-value target.',
    'waf (component)': 'The firewall layer sitting in front of your web server. It inspects traffic and blocks common attacks.',

    // Attack concepts
    'fuzzing': 'Sending random or unexpected inputs to see how the system reacts — looking for crashes or leaks.',
    'race condition': 'When two operations happen simultaneously in a way that breaks assumptions — like double-spending.',
    'entropy': 'Randomness. High-entropy attacks are unpredictable, making them harder to filter or block.',
    'enumeration': 'Systematically mapping out what exists — users, files, directories — to find attack surfaces.',
    'pivot': 'Using a compromised system as a base to attack other systems that are unreachable directly.',
    'lateral movement': 'Moving from one compromised system to others inside a network to expand access.',
    'privilege escalation': 'Gaining higher-level access (e.g., admin) than you were initially granted.',
    'persistence': 'Leaving a backdoor or mechanism so you can return even after the system is rebooted or patched.',
    'exfiltration': 'Stealing data and smuggling it out of the target environment.',

    // Defense concepts
    'hardened': 'Extra protections applied to a component — it\'s harder for attackers to exploit.',
    'monitoring': 'Active watching of a component for suspicious activity. Increases risk of detection.',
    'detection': 'The process of identifying that an attack is happening. Your enemy in attacker mode.',
    'containment': 'Isolating a compromised component to prevent the attacker from spreading further.',
    'remediation': 'Fixing a vulnerability after it\'s been exploited — patching, resetting, restoring.',
    'false positive': 'An alert that fires for legitimate activity — the system thinks something bad is happening when it isn\'t.',
    'honeypot': 'A decoy system designed to attract attackers and waste their time or expose their techniques.',
    'deception': 'Intentionally misleading the attacker — fake endpoints, fake data, fake signals.',

    // AI / opponent
    'ai opponent': 'The simulated defender or attacker that reacts to your moves in real time.',
    'adaptive': 'The AI changes its behavior based on what you do. Repeating the same move gets punished.',
    'posture': 'The AI\'s current defensive stance — observing, defensive, aggressive, or deceptive.',
    'entropy (ai)': 'How chaotic or unpredictable the AI\'s behavior has become. High entropy = harder to predict.',
};

/** Returns a tooltip definition for a term, case-insensitive. */
export function lookupJargon(term: string): string | undefined {
    return JARGON[term.toLowerCase()];
}

/** All known terms sorted by descending length so longer phrases match first. */
export const JARGON_TERMS = Object.keys(JARGON).sort((a, b) => b.length - a.length);
