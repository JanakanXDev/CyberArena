import React, { useState, useEffect, useCallback } from 'react';
import { LearningMode } from '../../types/game';
import { Shield, Sword, Eye, Zap, ChevronRight, Lock, Clock } from 'lucide-react';

interface BriefingScreenProps {
    mode: LearningMode;
    scenarioName: string;
    onBegin: () => void;
}

interface BriefingContent {
    icon: React.ReactNode;
    roleTag: string;
    roleColor: string;
    headline: string;
    narrative: string[];
    concepts: { term: string; plain: string }[];
    mission: string;
    accentColor: string;
    bgGradient: string;
}

const BRIEFINGS: Record<LearningMode, BriefingContent> = {
    guided_simulation: {
        icon: <Eye className="w-10 h-10" />,
        roleTag: 'ANALYST',
        roleColor: 'text-purple-400',
        headline: 'You are a Digital Analyst',
        narrative: [
            'A legacy web application is behaving strangely. Requests that should fail are quietly succeeding. Inputs that should cause errors are disappearing without a trace.',
            'Your job is NOT to break anything. Your job is to understand WHY it\'s broken — by forming a belief, testing it, and following the evidence.',
            'Think like a scientist investigating a mystery, not a hacker trying to cause damage.',
        ],
        concepts: [
            { term: 'Hypothesis', plain: 'A belief you form about how the system works. You test it to see if you\'re right.' },
            { term: 'WAF', plain: 'Web Application Firewall — a security gate that checks traffic before it reaches the app.' },
            { term: 'Session State', plain: 'The server\'s memory of who you are and what you\'re doing between requests.' },
            { term: 'Pressure', plain: 'How much the system is under stress. High pressure = things are about to break.' },
        ],
        mission: 'Test your hypotheses. Discover the true vulnerability. Achieve mission victory.',
        accentColor: 'purple',
        bgGradient: 'from-purple-950/40 via-black to-black',
    },
    attacker_campaign: {
        icon: <Sword className="w-10 h-10" />,
        roleTag: 'INFILTRATOR',
        roleColor: 'text-red-400',
        headline: 'You are a Silent Infiltrator',
        narrative: [
            'The target system has active defenses. An AI opponent is watching your every move — adapting, blocking, and shifting its behavior in real-time.',
            'Brute force won\'t work. You need to read the system\'s reactions, move slowly, and strike where the defenses have blind spots.',
            'Every action you take teaches the defender something new. Move smart, or lose the window.',
        ],
        concepts: [
            { term: 'AI Aggressiveness', plain: 'How actively the defender is responding. It rises as you probe more.' },
            { term: 'Evasion', plain: 'Acting in a way that avoids triggering detection — slow, quiet, indirect.' },
            { term: 'Blind Spot', plain: 'A part of the system the defender isn\'t watching. Your most valuable entry point.' },
            { term: 'Escalate', plain: 'A high-risk action that can accelerate your goal — but also alerts the defender.' },
        ],
        mission: 'Bypass the active defense before it closes every opening. Strike without being seen.',
        accentColor: 'red',
        bgGradient: 'from-red-950/40 via-black to-black',
    },
    defender_campaign: {
        icon: <Shield className="w-10 h-10" />,
        roleTag: 'DEFENDER',
        roleColor: 'text-blue-400',
        headline: 'You are the Last Line of Defense',
        narrative: [
            'Bad news: the attacker is already inside. The system was breached before you arrived. You\'re walking into an active incident.',
            'Your mission is damage control. Find what\'s already compromised, contain the spread, and restore system integrity before it\'s too late.',
            'Every turn you waste, the attacker digs deeper. Prioritize — you can\'t fix everything at once.',
        ],
        concepts: [
            { term: 'Compromised', plain: 'A component the attacker has already accessed or tampered with.' },
            { term: 'Stability', plain: 'How intact the system is. It drops as the attacker exploits more of it.' },
            { term: 'Isolate', plain: 'Cutting a component off from the rest of the system to stop the attacker spreading.' },
            { term: 'Hardening', plain: 'Applying protections to a component so the attacker can\'t exploit it again.' },
        ],
        mission: 'Contain the breach. Restore stability. Don\'t let the attacker win.',
        accentColor: 'blue',
        bgGradient: 'from-blue-950/40 via-black to-black',
    },
    playground: {
        icon: <Zap className="w-10 h-10" />,
        roleTag: 'EXPLORER',
        roleColor: 'text-amber-400',
        headline: 'Open Sandbox — Your Rules',
        narrative: [
            'This is your laboratory. No win condition. No time limit. Just you and the system.',
            'Try things that seem like bad ideas. Push actions to their limits. See what breaks and why.',
            'Real security professionals learn by breaking controlled systems intentionally. This is that space.',
        ],
        concepts: [
            { term: 'Fuzzing', plain: 'Sending random, unexpected, or extreme inputs to see how the system reacts.' },
            { term: 'Race Condition', plain: 'Sending two conflicting requests at the exact same time to confuse the system.' },
            { term: 'Entropy', plain: 'Randomness. High-entropy attacks are unpredictable — but also hard to control.' },
            { term: 'Stability Collapse', plain: 'When the system has taken too much damage and goes completely offline.' },
        ],
        mission: 'There is no mission. Break things. Learn why they break.',
        accentColor: 'amber',
        bgGradient: 'from-amber-950/30 via-black to-black',
    },
};

