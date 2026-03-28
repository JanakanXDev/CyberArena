import type { ExperienceMode } from '../types/game';

export const LOCK_REASON = '🔒 Locked: Requires validated hypothesis';

export const CURRENT_OBJECTIVE: Record<ExperienceMode, string> = {
  beginner: 'Objective: Understand system behavior and form a hypothesis.',
  intermediate: 'Objective: Analyze system signals and form a hypothesis.',
  advanced: 'Objective: Form a hypothesis based on observed behavior.',
};

/** Beginner Module 1 (observation-only path). */
export const OBSERVATION_ONLY_OBJECTIVE =
  'Objective: Observe system responses → read State Signals → identify what changed → understand before concluding.';

/** Maps identification action id → system_conditions key (keep in sync with backend). */
export const IDENTIFY_ACTION_TO_SIGNAL: Record<string, string> = {
  act_beginner_identify_timing: 'timing_jitter',
  act_beginner_identify_validation: 'validation_tightened',
  act_beginner_identify_access: 'access_restricted',
  act_beginner_identify_routing: 'route_shifted',
  act_beginner_identify_errors: 'errors_suppressed',
  act_beginner_identify_deception: 'deception_active',
};

const BEGINNER_SUGGESTIONS_BY_SIGNAL: Record<string, string[]> = {
  validation_tightened: ['Input validation is active', 'Requests are being filtered'],
  timing_jitter: ['Timing behavior is inconsistent'],
  access_restricted: ['Access to some operations is restricted'],
  route_shifted: ['Service routes or endpoints have shifted'],
  errors_suppressed: ['Error detail is suppressed or generic'],
  deception_active: ['Deceptive or bait responses may be present'],
};

/** Context-aware hypothesis chips for beginner (non–module-1) modes. */
export function beginnerSuggestionsForSignals(activeKeys: string[]): string[] {
  const out: string[] = [];
  const seen = new Set<string>();
  for (const k of activeKeys) {
    for (const s of BEGINNER_SUGGESTIONS_BY_SIGNAL[k] || []) {
      if (!seen.has(s)) {
        seen.add(s);
        out.push(s);
      }
    }
  }
  return out;
}

/** System signal keys match backend system_conditions */
export const SIGNAL_GUIDANCE: Record<
  string,
  { label: string; short: string; meaning: string }
> = {
  errors_suppressed: {
    label: 'Error detail suppressed',
    short: 'The system is hiding detailed errors from responses.',
    meaning:
      'Defenses often hide stack traces or internals so attackers learn less. Use other signals (timing, behavior changes) to infer what changed.',
  },
  timing_jitter: {
    label: 'Timing jitter introduced',
    short: 'Responses may arrive with inconsistent delays.',
    meaning:
      'Jitter is a common anti-recon technique: it makes timing-based fingerprinting harder. Note it when comparing probe results.',
  },
  route_shifted: {
    label: 'Service routes shifted',
    short: 'Traffic may be taking different paths than before.',
    meaning:
      'Routing changes can mean load balancing, failover, or deliberate redirection. Your next action should account for a moving target.',
  },
  validation_tightened: {
    label: 'Input normalization tightened',
    short: 'Stricter filtering or sanitization is active.',
    meaning:
      'Tighter validation often follows suspicious input. It explains why payloads that worked earlier may start failing.',
  },
  access_restricted: {
    label: 'Access scope restricted',
    short: 'Fewer operations or endpoints are reachable.',
    meaning:
      'Restricted access usually raises pressure on alternate paths. Watch which actions remain available.',
  },
  deception_active: {
    label: 'Deceptive responses active',
    short: 'Some responses may be misleading by design.',
    meaning:
      'Deception is a signal to distrust surface-level success; cross-check with logs, metrics, and follow-up actions.',
  },
};

type ActionHistoryEntry = {
  action_id: string;
  action_label?: string;
  action_type?: string;
};

function baseFacts(ev: ActionHistoryEntry): { type: string; label: string } {
  const type = (ev.action_type || 'action').toLowerCase();
  const label = ev.action_label || ev.action_id || 'Unknown action';
  return { type, label };
}

/** Mode-based evidence copy; does not change game data. */
export function interpretEvidence(
  ev: ActionHistoryEntry,
  mode: ExperienceMode
): string {
  if (ev.action_id?.startsWith('hypothesis_text')) {
    if (mode === 'advanced') {
      return 'Observed: Hypothesis submitted for validation';
    }
    if (mode === 'beginner') {
      return 'You submitted a hypothesis. The simulation checks it against behavior; a good match unlocks deeper actions.';
    }
    return 'Hypothesis submitted; validation determines which follow-up actions unlock.';
  }

  const { type, label } = baseFacts(ev);

  if (mode === 'advanced') {
    return `Observed: ${label} (${type})`;
  }

  let what = `You ran “${label}”.`;
  let why = '';

  if (type.includes('inspect') || type.includes('probe')) {
    what = `You probed or inspected (“${label}”), gathering observable behavior.`;
    why =
      mode === 'beginner'
        ? ' The system often reacts to recon by tightening defenses or changing responses—that is normal.'
        : ' Defenses may respond to recon.';
  } else if (type.includes('escalate') || type.includes('pivot')) {
    what = `You escalated (“${label}”), increasing pressure on the system.`;
    why =
      mode === 'beginner'
        ? ' Stronger moves can trigger defensive countermeasures and higher detection pressure.'
        : ' Higher-risk actions tend to trigger stronger system reactions.';
  } else if (type.includes('monitor')) {
    what = `You monitored (“${label}”), watching passive signals.`;
    why =
      mode === 'beginner'
        ? ' Monitoring helps correlate logs and metrics without immediately provoking the opponent.'
        : ' Passive observation reduces immediate pushback while you interpret signals.';
  } else if (type.includes('isolate') || type.includes('restrict')) {
    what = `You applied containment (“${label}”), narrowing what the system can do.`;
    why =
      mode === 'beginner'
        ? ' Containment changes attack surface and can shift the adversary’s options.'
        : ' Containment reshapes available paths for both you and the opponent.';
  } else {
    why =
      mode === 'beginner'
        ? ' Each action updates what the simulation exposes next—tie it to a hypothesis.'
        : ' Outcomes should inform your next hypothesis.';
  }

  if (mode === 'beginner') {
    return `${what} ${why}`.trim();
  }
  return `${what} ${why}`.trim();
}

export const INTERMEDIATE_HYPOTHESIS_CATEGORIES: Array<{
  id: string;
  prefix: string;
  hint: string;
}> = [
  {
    id: 'timing',
    prefix: 'Timing or latency behavior: ',
    hint: 'Response timing, delays, jitter',
  },
  {
    id: 'validation',
    prefix: 'Input handling or validation: ',
    hint: 'Filtering, blocking, normalization',
  },
  {
    id: 'rate',
    prefix: 'Request rate or throttling: ',
    hint: 'Frequency limits, bursts vs steady traffic',
  },
  {
    id: 'session',
    prefix: 'Session or authentication state: ',
    hint: 'Login flow, tokens, retries',
  },
];
