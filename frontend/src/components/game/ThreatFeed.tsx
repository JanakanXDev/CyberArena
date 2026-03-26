import React, { useEffect, useRef } from 'react';
import { AiMove } from '../../types/game';
import { Shield, Skull, AlertTriangle, Zap, Eye } from 'lucide-react';

interface ThreatFeedProps {
    aiLastMove?: AiMove;
    aiMoveHistory?: AiMove[];
    aiPersona?: string; // "attacker" | "defender"
}

const SEVERITY_CONFIG = {
    low: { border: 'border-blue-500/40', bg: 'bg-blue-500/5', text: 'text-blue-400', badge: 'bg-blue-500/20 text-blue-300', label: 'LOW', icon: Eye },
    medium: { border: 'border-amber-500/50', bg: 'bg-amber-500/8', text: 'text-amber-400', badge: 'bg-amber-500/20 text-amber-300', label: 'MEDIUM', icon: AlertTriangle },
    high: { border: 'border-red-500/60', bg: 'bg-red-500/8', text: 'text-red-400', badge: 'bg-red-500/20 text-red-300', label: 'HIGH', icon: Skull },
    critical: { border: 'border-red-400/80', bg: 'bg-red-500/12', text: 'text-red-300', badge: 'bg-red-400/30 text-red-200', label: 'CRITICAL', icon: Zap },
};

export const ThreatFeed: React.FC<ThreatFeedProps> = ({
    aiLastMove,
    aiMoveHistory = [],
    aiPersona = 'attacker',
}) => {
    const prevMoveRef = useRef<string | undefined>();
    const cardRef = useRef<HTMLDivElement>(null);

    // Flash animation when a new move arrives
    useEffect(() => {
        if (aiLastMove && aiLastMove.name !== prevMoveRef.current) {
            prevMoveRef.current = aiLastMove.name;
            cardRef.current?.animate(
                [
                    { boxShadow: '0 0 0 2px rgba(239,68,68,0.8)', opacity: 0.6 },
                    { boxShadow: '0 0 24px 4px rgba(239,68,68,0.4)', opacity: 1 },
                    { boxShadow: '0 0 0 0 rgba(239,68,68,0)', opacity: 1 },
                ],
                { duration: 800, easing: 'ease-out' }
            );
        }
    }, [aiLastMove]);

    const personaLabel = aiPersona === 'attacker' ? 'AI Attacker' : 'AI Defender';
    const PersonaIcon = aiPersona === 'attacker' ? Skull : Shield;

    return (
        <div className="flex flex-col gap-3 h-full">
            {/* Header */}
            <div className="flex items-center gap-2 px-1">
                <PersonaIcon
                    className={`w-4 h-4 ${aiPersona === 'attacker' ? 'text-red-400' : 'text-cyan-400'}`}
                />
                <span className="text-xs font-bold uppercase tracking-widest text-slate-400">
                    {personaLabel} — Last Move
                </span>
            </div>

            {/* Primary move card */}
            {aiLastMove ? (
                <PrimaryMoveCard move={aiLastMove} cardRef={cardRef} />
            ) : (
                <div className="flex-1 flex items-center justify-center rounded-lg border border-slate-800 bg-slate-900/30">
                    <div className="text-center">
                        <Eye className="w-6 h-6 text-slate-600 mx-auto mb-2" />
                        <p className="text-xs text-slate-600 font-mono">Waiting for adversary…</p>
                        <p className="text-[10px] text-slate-700 mt-1">Take an action to provoke a response</p>
                    </div>
                </div>
            )}

            {/* Move history — last 3 prior moves */}
            {aiMoveHistory.length > 1 && (
                <div className="space-y-1.5">
                    <div className="text-[10px] font-bold text-slate-600 uppercase tracking-widest px-1">
                        Previous Moves
                    </div>
                    {aiMoveHistory.slice(1, 4).map((m, i) => (
                        <HistoryMoveRow key={i} move={m} />
                    ))}
                </div>
            )}
        </div>
    );
};

// ── Primary card ─────────────────────────────────────────────────────────────

const PrimaryMoveCard: React.FC<{
    move: AiMove;
    cardRef: React.RefObject<HTMLDivElement>;
}> = ({ move, cardRef }) => {
    const cfg = SEVERITY_CONFIG[move.severity] ?? SEVERITY_CONFIG.medium;
    const Icon = cfg.icon;

    return (
        <div
            ref={cardRef}
            className={`rounded-lg border-2 ${cfg.border} ${cfg.bg} p-4 space-y-3 transition-all duration-300`}
        >
            {/* Title row */}
            <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                    <Icon className={`w-4 h-4 flex-shrink-0 ${cfg.text}`} />
                    <span className={`text-sm font-bold ${cfg.text} font-mono`}>{move.label}</span>
                </div>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${cfg.badge} flex-shrink-0`}>
                    {cfg.label}
                </span>
            </div>

            {/* Description */}
            <p className="text-xs text-slate-300 leading-relaxed">{move.description}</p>

            {/* Effects */}
            {move.effects_summary && move.effects_summary.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                    {move.effects_summary.map((e, i) => (
                        <span
                            key={i}
                            className={`text-[10px] font-mono px-2 py-0.5 rounded ${e.startsWith('+') && e.includes('Pressure')
                                    ? 'bg-red-500/20 text-red-300'
                                    : e.startsWith('-') && e.includes('Stability')
                                        ? 'bg-orange-500/20 text-orange-300'
                                        : e.includes('Locks')
                                            ? 'bg-purple-500/20 text-purple-300'
                                            : 'bg-slate-700 text-slate-400'
                                }`}
                        >
                            {e}
                        </span>
                    ))}
                </div>
            )}

            {/* Counter hint */}
            {move.counter_hint && (
                <div className="border-t border-slate-700/50 pt-2 flex gap-2 items-start">
                    <Shield className="w-3 h-3 text-cyan-500 flex-shrink-0 mt-0.5" />
                    <p className="text-[10px] text-cyan-400/80 leading-relaxed">
                        <span className="font-bold text-cyan-400">Counter: </span>
                        {move.counter_hint}
                    </p>
                </div>
            )}
        </div>
    );
};

// ── History row ───────────────────────────────────────────────────────────────

const HistoryMoveRow: React.FC<{ move: AiMove }> = ({ move }) => {
    const cfg = SEVERITY_CONFIG[move.severity] ?? SEVERITY_CONFIG.medium;
    return (
        <div className="flex items-center gap-2 px-2 py-1.5 rounded bg-slate-900/40 border border-slate-800/50">
            <span className={`text-[10px] font-bold shrink-0 ${cfg.text}`}>{cfg.label[0]}</span>
            <span className="text-[11px] text-slate-400 font-mono truncate">{move.label}</span>
            {move.effects_summary?.[0] && (
                <span className="text-[10px] text-slate-600 ml-auto shrink-0">{move.effects_summary[0]}</span>
            )}
        </div>
    );
};