const ACCENT_CLASSES: Record<string, { border: string; text: string; bg: string; button: string; ring: string }> = {
    purple: {
        border: 'border-purple-500/40',
        text: 'text-purple-400',
        bg: 'bg-purple-900/20',
        button: 'bg-purple-600 hover:bg-purple-500',
        ring: 'ring-purple-500/30',
    },
    red: {
        border: 'border-red-500/40',
        text: 'text-red-400',
        bg: 'bg-red-900/20',
        button: 'bg-red-700 hover:bg-red-600',
        ring: 'ring-red-500/30',
    },
    blue: {
        border: 'border-blue-500/40',
        text: 'text-blue-400',
        bg: 'bg-blue-900/20',
        button: 'bg-blue-700 hover:bg-blue-600',
        ring: 'ring-blue-500/30',
    },
    amber: {
        border: 'border-amber-500/40',
        text: 'text-amber-400',
        bg: 'bg-amber-900/20',
        button: 'bg-amber-600 hover:bg-amber-500',
        ring: 'ring-amber-500/30',
    },
};

const COUNTDOWN_SECONDS = 30;

export const BriefingScreen: React.FC<BriefingScreenProps> = ({ mode, scenarioName, onBegin }) => {
    const [secondsLeft, setSecondsLeft] = useState(COUNTDOWN_SECONDS);
    const [phase, setPhase] = useState<'narrative' | 'concepts'>('narrative');

    const briefing = BRIEFINGS[mode];
    const accent = ACCENT_CLASSES[briefing.accentColor];

    const handleBegin = useCallback(() => {
        onBegin();
    }, [onBegin]);

    useEffect(() => {
        if (secondsLeft <= 0) {
            handleBegin();
            return;
        }
        const timer = setTimeout(() => setSecondsLeft(s => s - 1), 1000);
        return () => clearTimeout(timer);
    }, [secondsLeft, handleBegin]);

    const circumference = 2 * Math.PI * 22;
    const strokeDash = (secondsLeft / COUNTDOWN_SECONDS) * circumference;

    return (
        <div className={`min-h-screen bg-gradient-to-br ${briefing.bgGradient} flex flex-col items-center justify-center p-6 font-mono`}>

            {/* Top badge */}
            <div className={`mb-6 px-4 py-1.5 rounded-full border text-xs tracking-widest uppercase font-bold ${accent.border} ${accent.text} ${accent.bg}`}>
                ⬡ MISSION BRIEFING — {briefing.roleTag}
            </div>

            {/* Main card */}
            <div className={`w-full max-w-3xl border rounded-xl overflow-hidden ${accent.border} ring-1 ${accent.ring} shadow-2xl shadow-black/80`}>

                {/* Header */}
                <div className={`px-8 py-6 border-b ${accent.border} ${accent.bg} flex items-center gap-4`}>
                    <div className={accent.text}>
                        {briefing.icon}
                    </div>
                    <div>
                        <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">{scenarioName}</div>
                        <h1 className="text-xl font-bold text-white">{briefing.headline}</h1>
                    </div>

                    {/* Circular countdown */}
                    <div className="ml-auto flex flex-col items-center gap-1">
                        <svg width="52" height="52" className="-rotate-90">
                            <circle cx="26" cy="26" r="22" fill="none" stroke="#1e293b" strokeWidth="3" />
                            <circle
                                cx="26" cy="26" r="22"
                                fill="none"
                                stroke={briefing.accentColor === 'red' ? '#ef4444' : briefing.accentColor === 'blue' ? '#3b82f6' : briefing.accentColor === 'amber' ? '#f59e0b' : '#a855f7'}
                                strokeWidth="3"
                                strokeDasharray={circumference}
                                strokeDashoffset={circumference - strokeDash}
                                strokeLinecap="round"
                                style={{ transition: 'stroke-dashoffset 1s linear' }}
                            />
                            <text
                                x="26" y="26"
                                textAnchor="middle"
                                dominantBaseline="central"
                                className="rotate-90"
                                fill="white"
                                fontSize="13"
                                fontWeight="bold"
                                style={{ transform: 'rotate(90deg)', transformOrigin: '26px 26px' }}
                            >
                                {secondsLeft}
                            </text>
                        </svg>
                        <span className="text-[9px] text-slate-500 uppercase tracking-widest">auto-start</span>
                    </div>
                </div>

                {/* Tab switcher */}
                <div className="flex border-b border-slate-800">
                    <button
                        onClick={() => setPhase('narrative')}
                        className={`flex-1 py-3 text-xs font-bold uppercase tracking-widest transition-colors ${phase === 'narrative' ? `${accent.text} border-b-2 ${accent.border} bg-slate-900/50` : 'text-slate-500 hover:text-slate-300'}`}
                    >
                        Situation
                    </button>
                    <button
                        onClick={() => setPhase('concepts')}
                        className={`flex-1 py-3 text-xs font-bold uppercase tracking-widest transition-colors ${phase === 'concepts' ? `${accent.text} border-b-2 ${accent.border} bg-slate-900/50` : 'text-slate-500 hover:text-slate-300'}`}
                    >
                        <Lock className="w-3 h-3 inline mr-1.5" />
                        Key Concepts
                    </button>
                </div>

                {/* Content area */}
                <div className="px-8 py-6 min-h-48 bg-black/40">
                    {phase === 'narrative' ? (
                        <div className="space-y-4">
                            {briefing.narrative.map((para, i) => (
                                <p key={i} className={`text-sm leading-relaxed ${i === 0 ? 'text-slate-200' : 'text-slate-400'}`}>
                                    {para}
                                </p>
                            ))}
                        </div>
                    ) : (
                        <div className="grid grid-cols-2 gap-3">
                            {briefing.concepts.map(c => (
                                <div key={c.term} className={`p-3 rounded-lg border ${accent.border} ${accent.bg}`}>
                                    <div className={`text-xs font-bold ${accent.text} mb-1 uppercase tracking-widest`}>{c.term}</div>
                                    <div className="text-xs text-slate-300 leading-relaxed">{c.plain}</div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Mission footer */}
                <div className={`px-8 py-4 border-t ${accent.border} ${accent.bg} flex items-center gap-3`}>
                    <Clock className="w-4 h-4 text-slate-500 shrink-0" />
                    <p className="text-xs text-slate-400 italic flex-1">
                        <span className={`font-bold ${accent.text}`}>Mission: </span>
                        {briefing.mission}
                    </p>
                </div>
            </div>

            {/* Begin button */}
            <button
                onClick={handleBegin}
                className={`mt-8 px-10 py-4 rounded-lg text-sm font-bold uppercase tracking-widest text-white flex items-center gap-3 transition-all duration-200 ${accent.button} shadow-lg hover:shadow-xl hover:scale-105 active:scale-100`}
            >
                Begin Mission
                <ChevronRight className="w-5 h-5" />
            </button>

            <p className="mt-4 text-[10px] text-slate-600 uppercase tracking-widest">
                Auto-starting in {secondsLeft}s · Click "Begin Mission" to start immediately
            </p>
        </div>
    );
};
