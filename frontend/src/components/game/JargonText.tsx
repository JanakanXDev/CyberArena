import React, { useState, useRef, useEffect, useCallback } from 'react';
import { JARGON_TERMS, JARGON } from '../../utils/jargon';

interface JargonTextProps {
    text: string;
    /** Limit how many unique terms get highlighted per block (default: 3). */
    maxHighlights?: number;
    className?: string;
}

interface Segment {
    text: string;
    term?: string;   // The matched jargon key (if this is a highlighted term)
}

/** Parses text into segments, tagging the first N unique jargon terms found. */
function parseSegments(text: string, maxHighlights: number): Segment[] {
    const segments: Segment[] = [];
    let remaining = text;
    let highlightCount = 0;
    const usedTerms = new Set<string>();

    while (remaining.length > 0) {
        let matched = false;

        if (highlightCount < maxHighlights) {
            for (const term of JARGON_TERMS) {
                // Skip aliases like 'entropy (ai)' that won't appear literally
                if (term.includes('(')) continue;

                const idx = remaining.toLowerCase().indexOf(term);
                if (idx === -1) continue;

                // Word-boundary check: character before and after mustn't be a letter
                const before = idx > 0 ? remaining[idx - 1] : ' ';
                const after = idx + term.length < remaining.length ? remaining[idx + term.length] : ' ';
                const wordBoundaryBefore = /\W/.test(before);
                const wordBoundaryAfter = /\W/.test(after);

                if (!wordBoundaryBefore || !wordBoundaryAfter) continue;
                if (usedTerms.has(term)) continue;

                // Push text before the match (if any)
                if (idx > 0) {
                    segments.push({ text: remaining.slice(0, idx) });
                }
                // Push the highlighted term
                segments.push({ text: remaining.slice(idx, idx + term.length), term });
                usedTerms.add(term);
                remaining = remaining.slice(idx + term.length);
                highlightCount++;
                matched = true;
                break;
            }
        }

        if (!matched) {
            segments.push({ text: remaining });
            remaining = '';
        }
    }

    return segments;
}

interface TooltipState {
    term: string;
    x: number;
    y: number;
}

export const JargonText: React.FC<JargonTextProps> = ({
    text,
    maxHighlights = 3,
    className,
}) => {
    const [tooltip, setTooltip] = useState<TooltipState | null>(null);
    const containerRef = useRef<HTMLSpanElement>(null);
    const hideTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

    const segments = parseSegments(text, maxHighlights);

    const showTooltip = useCallback((term: string, e: React.MouseEvent) => {
        if (hideTimer.current) clearTimeout(hideTimer.current);
        const rect = (e.target as HTMLElement).getBoundingClientRect();
        const containerRect = containerRef.current?.closest('.tooltip-boundary')?.getBoundingClientRect();
        const x = rect.left + rect.width / 2 - (containerRect?.left ?? 0);
        const y = rect.top - (containerRect?.top ?? 0);
        setTooltip({ term, x, y });
    }, []);

    const hideTooltip = useCallback(() => {
        hideTimer.current = setTimeout(() => setTooltip(null), 150);
    }, []);

    // Cleanup on unmount
    useEffect(() => () => { if (hideTimer.current) clearTimeout(hideTimer.current); }, []);

    return (
        <span ref={containerRef} className={className}>
            {segments.map((seg, i) => {
                if (!seg.term) {
                    return <span key={i}>{seg.text}</span>;
                }
                return (
                    <span
                        key={i}
                        onMouseEnter={(e) => showTooltip(seg.term!, e)}
                        onMouseLeave={hideTooltip}
                        className="relative inline cursor-help border-b border-dashed border-cyan-600/60 text-cyan-300/90 hover:text-cyan-200 transition-colors"
                    >
                        {seg.text}
                        {tooltip?.term === seg.term && (
                            <span
                                className="absolute z-50 pointer-events-none"
                                style={{
                                    left: '50%',
                                    bottom: 'calc(100% + 6px)',
                                    transform: 'translateX(-50%)',
                                    width: '220px',
                                }}
                            >
                                <span className="block bg-slate-900 border border-cyan-700/50 rounded-lg px-3 py-2 text-[11px] text-slate-200 leading-relaxed shadow-xl shadow-black/60 font-sans not-italic">
                                    <span className="block text-cyan-400 font-bold uppercase tracking-widest text-[9px] mb-1">
                                        {seg.term.toUpperCase()}
                                    </span>
                                    {JARGON[seg.term.toLowerCase()] ?? ''}
                                    {/* Arrow */}
                                    <span
                                        className="absolute left-1/2 -translate-x-1/2 -bottom-[6px] w-3 h-3 bg-slate-900 border-r border-b border-cyan-700/50 rotate-45"
                                        style={{ bottom: '-6px' }}
                                    />
                                </span>
                            </span>
                        )}
                    </span>
                );
            })}
        </span>
    );
};
