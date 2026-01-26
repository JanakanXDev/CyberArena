import React from 'react';
import { X, BookOpen } from 'lucide-react';

interface TheoryModalProps {
  content: string;
  onClose: () => void;
}

export const TheoryModal: React.FC<TheoryModalProps> = ({ content, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-emerald-500/50 w-full max-w-2xl max-h-[80vh] rounded-xl flex flex-col shadow-2xl animate-in zoom-in duration-300">
        
        <div className="flex justify-between items-center p-6 border-b border-slate-800">
          <h2 className="text-xl font-bold text-emerald-400 flex items-center gap-2">
            <BookOpen className="w-6 h-6" /> MISSION INTEL
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-8 overflow-y-auto font-sans leading-relaxed text-slate-300 space-y-4">
          {/* Simple Markdown Rendering */}
          {content.split('\n').map((line, i) => {
            if (line.startsWith('###')) return <h3 key={i} className="text-lg font-bold text-white mt-4 mb-2">{line.replace('###', '')}</h3>;
            if (line.startsWith('**')) return <strong key={i} className="text-emerald-300 block mt-2">{line.replace(/\*\*/g, '')}</strong>;
            return <p key={i}>{line}</p>;
          })}
        </div>

        <div className="p-6 border-t border-slate-800 bg-slate-900/50 rounded-b-xl flex justify-end">
          <button 
            onClick={onClose}
            className="px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded"
          >
            ACKNOWLEDGE & CLOSE
          </button>
        </div>
      </div>
    </div>
  );
};