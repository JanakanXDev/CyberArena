import React, { useEffect, useRef, useState } from 'react';
import { GameState } from '../../types/game';
import { Brain, MessageSquare } from 'lucide-react';
import { ActionPanel } from '../game/ActionPanel';
import { StatusHUD } from '../game/StatusHUD';
import { EventLog } from '../game/EventLog';
import { SystemView } from '../game/SystemView';
import { MentorChat } from '../game/MentorChat';

interface DashboardProps {
  state: GameState;
  onAction: (actionId: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ state, onAction }) => {
  const systemViewRef = useRef<HTMLDivElement>(null);
  const eventLogRef = useRef<HTMLDivElement>(null);
  const [showMentorChat, setShowMentorChat] = useState(false);

  // Auto-scroll logs
  useEffect(() => {
    systemViewRef.current?.scrollTo({ top: systemViewRef.current.scrollHeight, behavior: 'smooth' });
    eventLogRef.current?.scrollTo({ top: eventLogRef.current.scrollHeight, behavior: 'smooth' });
  }, [state.logs]);

  if (!state) {
    return <div className="bg-black text-emerald-500 p-10 font-mono text-center">SYSTEM OFFLINE - No state</div>;
  }

  const systemLogs = state.logs.filter(l => l.category === 'system_view');
  const eventLogs = state.logs.filter(l => l.category === 'event_log');

  return (
    <div className="h-screen bg-[#0a0a0a] text-slate-300 font-mono flex flex-col overflow-hidden">
      {/* Header */}
      <header className="h-14 border-b border-slate-800 bg-[#111] flex items-center justify-between px-6 z-20 shrink-0">
        <div className="flex items-center gap-4">
          <div className="text-emerald-500 font-black text-lg tracking-tight">
            CYBER<span className="text-white">ARENA</span>
          </div>
          <div className="h-4 w-px bg-slate-700 mx-2" />
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest">{state.scenarioName}</div>
          <div className="h-4 w-px bg-slate-700 mx-2" />
          <div className="text-xs font-bold text-slate-500">Turn {state.turnCount}</div>
          {state.scenarioState && state.scenarioState !== 'active' && (
            <>
              <div className="h-4 w-px bg-slate-700 mx-2" />
              <div className={`text-xs font-bold uppercase tracking-widest px-2 py-0.5 rounded ${state.scenarioState === 'victory'
                ? 'bg-emerald-900/40 text-emerald-400 border border-emerald-500/40'
                : 'bg-red-900/40 text-red-400 border border-red-500/40'
                }`}>
                {state.scenarioState}
              </div>
            </>
          )}
        </div>

        {/* Mentor Chat Button — prominent for learners */}
        <button
          onClick={() => setShowMentorChat(v => !v)}
          className={`flex items-center gap-2 px-4 py-2 rounded text-xs font-bold uppercase tracking-widest transition-all ${showMentorChat
            ? 'bg-emerald-600 text-white border border-emerald-400 shadow-lg shadow-emerald-500/30'
            : 'bg-slate-800 hover:bg-emerald-900/40 text-emerald-400 border border-emerald-700 hover:border-emerald-500'
            }`}
        >
          <MessageSquare className="w-3.5 h-3.5" />
          Ask Mentor
          {!showMentorChat && (
            <span className="ml-1 w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
          )}
        </button>
      </header>

      {/* Main Content + Mentor Sidebar */}
      <div className="flex-1 flex overflow-hidden">

        {/* Simulation Grid — always full width */}
        <div className="flex-1 grid grid-cols-12 grid-rows-2 gap-0 overflow-hidden">
          {/* Zone 1: System View (Top Left) */}
          <div className="col-span-7 row-span-1 border-r border-b border-slate-800 bg-black relative overflow-hidden">
            <div className="absolute top-0 left-0 bg-slate-900 text-[10px] text-slate-400 font-bold px-3 py-1 uppercase tracking-wider rounded-br z-10">
              System View
            </div>
            <SystemView ref={systemViewRef} logs={systemLogs} components={state.systemComponents} />
          </div>

          {/* Zone 2: Action Panel (Top Right) */}
          <div className="col-span-5 row-span-1 border-b border-slate-800 bg-[#161618] relative overflow-hidden flex flex-col">
            <div className="absolute top-0 left-0 right-0 flex items-center justify-between bg-slate-800 text-[10px] text-slate-400 font-bold px-3 py-1 z-20">
              <span className="uppercase tracking-wider">Actions &amp; Hypotheses</span>
              {state.mode === 'guided_simulation' && (
                <span className="text-purple-400 text-[9px]">Test hypotheses first → unlock actions</span>
              )}
            </div>
            <div className="pt-6 h-full">
              <ActionPanel
                actions={state.availableActions}
                hypotheses={state.hypotheses}
                actionHistory={state.actionHistory}
                onAction={onAction}
              />
            </div>
          </div>

          {/* Zone 3: State Panel (Bottom Left) */}
          <div className="col-span-7 row-span-1 border-r border-slate-800 bg-[#0f0f11] relative overflow-hidden">
            <div className="absolute top-0 left-0 bg-slate-900 text-[10px] text-slate-400 font-bold px-3 py-1 uppercase tracking-wider rounded-br z-10">
              State Signals
            </div>
            <StatusHUD
              pressure={state.pressure}
              stability={state.stability}
              userAssumptions={state.userAssumptions}
              contradictions={state.contradictions}
              systemConditions={state.systemConditions}
              sessionStatus={state.sessionStatus}
              reflectionSummary={state.reflectionSummary}
            />
          </div>

          {/* Zone 4: Event Log (Bottom Right) */}
          <div className="col-span-5 row-span-1 border-slate-800 bg-[#111] relative overflow-hidden">
            <div className="absolute top-0 left-0 bg-slate-800 text-[10px] text-slate-400 font-bold px-3 py-1 uppercase tracking-wider rounded-br z-10">
              Event Log
            </div>
            <EventLog ref={eventLogRef} logs={eventLogs} actionHistory={state.actionHistory} />
          </div>
        </div>

        {/* Mentor Chat — fixed overlay, does not shrink the grid */}
        {showMentorChat && (
          <div className="fixed top-14 right-0 bottom-0 w-80 border-l border-slate-800 bg-[#0d0d10] flex flex-col z-50 shadow-2xl shadow-black/60">
            <MentorChat onClose={() => setShowMentorChat(false)} mode={state.mode} />
          </div>
        )}
      </div>

      {/* Strategic Debrief Overlay (Victory/Defeat) */}
      {state.strategicDebrief && (
        <div className="fixed inset-0 bg-black/90 backdrop-blur-md z-[100] flex items-center justify-center p-4">
          <div className="bg-[#111] border-2 border-slate-700 rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col">
            <div className={`p-6 border-b-2 ${state.strategicDebrief.outcome === 'victory' ? 'bg-emerald-900/40 border-emerald-500/50' : 'bg-red-900/40 border-red-500/50'}`}>
              <h2 className={`text-3xl font-black uppercase tracking-widest ${state.strategicDebrief.outcome === 'victory' ? 'text-emerald-400' : 'text-red-400'}`}>
                {state.strategicDebrief.outcome === 'victory' ? '⬡ Mission Victory' : '⬢ Mission Defeat'}
              </h2>
              <p className="text-slate-300 mt-2 text-sm">{state.strategicDebrief.summary}</p>
            </div>
            <div className="p-6 grid grid-cols-2 gap-6 bg-[#0a0a0c]">
              <div className="space-y-4">
                <div>
                  <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Turns Survived</div>
                  <div className="text-xl text-slate-200 font-bold">{state.strategicDebrief.turns}</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Final Pressure</div>
                  <div className={`text-xl font-bold ${state.strategicDebrief.final_pressure > 70 ? 'text-red-400' : 'text-slate-200'}`}>{state.strategicDebrief.final_pressure}%</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">System Stability</div>
                  <div className={`text-xl font-bold ${state.strategicDebrief.final_stability < 30 ? 'text-red-400' : 'text-emerald-400'}`}>{state.strategicDebrief.final_stability}%</div>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">AI Final Posture</div>
                  <div className="text-xl capitalize text-slate-200 font-bold">{state.strategicDebrief.ai_end_posture}</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">AI Entropy</div>
                  <div className="text-xl text-slate-200 font-bold">{state.strategicDebrief.final_ai_entropy}%</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Core Hypotheses Solved</div>
                  <div className="text-xl text-emerald-400 font-bold">
                    {state.strategicDebrief.hypotheses_validated} / {state.strategicDebrief.hypotheses_validated + state.strategicDebrief.hypotheses_invalidated}
                  </div>
                </div>
              </div>
            </div>
            <div className="p-4 bg-black border-t border-slate-800 flex justify-end gap-3">
              <button
                onClick={() => window.location.href = '/'}
                className="px-6 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 uppercase tracking-widest text-xs font-bold rounded transition-colors border border-slate-700 hover:border-slate-500"
              >
                Return to Menu
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
