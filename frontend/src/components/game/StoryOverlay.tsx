import React, { useEffect, useState } from 'react';
import { Terminal, Shield, ChevronRight } from 'lucide-react';

interface StoryOverlayProps {
  sender: string;
  subject: string;
  message: string;
  onDismiss: () => void;
}

export const StoryOverlay: React.FC<StoryOverlayProps> = ({ sender, subject, message, onDismiss }) => {
  const [displayedText, setDisplayedText] = useState("");
  const [charIndex, setCharIndex] = useState(0);

  // Typewriter Effect
  useEffect(() => {
    if (charIndex < message.length) {
      const timeout = setTimeout(() => {
        setDisplayedText((prev) => prev + message[charIndex]);
        setCharIndex((prev) => prev + 1);
      }, 30); // Speed of typing (lower is faster)
      return () => clearTimeout(timeout);
    }
  }, [charIndex, message]);

  // Reset when message changes (new stage)
  useEffect(() => {
    setDisplayedText("");
    setCharIndex(0);
  }, [message]);

  return (
    <div className="absolute inset-0 z-50 bg-slate-950/95 flex items-center justify-center p-8 backdrop-blur-sm animate-in fade-in duration-500">
      <div className="max-w-2xl w-full bg-black border border-emerald-500/30 shadow-[0_0_50px_rgba(16,185,129,0.1)] p-8 relative overflow-hidden">
        
        {/* Decor: Scanlines */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] z-0 pointer-events-none bg-[length:100%_4px,3px_100%]" />
        
        {/* Header */}
        <div className="relative z-10 flex justify-between items-start mb-8 border-b border-slate-800 pb-4">
          <div>
            <div className="text-emerald-500 font-bold text-xs tracking-[0.3em] mb-1">INCOMING TRANSMISSION</div>
            <h2 className="text-white text-2xl font-black uppercase tracking-tighter">{subject}</h2>
          </div>
          <div className="text-right">
             <div className="text-xs text-slate-500 font-bold uppercase tracking-widest">Sender</div>
             <div className="text-emerald-400 font-mono font-bold">{sender}</div>
          </div>
        </div>

        {/* Body (Typewriter) */}
        <div className="relative z-10 min-h-[150px] font-mono text-lg text-slate-300 leading-relaxed whitespace-pre-wrap">
          {displayedText}
          <span className="animate-pulse text-emerald-500">_</span>
        </div>

        {/* Footer / Action */}
        <div className="relative z-10 mt-8 flex justify-end">
           {charIndex >= message.length && (
             <button 
               onClick={onDismiss}
               className="group bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-black py-3 px-8 flex items-center gap-2 transition-all hover:scale-105"
             >
               <Terminal className="w-5 h-5" />
               ACKNOWLEDGE & ENGAGE
               <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
             </button>
           )}
        </div>

      </div>
    </div>
  );
};