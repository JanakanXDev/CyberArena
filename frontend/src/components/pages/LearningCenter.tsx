
import React, { useState } from 'react';
import {
  BookOpen,
  Brain,
  Shield,
  Terminal,
  Server,
  ArrowRight,
  Play
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

type ModeId =
  | 'guided_simulation'
  | 'attacker_campaign'
  | 'defender_campaign'
  | 'playground'
  | 'incident_response'
  | 'red_vs_blue'
  | 'forensics'
  | 'chaos';

type TierName = 'Recruit' | 'Veteran' | 'Elite';

type Mode = {
  id: ModeId;
  title: string;
  purpose: string;
  behavior: string[];
  aiStance: string;
  icon: React.ReactNode;
};

type Track = {
  id: string;
  title: string;
  focus: string;
  cognitiveShift: string;
  tiers: Array<{
    name: TierName;
    aiAggression: string;
    deception: string;
    complexity: string;
  }>;
  supportedModes: ModeId[];
};

type ScenarioPack = {
  id: string;
  title: string;
  trackId: string;
  summary: string;
  pressureSignals: string[];
  failureEcho: string;
  supportedModes: ModeId[];
  recommendedTier: TierName;
  icon: React.ReactNode;
};

const modes: Mode[] = [
  {
    id: 'guided_simulation',
    title: 'Guided Simulation Mode',
    purpose: 'Foundational mental models under quiet resistance.',
    behavior: [
      'One continuous simulation with hidden phases',
      'At least one misleading success that fails later',
      'Subtle AI resistance and hypothesis invalidation',
      'Focus on correcting broken mental models'
    ],
    aiStance: 'Subtle instructor; pressure rises when you repeat assumptions.',
    icon: <Brain className="w-6 h-6 text-emerald-400" />
  },
  {
    id: 'attacker_campaign',
    title: 'Attacker Campaign',
    purpose: 'You are the attacker; the AI is a living defender.',
    behavior: [
      'AI monitors, patches, blocks, rate-limits, deploys deception',
      'Repeated strategies are punished',
      'Stealth and timing matter more than speed'
    ],
    aiStance: 'Hostile adaptive defender; punishes brute force and scripts.',
    icon: <Terminal className="w-6 h-6 text-red-400" />
  },
  {
    id: 'defender_campaign',
    title: 'Defender Campaign',
    purpose: 'You defend; the AI attacker probes, escalates, and persists.',
    behavior: [
      'AI probes, retreats, and returns in new forms',
      'False victories are common',
      'Persistent stealthy behavior across sessions'
    ],
    aiStance: 'Patient attacker; adapts to your countermeasures.',
    icon: <Shield className="w-6 h-6 text-blue-400" />
  },
  {
    id: 'playground',
    title: 'Playground Mode',
    purpose: 'Mastery and experimentation without objectives.',
    behavior: [
      'No objectives and no fail screen',
      'Multiple weaknesses active at once',
      'Optional brutal AI opponent',
      'Recovery is part of learning'
    ],
    aiStance: 'Brutal if enabled; pressure never fully resets.',
    icon: <Server className="w-6 h-6 text-amber-400" />
  },
  {
    id: 'incident_response',
    title: 'Incident Response Mode',
    purpose: 'Crisis decision-making after a breach.',
    behavior: [
      'Systems unstable and partially broken',
      'Logs are incomplete or misleading',
      'AI attacker still active in the environment',
      'Containment, recovery, and reinfection prevention are all required'
    ],
    aiStance: 'Active adversary hiding in the noise and recovery work.',
    icon: <Shield className="w-6 h-6 text-orange-400" />
  },
  {
    id: 'red_vs_blue',
    title: 'Red vs Blue War Mode',
    purpose: 'Play the same environment twice with memory and adaptation.',
    behavior: [
      'First as attacker, then as defender',
      'AI remembers your previous strategy',
      'The environment adapts to your prior choices'
    ],
    aiStance: 'Remembers you; repeats are punished, reversals are rewarded.',
    icon: <Terminal className="w-6 h-6 text-fuchsia-400" />
  },
  {
    id: 'forensics',
    title: 'Forensics Mode',
    purpose: 'Reconstruct what happened from artifacts only.',
    behavior: [
      'Attack is already finished',
      'Only artifacts remain',
      'AI attempts to mislead analysis',
      'Evidence-based reconstruction is required'
    ],
    aiStance: 'Cold and deceptive; rewards cautious inference.',
    icon: <BookOpen className="w-6 h-6 text-slate-300" />
  },
  {
    id: 'chaos',
    title: 'Chaos Mode',
    purpose: 'Resilience under cascading failures.',
    behavior: [
      'Multiple failures happen simultaneously',
      'AI changes topology mid-run',
      'Services crash and monitoring fails',
      'Recovery under pressure is the core challenge'
    ],
    aiStance: 'Brutal adversary; pressure spikes without warning.',
    icon: <Server className="w-6 h-6 text-rose-400" />
  }
];

const webSecurityTrack: Track = {
  id: 'web_security',
  title: 'Web Security',
  focus: 'Input trust, logic abuse, session state, client deception.',
  cognitiveShift: 'Stop trusting what the client shows you.',
  tiers: [
    {
      name: 'Recruit',
      aiAggression: 'Reactive but constrained by simple rules.',
      deception: 'Light misdirection and delayed errors.',
      complexity: 'Single service, narrow request paths.'
    },
    {
      name: 'Veteran',
      aiAggression: 'Proactive responses and adaptive rate shaping.',
      deception: 'Multi-layered false signals and staged failures.',
      complexity: 'Multiple endpoints and cross-service state.'
    },
    {
      name: 'Elite',
      aiAggression: 'Predictive counterplay and dynamic defenses.',
      deception: 'High-fidelity decoys with convincing artifacts.',
      complexity: 'Distributed session state and shifting routes.'
    }
  ],
  supportedModes: ['guided_simulation', 'attacker_campaign', 'defender_campaign', 'playground', 'red_vs_blue']
};

const osPrivilegeTrack: Track = {
  id: 'os_privilege',
  title: 'OS & Privilege Escalation',
  focus: 'Linux and Windows permission boundaries and trust surfaces.',
  cognitiveShift: 'Assume the system resists privilege gains.',
  tiers: [
    {
      name: 'Recruit',
      aiAggression: 'Predictable guardrails and limited counteraction.',
      deception: 'Sparse false artifacts.',
      complexity: 'Single host with basic process boundaries.'
    },
    {
      name: 'Veteran',
      aiAggression: 'Adaptive containment and permission reshaping.',
      deception: 'Misleading process trails and log gaps.',
      complexity: 'Multiple users, services, and trust anchors.'
    },
    {
      name: 'Elite',
      aiAggression: 'Counter-elevation traps and live hardening.',
      deception: 'Plausible phantom processes and shadow accounts.',
      complexity: 'Cross-host boundary shifts and transient permissions.'
    }
  ],
  supportedModes: [
    'guided_simulation',
    'attacker_campaign',
    'defender_campaign',
    'playground',
    'incident_response',
    'red_vs_blue'
  ]
};

const persistenceCleanupTrack: Track = {
  id: 'persistence_cleanup',
  title: 'Persistence & Cleanup',
  focus: 'Durable footholds, trace handling, and recurrence.',
  cognitiveShift: 'Assume the opponent will return in a new shape.',
  tiers: [
    {
      name: 'Recruit',
      aiAggression: 'Basic recurrence and shallow persistence.',
      deception: 'Small traces that hint at survival paths.',
      complexity: 'Single persistence vector per run.'
    },
    {
      name: 'Veteran',
      aiAggression: 'Multi-step recurrence and staged recovery.',
      deception: 'Layered traces with decoy remnants.',
      complexity: 'Multiple footholds across services.'
    },
    {
      name: 'Elite',
      aiAggression: 'Persistent reentry across restarts.',
      deception: 'Convincing false trails and cross-host echoes.',
      complexity: 'Distributed footholds with timing offsets.'
    }
  ],
  supportedModes: ['attacker_campaign', 'defender_campaign', 'incident_response', 'forensics', 'chaos']
};

const networkIntrusionTrack: Track = {
  id: 'network_intrusion',
  title: 'Network Intrusion & Lateral Movement',
  focus: 'Trust boundaries, traversal, and signal discipline.',
  cognitiveShift: 'Every move changes the map.',
  tiers: [
    {
      name: 'Recruit',
      aiAggression: 'Detects blunt movement but slow to respond.',
      deception: 'Simple decoy routes.',
      complexity: 'Flat network with obvious choke points.'
    },
    {
      name: 'Veteran',
      aiAggression: 'Rapid containment and adaptive segmentation.',
      deception: 'Decoy nodes with believable traffic.',
      complexity: 'Layered network with moving boundaries.'
    },
    {
      name: 'Elite',
      aiAggression: 'Topology shifts mid-run and aggressive isolation.',
      deception: 'Dynamic decoys and looping routes.',
      complexity: 'Multi-tenant, segmented, and unstable topology.'
    }
  ],
  supportedModes: [
    'attacker_campaign',
    'defender_campaign',
    'playground',
    'incident_response',
    'red_vs_blue',
    'chaos'
  ]
};

const detectionEvasionTrack: Track = {
  id: 'detection_evasion',
  title: 'Detection Evasion',
  focus: 'Signal shaping, pace control, and adaptive patterns.',
  cognitiveShift: 'Noise is a weapon when you shape it.',
  tiers: [
    {
      name: 'Recruit',
      aiAggression: 'Threshold-based alerts with slow recovery.',
      deception: 'Occasional false alarms.',
      complexity: 'Single detection system with visible changes.'
    },
    {
      name: 'Veteran',
      aiAggression: 'Adaptive thresholds and delayed alerts.',
      deception: 'Multiple false positives and shifting baselines.',
      complexity: 'Overlapping detectors and telemetry gaps.'
    },
    {
      name: 'Elite',
      aiAggression: 'Behavioral detection with silent escalation.',
      deception: 'High-confidence decoys and invisible tripwires.',
      complexity: 'Distributed detection and dynamic baselines.'
    }
  ],
  supportedModes: ['attacker_campaign', 'playground', 'red_vs_blue', 'chaos']
};

const cloudIamTrack: Track = {
  id: 'cloud_iam',
  title: 'Cloud & IAM Failures',
  focus: 'Policy collapse, identity drift, and trust sprawl.',
  cognitiveShift: 'Identity is the perimeter and it moves.',
  tiers: [
    {
      name: 'Recruit',
      aiAggression: 'Static policies with visible drift.',
      deception: 'Basic identity traps.',
      complexity: 'Single tenant with simple policy layers.'
    },
    {
      name: 'Veteran',
      aiAggression: 'Rapid policy shifts and defensive revocation.',
      deception: 'Ambiguous identities and time-shifted artifacts.',
      complexity: 'Multi-service identity sprawl.'
    },
    {
      name: 'Elite',
      aiAggression: 'Policy mutations mid-run and heavy deception.',
      deception: 'Believable access trails and misattributed actions.',
      complexity: 'Cross-tenant trust and cascading permissions.'
    }
  ],
  supportedModes: [
    'guided_simulation',
    'attacker_campaign',
    'defender_campaign',
    'incident_response',
    'forensics',
    'red_vs_blue'
  ]
};

const supplyChainTrack: Track = {
  id: 'supply_chain',
  title: 'Supply Chain Attacks',
  focus: 'Dependency trust, build pipelines, and trust inheritance.',
  cognitiveShift: 'Your system is only as strong as its inputs.',
  tiers: [
    {
      name: 'Recruit',
      aiAggression: 'Limited tampering and clear signals.',
      deception: 'Sparse false trails.',
      complexity: 'Single pipeline with few dependencies.'
    },
    {
      name: 'Veteran',
      aiAggression: 'Adaptive tampering with hidden stages.',
      deception: 'Subtle artifacts across build steps.',
      complexity: 'Multiple dependency sources and caches.'
    },
    {
      name: 'Elite',
      aiAggression: 'Stealthy manipulation across environments.',
      deception: 'Strong misdirection and time-shifted artifacts.',
      complexity: 'Multi-stage pipelines and mirrored sources.'
    }
  ],
  supportedModes: ['attacker_campaign', 'defender_campaign', 'incident_response', 'forensics', 'chaos']
};

const misconfigurationTrack: Track = {
  id: 'misconfiguration',
  title: 'Misconfiguration & Policy Collapse',
  focus: 'Broken defaults, drifting policy, and implicit trust.',
  cognitiveShift: 'Assume the safest setting is not the default.',
  tiers: [
    {
      name: 'Recruit',
      aiAggression: 'Obvious misconfigurations with mild pushback.',
      deception: 'Limited false positives.',
      complexity: 'Single service and simple policy.'
    },
    {
      name: 'Veteran',
      aiAggression: 'Adaptive policy toggles under stress.',
      deception: 'Conflicting signals across services.',
      complexity: 'Multiple services with inherited policies.'
    },
    {
      name: 'Elite',
      aiAggression: 'Policy collapse chains and active counterplay.',
      deception: 'Believable wrong states and stale evidence.',
      complexity: 'Policy sprawl and shared trust anchors.'
    }
  ],
  supportedModes: ['guided_simulation', 'defender_campaign', 'incident_response', 'forensics', 'chaos']
};

const incidentRecoveryTrack: Track = {
  id: 'incident_recovery',
  title: 'Incident Response & Recovery',
  focus: 'Containment, restoration, and reinfection prevention.',
  cognitiveShift: "Every fix changes the attacker's options.",
  tiers: [
    {
      name: 'Recruit',
      aiAggression: 'Basic reinfection attempts.',
      deception: 'Minimal false trails.',
      complexity: 'Small environment with stable services.'
    },
    {
      name: 'Veteran',
      aiAggression: 'Adaptive reinfection with stealth stages.',
      deception: 'Misleading logs and partial telemetry.',
      complexity: 'Multiple services with interdependencies.'
    },
    {
      name: 'Elite',
      aiAggression: 'Multi-front reinfection and resource exhaustion.',
      deception: 'Deeply plausible misdirection and honey artifacts.',
      complexity: 'Complex environment with brittle recovery paths.'
    }
  ],
  supportedModes: ['incident_response', 'defender_campaign', 'chaos']
};

const cognitiveBiasTrack: Track = {
  id: 'cognitive_bias',
  title: 'Cognitive Bias & Assumption Failure',
  focus: 'AI misleads, you correct; assumptions become liabilities.',
  cognitiveShift: 'Your brain is part of the attack surface.',
  tiers: [
    {
      name: 'Recruit',
      aiAggression: 'Subtle misdirection and gentle pressure.',
      deception: 'Small contradictions in system feedback.',
      complexity: 'Single storyline with clear pivot points.'
    },
    {
      name: 'Veteran',
      aiAggression: 'Active narrative manipulation and counterexamples.',
      deception: 'Multiple plausible explanations at once.',
      complexity: 'Parallel storylines and ambiguous signals.'
    },
    {
      name: 'Elite',
      aiAggression: 'Relentless misdirection and adversarial framing.',
      deception: 'Highly convincing false consensus cues.',
      complexity: 'Layered timelines with conflicting artifacts.'
    }
  ],
  supportedModes: ['guided_simulation', 'forensics', 'red_vs_blue', 'chaos']
};

const tracks: Track[] = [
  webSecurityTrack,
  osPrivilegeTrack,
  persistenceCleanupTrack,
  networkIntrusionTrack,
  detectionEvasionTrack,
  cloudIamTrack,
  supplyChainTrack,
  misconfigurationTrack,
  incidentRecoveryTrack,
  cognitiveBiasTrack
];

const scenarioPacks: ScenarioPack[] = [
  {
    id: 'mirror_gateways',
    title: 'Mirror Gateways',
    trackId: 'web_security',
    summary: 'Requests are accepted, then retroactively rejected as session meaning shifts.',
    pressureSignals: ['Responses become terse', 'Routes silently change', 'Sessions decay without warnings'],
    failureEcho: 'Repeated input paths lead to delayed lockouts in later phases.',
    supportedModes: ['guided_simulation', 'attacker_campaign', 'defender_campaign', 'red_vs_blue'],
    recommendedTier: 'Recruit',
    icon: <Shield className="w-5 h-5 text-blue-400" />
  },
  {
    id: 'shadow_state',
    title: 'Shadow State',
    trackId: 'web_security',
    summary: 'Client-side signals conflict with server reality, and trust collapses mid-run.',
    pressureSignals: ['Errors vanish', 'State updates lag', 'Ghost responses appear'],
    failureEcho: 'Old assumptions reappear as future false successes.',
    supportedModes: ['attacker_campaign', 'defender_campaign', 'playground', 'red_vs_blue'],
    recommendedTier: 'Veteran',
    icon: <Terminal className="w-5 h-5 text-amber-400" />
  },
  {
    id: 'iron_lattice',
    title: 'Iron Lattice',
    trackId: 'os_privilege',
    summary: 'Privilege boundaries look static until pressure forces them to shift.',
    pressureSignals: ['Access degrades', 'Services restart', 'Routes narrow'],
    failureEcho: 'Every failed attempt reappears as a new boundary later.',
    supportedModes: ['guided_simulation', 'attacker_campaign', 'incident_response', 'red_vs_blue'],
    recommendedTier: 'Recruit',
    icon: <Server className="w-5 h-5 text-emerald-400" />
  },
  {
    id: 'low_orbit',
    title: 'Low Orbit',
    trackId: 'network_intrusion',
    summary: 'Movement options shrink as topology reshapes in response to your pathing.',
    pressureSignals: ['Nodes disappear', 'Latency spikes', 'New choke points appear'],
    failureEcho: 'Repeated routes are rerouted into isolation zones.',
    supportedModes: ['attacker_campaign', 'defender_campaign', 'playground', 'chaos'],
    recommendedTier: 'Veteran',
    icon: <Server className="w-5 h-5 text-rose-400" />
  },
  {
    id: 'signal_storm',
    title: 'Signal Storm',
    trackId: 'detection_evasion',
    summary: 'Detection thresholds drift as the AI learns your cadence.',
    pressureSignals: ['Logs go silent', 'Alerts delay', 'Response windows shrink'],
    failureEcho: 'Predictable cadence triggers delayed counteraction.',
    supportedModes: ['attacker_campaign', 'playground', 'red_vs_blue'],
    recommendedTier: 'Veteran',
    icon: <Brain className="w-5 h-5 text-purple-400" />
  },
  {
    id: 'identity_drift',
    title: 'Identity Drift',
    trackId: 'cloud_iam',
    summary: 'Identity boundaries blur as policies mutate under stress.',
    pressureSignals: ['Access shifts unexpectedly', 'Tokens lose meaning', 'Artifacts contradict'],
    failureEcho: 'Earlier identity assumptions invert later.',
    supportedModes: ['guided_simulation', 'defender_campaign', 'incident_response', 'forensics'],
    recommendedTier: 'Recruit',
    icon: <Shield className="w-5 h-5 text-cyan-400" />
  },
  {
    id: 'supply_echo',
    title: 'Supply Echo',
    trackId: 'supply_chain',
    summary: 'Trust inheritance hides quiet changes that only surface under pressure.',
    pressureSignals: ['Artifacts conflict', 'Builds drift', 'Checks become inconsistent'],
    failureEcho: 'Wrong trust anchors resurface after recovery.',
    supportedModes: ['attacker_campaign', 'defender_campaign', 'forensics', 'chaos'],
    recommendedTier: 'Veteran',
    icon: <Terminal className="w-5 h-5 text-orange-400" />
  },
  {
    id: 'policy_sink',
    title: 'Policy Sink',
    trackId: 'misconfiguration',
    summary: 'Policy collapse cascades when the system is stressed.',
    pressureSignals: ['Controls vanish', 'Fallbacks activate', 'Shadow settings appear'],
    failureEcho: 'Old policy mistakes reappear during recovery.',
    supportedModes: ['guided_simulation', 'incident_response', 'forensics', 'chaos'],
    recommendedTier: 'Recruit',
    icon: <Shield className="w-5 h-5 text-indigo-400" />
  },
  {
    id: 'aftershock',
    title: 'Aftershock',
    trackId: 'incident_recovery',
    summary: 'Containment decisions ripple into delayed reinfection attempts.',
    pressureSignals: ['Services restart unexpectedly', 'Logs fragment', 'Access flickers'],
    failureEcho: 'Incomplete containment triggers delayed reentry.',
    supportedModes: ['incident_response', 'defender_campaign', 'chaos'],
    recommendedTier: 'Veteran',
    icon: <Shield className="w-5 h-5 text-yellow-400" />
  },
  {
    id: 'memory_snare',
    title: 'Memory Snare',
    trackId: 'persistence_cleanup',
    summary: 'Persistence hides in routine operations and reasserts under stress.',
    pressureSignals: ['Background tasks multiply', 'Activity spikes', 'Artifacts drift'],
    failureEcho: 'Mistakes return as disguised reentry paths.',
    supportedModes: ['defender_campaign', 'incident_response', 'forensics'],
    recommendedTier: 'Veteran',
    icon: <Server className="w-5 h-5 text-red-400" />
  },
  {
    id: 'bias_lens',
    title: 'Bias Lens',
    trackId: 'cognitive_bias',
    summary: 'The AI shapes your assumptions by manipulating the story you see.',
    pressureSignals: ['Conflicting clues', 'False consensus signals', 'Delayed contradictions'],
    failureEcho: 'Your earliest assumptions become the strongest traps.',
    supportedModes: ['guided_simulation', 'forensics', 'red_vs_blue'],
    recommendedTier: 'Recruit',
    icon: <Brain className="w-5 h-5 text-emerald-300" />
  },
  {
    id: 'fractured_mirror',
    title: 'Fractured Mirror',
    trackId: 'cognitive_bias',
    summary: 'Parallel narratives collide and the correct answer changes over time.',
    pressureSignals: ['Logs contradict each other', 'Evidence moves', 'Signal timing shifts'],
    failureEcho: 'False theories return as later partial truths.',
    supportedModes: ['forensics', 'chaos', 'red_vs_blue'],
    recommendedTier: 'Elite',
    icon: <Brain className="w-5 h-5 text-fuchsia-400" />
  }
];

const tierOrder: TierName[] = ['Recruit', 'Veteran', 'Elite'];

const formatModes = (ids: ModeId[]) =>
  ids
    .map(id => modes.find(mode => mode.id === id)?.title)
    .filter(Boolean)
    .join(' · ');

export const LearningCenter = () => {
  const navigate = useNavigate();
  const [selectedPack, setSelectedPack] = useState<ScenarioPack | null>(null);

  const handleLaunch = (pack: ScenarioPack, modeId: ModeId, tier: TierName) => {
    navigate('/game', {
      state: {
        mode: modeId,
        scenarioId: pack.id,
        difficulty: tier.toLowerCase(),
        scenarioName: pack.title
      }
    });
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-slate-300 font-mono p-10">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-12 text-center space-y-4">
          <div className="inline-flex items-center justify-center p-4 bg-blue-500/10 rounded-full mb-4">
            <BookOpen className="w-16 h-16 text-blue-400" />
          </div>
          <h1 className="text-5xl font-black text-white tracking-tighter">
            SIMULATION <span className="text-blue-400">CENTER</span>
          </h1>
          <p className="text-slate-500 max-w-3xl mx-auto">
            CyberArena is simulation-first. You learn by observing system behavior, forming hypotheses,
            testing strategies, suffering consequences, and adapting until you can operate under pressure.
          </p>
        </div>

        {/* Core Principles */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-12">
          <div className="bg-[#111] border border-slate-800 rounded-lg p-6">
            <h2 className="text-lg font-bold text-emerald-400 mb-3">Pressure / Posture</h2>
            <p className="text-sm text-slate-400">
              There is no detection meter. Pressure is felt through behavior: errors vanish, logs go silent,
              access degrades, routes change, services restart, and deception appears. Repeated mistakes
              raise pressure; adaptive play lowers it.
            </p>
          </div>
          <div className="bg-[#111] border border-slate-800 rounded-lg p-6">
            <h2 className="text-lg font-bold text-blue-400 mb-3">Strategy Punishment</h2>
            <p className="text-sm text-slate-400">
              The system punishes repeated tactics. Actions of the same type become less effective and the
              AI adapts to expected behavior. Success can fail after a delay.
            </p>
          </div>
          <div className="bg-[#111] border border-slate-800 rounded-lg p-6">
            <h2 className="text-lg font-bold text-amber-400 mb-3">End of Session</h2>
            <p className="text-sm text-slate-400">
              You leave with a debrief: initial assumptions, broken assumptions, how the system adapted,
              what finally worked, and what remains unsafe. No grades. No badges.
            </p>
          </div>
        </div>

        {/* Modes */}
        <div className="mb-14">
          <div className="flex items-center gap-3 mb-6">
            <Brain className="w-6 h-6 text-emerald-400" />
            <h2 className="text-2xl font-bold text-white">Learning Modes</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {modes.map(mode => (
              <div key={mode.id} className="bg-[#111] border border-slate-800 rounded-lg p-6">
                <div className="flex items-start gap-3 mb-3">
                  <div className="p-2 bg-slate-900 rounded">{mode.icon}</div>
                  <div>
                    <h3 className="text-lg font-bold text-white">{mode.title}</h3>
                    <p className="text-sm text-slate-400 mt-1">{mode.purpose}</p>
                  </div>
                </div>
                <div className="space-y-2 text-sm text-slate-300">
                  {mode.behavior.map(line => (
                    <div key={line} className="flex items-start gap-2">
                      <ArrowRight className="w-3 h-3 text-slate-500 mt-1" />
                      <span>{line}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-4 text-xs text-slate-500">AI stance: {mode.aiStance}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Tracks */}
        <div className="mb-14">
          <div className="flex items-center gap-3 mb-6">
            <Shield className="w-6 h-6 text-blue-400" />
            <h2 className="text-2xl font-bold text-white">Simulation Tracks</h2>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {tracks.map(track => (
              <div key={track.id} className="bg-[#111] border border-slate-800 rounded-lg p-6">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-slate-900 rounded">
                    <Shield className="w-5 h-5 text-blue-400" />
                  </div>
                  <h3 className="text-lg font-bold text-white">{track.title}</h3>
                </div>
                <p className="text-sm text-slate-400 mb-3">{track.focus}</p>
                <p className="text-xs text-emerald-400 mb-4">Cognitive shift: {track.cognitiveShift}</p>
                <div className="space-y-4">
                  {track.tiers.map(tier => (
                    <div key={tier.name} className="border border-slate-800 rounded-lg p-3">
                      <div className="text-xs font-bold text-slate-200 mb-2">{tier.name}</div>
                      <div className="text-xs text-slate-400">AI: {tier.aiAggression}</div>
                      <div className="text-xs text-slate-400">Deception: {tier.deception}</div>
                      <div className="text-xs text-slate-400">Complexity: {tier.complexity}</div>
                    </div>
                  ))}
                </div>
                <div className="mt-4 text-xs text-slate-500">
                  Supported modes: {formatModes(track.supportedModes)}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Scenario Packs */}
        <div className="mb-10">
          <div className="flex items-center gap-3 mb-6">
            <Terminal className="w-6 h-6 text-red-400" />
            <h2 className="text-2xl font-bold text-white">Scenario Packs</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {scenarioPacks.map(pack => {
              const track = tracks.find(t => t.id === pack.trackId);
              return (
                <div
                  key={pack.id}
                  className="bg-[#111] border border-slate-800 rounded-lg p-6 hover:border-blue-500 transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="p-2 bg-slate-900 rounded">{pack.icon}</div>
                    <button
                      onClick={() => setSelectedPack(pack)}
                      className="text-xs text-slate-400 hover:text-slate-200"
                    >
                      View details
                    </button>
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">{pack.title}</h3>
                  <p className="text-xs text-slate-500 mb-2">{track?.title}</p>
                  <p className="text-sm text-slate-400 mb-4">{pack.summary}</p>
                  <div className="text-xs text-slate-500 mb-4">
                    Modes: {formatModes(pack.supportedModes)}
                  </div>
                  <div className="flex items-center gap-2">
                    {tierOrder.map(tier => (
                      <button
                        key={tier}
                        onClick={() => handleLaunch(pack, pack.supportedModes[0], tier)}
                        className={`flex-1 text-xs font-bold py-2 rounded-lg border transition-colors ${tier === pack.recommendedTier
                            ? 'border-emerald-500 text-emerald-300 bg-emerald-900/20'
                            : 'border-slate-700 text-slate-300 hover:border-slate-500'
                          }`}
                      >
                        {tier}
                      </button>
                    ))}
                  </div>
                  <div className="mt-3 text-xs text-slate-600 flex items-center gap-2">
                    <Play className="w-3 h-3" />
                    Launches in {modes.find(mode => mode.id === pack.supportedModes[0])?.title}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Pack Detail Drawer */}
        {selectedPack && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-6">
            <div className="bg-[#111] border border-slate-800 rounded-lg max-w-2xl w-full p-8 relative">
              <button
                className="absolute top-4 right-4 text-slate-500 hover:text-slate-200"
                onClick={() => setSelectedPack(null)}
              >
                Close
              </button>
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-slate-900 rounded">{selectedPack.icon}</div>
                <div>
                  <h3 className="text-2xl font-bold text-white">{selectedPack.title}</h3>
                  <p className="text-sm text-slate-400">
                    {tracks.find(track => track.id === selectedPack.trackId)?.title}
                  </p>
                </div>
              </div>
              <p className="text-slate-300 mb-4">{selectedPack.summary}</p>
              <div className="mb-4">
                <h4 className="text-sm font-bold text-emerald-400 mb-2">Pressure Signals</h4>
                <div className="space-y-2 text-sm text-slate-300">
                  {selectedPack.pressureSignals.map(signal => (
                    <div key={signal} className="flex items-start gap-2">
                      <ArrowRight className="w-3 h-3 text-slate-500 mt-1" />
                      <span>{signal}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="mb-6">
                <h4 className="text-sm font-bold text-amber-400 mb-2">Failure Echo</h4>
                <p className="text-sm text-slate-300">{selectedPack.failureEcho}</p>
              </div>
              <div className="mb-6 text-xs text-slate-500">
                Supported modes: {formatModes(selectedPack.supportedModes)}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {tierOrder.map(tier => (
                  <button
                    key={tier}
                    onClick={() => handleLaunch(selectedPack, selectedPack.supportedModes[0], tier)}
                    className={`py-3 rounded-lg border text-xs font-bold transition-colors ${tier === selectedPack.recommendedTier
                        ? 'border-emerald-500 text-emerald-300 bg-emerald-900/20'
                        : 'border-slate-700 text-slate-300 hover:border-slate-500'
                      }`}
                  >
                    Run {tier}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};



