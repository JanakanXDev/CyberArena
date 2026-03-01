import React, { useState, useRef, useEffect } from 'react';
import { api } from '../../api/client';
import { Brain, Send, X, Loader2, BookOpen } from 'lucide-react';

interface Message {
    role: 'user' | 'mentor';
    text: string;
    timestamp: Date;
}

const STARTER_PROMPTS = [
    "What should I do first?",
    "What is a hypothesis?",
    "How do I win this scenario?",
    "Why did my last action fail?",
    "What does pressure mean?",
];

interface MentorChatProps {
    onClose: () => void;
    mode?: string;
}

export const MentorChat: React.FC<MentorChatProps> = ({ onClose, mode }) => {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'mentor',
            text: mode === 'guided_simulation'
                ? "Welcome, operator. I'm your Mentor AI. This is Guided Simulation — your goal is to discover which of your beliefs about this system are TRUE. Start by testing the hypotheses in the top-right panel. Ask me anything!"
                : "Welcome. I'm your Mentor AI. Ask me anything about the simulation, what action to take, or what any term means.",
            timestamp: new Date()
        }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    const sendMessage = async (text?: string) => {
        const messageText = (text || input).trim();
        if (!messageText || isLoading) return;

        const userMsg: Message = { role: 'user', text: messageText, timestamp: new Date() };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            const result = await api.mentorChat(messageText);
            const mentorMsg: Message = { role: 'mentor', text: result.reply, timestamp: new Date() };
            setMessages(prev => [...prev, mentorMsg]);
        } catch (err: unknown) {
            // Network error = backend not reachable; otherwise backend returned an error
            const isNetworkError = err instanceof TypeError && (err.message.includes('fetch') || err.message.includes('network') || err.message.includes('Failed to fetch'));
            const fallbackText = isNetworkError
                ? "⚠️ Backend unreachable — make sure the Python server is running on port 5000. (Tip: run `python -m app` in the backend folder.)"
                : "⚠️ Mentor AI hit an error. Ollama may be down or overloaded — but the game continues normally. Try: 'What should I do next?'";
            setMessages(prev => [...prev, {
                role: 'mentor',
                text: fallbackText,
                timestamp: new Date()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-[#0d0d10] text-slate-200 font-mono">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 bg-[#111] border-b border-slate-800 shrink-0">
                <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-full bg-emerald-900/60 border border-emerald-500/40 flex items-center justify-center">
                        <Brain className="w-4 h-4 text-emerald-400" />
                    </div>
                    <div>
                        <div className="text-xs font-bold text-emerald-400 uppercase tracking-widest">Mentor AI</div>
                        <div className="text-[10px] text-slate-500">Ask me anything</div>
                    </div>
                </div>
                <button
                    onClick={onClose}
                    className="p-1 text-slate-500 hover:text-slate-200 transition-colors"
                >
                    <X className="w-4 h-4" />
                </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 min-h-0">
                {messages.map((msg, i) => (
                    <div key={i} className={`flex items-start gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                        {msg.role === 'mentor' && (
                            <div className="w-6 h-6 rounded-full bg-emerald-900/60 border border-emerald-500/30 flex items-center justify-center shrink-0 mt-0.5">
                                <Brain className="w-3 h-3 text-emerald-400" />
                            </div>
                        )}
                        <div className={`max-w-[85%] px-3 py-2 rounded-lg text-xs leading-relaxed ${msg.role === 'mentor'
                            ? 'bg-[#1a2a1a] border border-emerald-900/40 text-emerald-100'
                            : 'bg-slate-800 border border-slate-700 text-slate-200'
                            }`}>
                            {msg.text}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex items-center gap-3">
                        <div className="w-6 h-6 rounded-full bg-emerald-900/60 border border-emerald-500/30 flex items-center justify-center">
                            <Brain className="w-3 h-3 text-emerald-400" />
                        </div>
                        <div className="flex items-center gap-1.5 px-3 py-2 bg-[#1a2a1a] border border-emerald-900/40 rounded-lg">
                            <Loader2 className="w-3 h-3 text-emerald-500 animate-spin" />
                            <span className="text-xs text-emerald-500">Thinking...</span>
                        </div>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            {/* Quick prompts */}
            <div className="px-4 py-2 border-t border-slate-900 flex flex-wrap gap-2 shrink-0">
                {STARTER_PROMPTS.map(prompt => (
                    <button
                        key={prompt}
                        onClick={() => sendMessage(prompt)}
                        disabled={isLoading}
                        className="text-[10px] px-2 py-1 bg-slate-800/60 hover:bg-slate-700 border border-slate-700 hover:border-emerald-600 text-slate-400 hover:text-emerald-400 rounded transition-all disabled:opacity-50"
                    >
                        {prompt}
                    </button>
                ))}
            </div>

            {/* Input */}
            <div className="px-4 py-3 border-t border-slate-800 flex items-center gap-2 shrink-0">
                <input
                    ref={inputRef}
                    type="text"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && sendMessage()}
                    placeholder="Ask the Mentor anything..."
                    disabled={isLoading}
                    className="flex-1 bg-[#161618] border border-slate-700 focus:border-emerald-500 rounded px-3 py-2 text-xs text-slate-200 placeholder-slate-600 outline-none transition-colors disabled:opacity-50"
                />
                <button
                    onClick={() => sendMessage()}
                    disabled={isLoading || !input.trim()}
                    className="p-2 bg-emerald-700 hover:bg-emerald-600 disabled:bg-slate-800 disabled:text-slate-600 text-white rounded transition-colors"
                >
                    <Send className="w-3.5 h-3.5" />
                </button>
            </div>
        </div>
    );
};
