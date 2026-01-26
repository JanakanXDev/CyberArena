import React, { useEffect, useRef, useState } from 'react';
import { GameState } from '../../types/game';
import { Activity, ShieldCheck, AlertTriangle, Brain, HelpCircle } from 'lucide-react';
import { ActionPanel } from '../game/ActionPanel';
import { StatusHUD } from '../game/StatusHUD';
import { EventLog } from '../game/EventLog';
import { SystemView } from '../game/SystemView';
import { MentorPanel } from '../game/MentorPanel';

interface DashboardProps {
  state: GameState;
  onAction: (actionId: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ state, onAction }) => {
  console.log('Dashboard rendering with state:', {
    actionsCount: state.availableActions?.length || 0,
    hypothesesCount: state.hypotheses?.length || 0,
    logsCount: state.logs?.length || 0,
    turnCount: state.turnCount
  });
  
  const systemViewRef = useRef<HTMLDivElement>(null);
  const eventLogRef = useRef<HTMLDivElement>(null);
  const [mentorEnabled, setMentorEnabled] = useState(false);
  const [showMentorModal, setShowMentorModal] = useState(false);
  const [mentorAnalysis, setMentorAnalysis] = useState<any>(null);

  // Auto-scroll logs
  useEffect(() => {
    systemViewRef.current?.scrollTo({
      top: systemViewRef.current.scrollHeight,
      behavior: 'smooth'
    });
    eventLogRef.current?.scrollTo({
      top: eventLogRef.current.scrollHeight,
      behavior: 'smooth'
    });
  }, [state.logs]);

  if (!state) {
    console.error('Dashboard: No state provided!');
    return (
      <div className="bg-black text-emerald-500 p-10 font-mono text-center">
        SYSTEM OFFLINE - No state
      </div>
    );
  }

  // Debug: Show if actions are empty
  if (!state.availableActions || state.availableActions.length === 0) {
    console.warn('Dashboard: No actions available!', state);
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
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest">
            {state.scenarioName}
          </div>
          <div className="h-4 w-px bg-slate-700 mx-2" />
          <div className="text-xs font-bold text-slate-500">
            Turn {state.turnCount}
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={async () => {
              try {
                const { api } = await import('../../api/client');
                // Request mentor analysis
                const analysis = await api.getMentorAnalysis();
                setMentorAnalysis(analysis);
                setShowMentorModal(true);
                // Enable mentor for continuous guidance
                const result = await api.toggleMentor();
                setMentorEnabled(result.enabled);
              } catch (error) {
                console.error('Failed to get mentor analysis:', error);
              }
            }}
            className="flex items-center gap-2 px-3 py-1.5 rounded text-xs font-bold uppercase tracking-widest transition-colors bg-emerald-600 hover:bg-emerald-500 text-white border border-emerald-500 hover:border-emerald-400 shadow-lg hover:shadow-emerald-500/50"
          >
            <Brain className="w-3 h-3" />
            Ask Mentor
          </button>
        </div>
      </header>

      {/* Four-Zone Layout */}
      <div className="flex-1 grid grid-cols-12 grid-rows-2 gap-0 overflow-hidden">
        {/* Zone 1: System View (Top Left) - Partial and noisy signals */}
        <div className="col-span-7 row-span-1 border-r border-b border-slate-800 bg-black relative overflow-hidden">
          <div className="absolute top-0 left-0 bg-slate-900 text-[10px] text-slate-400 font-bold px-3 py-1 uppercase tracking-wider rounded-br z-10">
            System View
          </div>
          <SystemView
            ref={systemViewRef}
            logs={systemLogs}
            components={state.systemComponents}
            vulnerabilities={state.vulnerabilities}
          />
        </div>

        {/* Zone 2: Action Panel (Top Right) - Hypothesis-based actions */}
        <div className="col-span-5 row-span-1 border-b border-slate-800 bg-[#161618] relative overflow-hidden">
          <div className="absolute top-0 left-0 bg-slate-800 text-[10px] text-slate-400 font-bold px-3 py-1 uppercase tracking-wider rounded-br z-10">
            Actions
          </div>
          <ActionPanel
            actions={state.availableActions}
            hypotheses={state.hypotheses}
            onAction={onAction}
          />
        </div>

        {/* Zone 3: State Panel (Bottom Left) - Risk, detection, integrity, AI aggressiveness */}
        <div className="col-span-7 row-span-1 border-r border-slate-800 bg-[#0f0f11] relative overflow-hidden">
          <div className="absolute top-0 left-0 bg-slate-900 text-[10px] text-slate-400 font-bold px-3 py-1 uppercase tracking-wider rounded-br z-10">
            State Panel
          </div>
          <StatusHUD
            riskScore={state.riskScore}
            detectionLevel={state.detectionLevel}
            integrity={state.integrity}
            aiAggressiveness={state.aiAggressiveness}
            userAssumptions={state.userAssumptions}
            contradictions={state.contradictions}
          />
        </div>

        {/* Zone 4: Event Log (Bottom Right) - Cause-effect traces */}
        <div className="col-span-5 row-span-1 border-slate-800 bg-[#111] relative overflow-hidden">
          <div className="absolute top-0 left-0 bg-slate-800 text-[10px] text-slate-400 font-bold px-3 py-1 uppercase tracking-wider rounded-br z-10">
            Event Log
          </div>
          <EventLog ref={eventLogRef} logs={eventLogs} actionHistory={state.actionHistory} />
        </div>
      </div>

      {/* Mentor Modal (shown when requested) */}
      {showMentorModal && mentorAnalysis && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#1a1a1c] border border-emerald-500/30 rounded-lg shadow-2xl w-full max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
            <MentorPanel 
              guidance={mentorAnalysis} 
              onClose={() => {
                setShowMentorModal(false);
                setMentorAnalysis(null);
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};
