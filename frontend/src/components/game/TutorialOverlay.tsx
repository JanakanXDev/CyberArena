import React, { useEffect, useState } from 'react';
import { ArrowUp, ArrowRight, ArrowDown, ArrowLeft } from 'lucide-react';

interface TutorialStep {
    elementId: string;
    message: string;
    position: 'top' | 'right' | 'bottom' | 'left';
}

interface TutorialOverlayProps {
    step: TutorialStep | null;
    onDismiss: () => void;
}

export const TutorialOverlay: React.FC<TutorialOverlayProps> = ({ step, onDismiss }) => {
    const [targetRect, setTargetRect] = useState<DOMRect | null>(null);

    useEffect(() => {
        if (!step) return;

        // Find the element on the screen
        const element = document.getElementById(step.elementId);
        if (element) {
            setTargetRect(element.getBoundingClientRect());
            
            // Auto-scroll if off screen
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            console.warn(`Tutorial target not found: ${step.elementId}`);
        }
    }, [step]);

    if (!step || !targetRect) return null;

    // Calculate position for the explanation box
    let boxStyle: React.CSSProperties = {};
    const gap = 20;

    switch (step.position) {
        case 'left':
            boxStyle = { top: targetRect.top, left: targetRect.left - 320 - gap };
            break;
        case 'right':
            boxStyle = { top: targetRect.top, left: targetRect.right + gap };
            break;
        case 'top':
            boxStyle = { top: targetRect.top - 150 - gap, left: targetRect.left };
            break;
        case 'bottom':
            boxStyle = { top: targetRect.bottom + gap, left: targetRect.left };
            break;
    }

    return (
        <div className="fixed inset-0 z-50 pointer-events-none">
            {/* Dimmed Background - Clip out the target area */}
            <div className="absolute inset-0 bg-black/60 transition-opacity duration-500" />
            
            {/* The Mentor Box */}
            <div 
                className="absolute w-80 bg-slate-900 border border-amber-500 shadow-[0_0_30px_rgba(245,158,11,0.3)] rounded-lg p-5 pointer-events-auto animate-in fade-in slide-in-from-bottom-4 duration-500"
                style={boxStyle}
            >
                <div className="flex items-center gap-2 mb-3 border-b border-slate-800 pb-2">
                    <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
                    <span className="text-amber-500 font-bold uppercase tracking-widest text-xs">CTO Guidance</span>
                </div>
                <p className="text-slate-300 text-sm leading-relaxed mb-4">
                    {step.message}
                </p>
                <div className="flex justify-end">
                    <button 
                        onClick={onDismiss}
                        className="text-[10px] font-bold text-slate-500 hover:text-white uppercase tracking-widest bg-slate-800 px-3 py-1 rounded transition-colors"
                    >
                        Dismiss
                    </button>
                </div>
                
                {/* Pointer Arrow */}
                {step.position === 'right' && <ArrowLeft className="absolute top-6 -left-6 w-6 h-6 text-amber-500 animate-bounce" />}
                {step.position === 'left' && <ArrowRight className="absolute top-6 -right-6 w-6 h-6 text-amber-500 animate-bounce" />}
                {step.position === 'bottom' && <ArrowUp className="absolute -top-6 left-6 w-6 h-6 text-amber-500 animate-bounce" />}
                {step.position === 'top' && <ArrowDown className="absolute -bottom-6 left-6 w-6 h-6 text-amber-500 animate-bounce" />}
            </div>
        </div>
    );
};