import React, { useState } from 'react';
import { GameState } from '../../types/game';
import { MessageSquare } from 'lucide-react';
import { ActionPanel } from '../game/ActionPanel';
import { StatusHUD } from '../game/StatusHUD';
import { EventLog } from '../game/EventLog';
import { SystemView } from '../game/SystemView';
import { MentorChat } from '../game/MentorChat';
import { ThreatFeed } from '../game/ThreatFeed';
import { EvidenceLocker } from '../game/EvidenceLocker';

interface DashboardProps {
  state: GameState;
  onAction: (actionId: string) => void;
  isProcessing?: boolean;
}

export const Dashboard: React.FC<DashboardProps> = ({ state, onAction, isProcessing }) => {
  const [showMentorChat, setShowMentorChat] = useState(false);

  if (!state) {
    return <div className="bg-black text-emerald-500 p-10 font-mono text-center">SYSTEM OFFLINE</div>;
  }

  const systemLogs = state.logs.filter(l => l.category === 'system_view');
  const eventLogs = state.logs.filter(l => l.category === 'event_log');
  const aiPersona = (state.mode === 'defender_campaign' || state.mode === 'guided_simulation')
    ? 'attacker' : 'defender';
  const hasThreatActivity = Boolean(state.aiLastMove || (state.aiMoveHistory && state.aiMoveHistory.length > 0));

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-slate-300 font-mono">

      {/* ── Header ────────────────────────────────────────────────── */}
      <header className="border-b border-slate-800 bg-[#111] flex items-center justify-between px-6 py-3 z-20">
        <div className="flex items-center gap-4">
          <div className="text-emerald-500 font-black text-lg tracking-tight">
            CYBER<span className="text-white">ARENA</span>
          </div>
          <div className="h-4 w-px bg-slate-700" />
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest">{state.scenarioName}</div>
          <div className="h-4 w-px bg-slate-700" />
          <div className="text-xs font-bold text-slate-500">Turn {state.turnCount}</div>
          {state.beginnerLearningPath && (
            <>
              <div className="h-4 w-px bg-slate-700" />
              <div className="text-[10px] uppercase tracking-widest font-bold text-blue-300 border border-blue-500/40 bg-blue-900/20 px-2 py-0.5 rounded">
                Beginner Learning Path
              </div>
            </>
          )}
          {state.experienceMode && (
            <>
              <div className="h-4 w-px bg-slate-700" />
              <div className={`text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded border ${
                state.experienceMode === 'beginner'
                  ? 'bg-blue-900/40 text-blue-300 border-blue-500/40'
                  : state.experienceMode === 'intermediate'
                  ? 'bg-amber-900/40 text-amber-300 border-amber-500/40'
                  : 'bg-slate-900/60 text-slate-300 border-slate-600/60'
              }`}>
                {state.experienceMode}
              </div>
            </>
          )}
          {state.scenarioState && state.scenarioState !== 'active' && (
            <>
              <div className="h-4 w-px bg-slate-700" />
              <div className={`text-xs font-bold uppercase tracking-widest px-2 py-0.5 rounded ${state.scenarioState === 'victory'
                  ? 'bg-emerald-900/40 text-emerald-400 border border-emerald-500/40'
                  : 'bg-red-900/40 text-red-400 border border-red-500/40'
                }`}>
                {state.scenarioState}
              </div>
            </>
          )}
        </div>

        <button
          onClick={() => setShowMentorChat(v => !v)}
          className={`flex items-center gap-2 px-4 py-2 rounded text-xs font-bold uppercase tracking-widest transition-all ${showMentorChat
              ? 'bg-emerald-600 text-white border border-emerald-400 shadow-lg shadow-emerald-500/30'
              : 'bg-slate-800 hover:bg-emerald-900/40 text-emerald-400 border border-emerald-700 hover:border-emerald-500'
            }`}
        >
          <MessageSquare className="w-3.5 h-3.5" />
          Ask Mentor
          {!showMentorChat && <span className="ml-1 w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />}
        </button>
      </header>

      {/* ── 3-Column Body ─────────────────────────────────────────── */}
      {/*
          Col A (4/12) — System View (top) + State Signals (bottom)
          Col B (4/12) — Threat Feed (top ~35%) + Action Panel (bottom ~65%)
          Col C (4/12) — Event Log (full height)
      */}
      <div className="p-4">
      <div className="grid grid-cols-12 gap-4 items-start">

        {/* ── Col A : System Info ──────────────────────────────────── */}
        <div className="col-span-12 xl:col-span-3 flex flex-col gap-4">

          {/* System View — top half */}
          <div className="bg-black relative border border-slate-800 rounded-lg">
            <div className="absolute top-0 left-0 bg-slate-900 text-[10px] text-slate-400 font-bold px-3 py-1 uppercase tracking-wider rounded-br z-10 border-r border-b border-slate-800">
              System View
            </div>
            <SystemView logs={systemLogs} components={state.systemComponents} />
          </div>

          {/* State Signals — bottom half */}
          <div className="bg-[#0f0f11] relative border border-slate-800 rounded-lg">
            <div className="absolute top-0 left-0 bg-slate-900 text-[10px] text-slate-400 font-bold px-3 py-1 uppercase tracking-wider rounded-br z-10 border-r border-b border-slate-800">
              State Signals
            </div>
            <StatusHUD
              experienceMode={state.experienceMode}
              pressure={state.pressure}
              stability={state.stability}
              userAssumptions={state.userAssumptions}
              contradictions={state.contradictions}
              systemConditions={state.systemConditions}
              sessionStatus={state.sessionStatus}
              reflectionSummary={state.reflectionSummary}
            />
          </div>
        </div>

        {/* ── Col B : Threat Feed + Actions ───────────────────────── */}
        <div className="col-span-12 xl:col-span-6 flex flex-col gap-4">

          {/* Threat Feed — compact when idle */}
          <div className="bg-[#0d0d12] border border-slate-800 rounded-lg relative">
            <div className="absolute top-0 left-0 bg-red-900/40 text-[10px] text-red-400 font-bold px-3 py-1 uppercase tracking-wider z-10 border-r border-b border-red-800/40 rounded-br">
              ⚠ Threat Feed
            </div>
            <div className={`pt-6 px-3 pb-3 ${hasThreatActivity ? '' : 'opacity-85'}`}>
              <ThreatFeed
                aiLastMove={state.aiLastMove}
                aiMoveHistory={state.aiMoveHistory}
                aiPersona={aiPersona}
              />
            </div>
          </div>

          {/* Action Panel — takes remaining space */}
          <div className="bg-[#161618] relative border border-slate-800 rounded-lg">
            <div className="absolute top-0 left-0 right-0 flex items-center justify-between bg-slate-800 text-[10px] text-slate-400 font-bold px-3 py-1 z-20 rounded-t-lg border-b border-slate-700">
              <span className="uppercase tracking-wider">Actions & Hypotheses</span>
              {state.mode === 'guided_simulation' && (
                <span className="text-purple-400 text-[9px]">Test hypotheses → unlock actions</span>
              )}
            </div>
            <div className="pt-7 p-3 flex flex-col gap-2">
              {state.hypothesisEvaluation && (
                <div className={`mx-3 mt-2 mb-2 rounded border px-3 py-2 text-xs shrink-0 ${
                  state.hypothesisEvaluation.status === 'correct'
                    ? 'bg-emerald-950/40 border-emerald-700/60'
                    : state.hypothesisEvaluation.status === 'partial'
                    ? 'bg-amber-950/40 border-amber-700/60'
                    : 'bg-red-950/30 border-red-800/60'
                }`}>
                  <div className="flex items-center justify-between gap-2">
                    <span className="uppercase tracking-widest text-[10px] text-slate-400">
                      Hypothesis Feedback
                    </span>
                    <span className={`uppercase text-[10px] font-bold tracking-wider ${
                      state.hypothesisEvaluation.status === 'correct'
                        ? 'text-emerald-300'
                        : state.hypothesisEvaluation.status === 'partial'
                        ? 'text-amber-300'
                        : 'text-red-300'
                    }`}>
                      {state.hypothesisEvaluation.status}
                    </span>
                  </div>
                  <p className="mt-1 text-slate-200">{state.hypothesisEvaluation.feedback}</p>
                  <p className="mt-1 text-slate-400">Hint: {state.hypothesisEvaluation.hint}</p>
                </div>
              )}
              {state.beginnerLearningPath && state.beginnerStepFeedback && (
                <div className="mx-3 mb-2 rounded border border-blue-700/50 bg-blue-950/25 px-3 py-2 text-xs shrink-0">
                  <div className="uppercase tracking-widest text-[10px] text-blue-300 font-bold">
                    {state.beginnerLearningPath.title}
                  </div>
                  <p className="mt-1 text-slate-200">
                    Module {state.beginnerLearningPath.moduleIndex + 1}/{state.beginnerLearningPath.totalModules}: {state.beginnerLearningPath.currentModuleName}
                  </p>
                  <p className="mt-1 text-slate-400">Goal: {state.beginnerLearningPath.currentModuleGoal}</p>
                  <p className="mt-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">What happened</p>
                  <p className="mt-1 text-slate-300 whitespace-pre-line text-xs">{state.beginnerStepFeedback.what_happened}</p>
                  <p className="mt-3 text-[10px] font-bold uppercase tracking-wider text-slate-500">Why</p>
                  <p className="mt-1 text-slate-300 whitespace-pre-line text-xs">{state.beginnerStepFeedback.why_it_happened}</p>
                  <p className="mt-3 text-[10px] font-bold uppercase tracking-wider text-slate-500">Meaning</p>
                  <p className="mt-1 text-slate-400 whitespace-pre-line text-xs">{state.beginnerStepFeedback.what_it_means}</p>
                </div>
              )}
              <ActionPanel
                actions={state.availableActions}
                hypotheses={state.hypotheses}
                actionHistory={state.actionHistory}
                experienceMode={state.experienceMode}
                beginnerLearningPath={state.beginnerLearningPath}
                systemConditions={state.systemConditions}
                beginnerSignalsObserved={state.beginnerSignalsObserved}
                onAction={onAction}
                isProcessing={isProcessing}
              />
            </div>
          </div>

          {/* Evidence is useful, but secondary to action decision flow */}
          <div className="bg-[#101014]">
            <EvidenceLocker
              actionHistory={state.actionHistory}
              experienceMode={state.experienceMode}
            />
          </div>
        </div>

        {/* ── Col C : Event Log ───────────────────────────────────── */}
        <div className="col-span-12 xl:col-span-3 bg-[#111] relative border border-slate-800 rounded-lg xl:sticky xl:top-4">
          <div className="absolute top-0 left-0 right-0 bg-slate-800 text-[10px] text-slate-400 font-bold px-3 py-1 uppercase tracking-wider z-10 rounded-t-lg border-b border-slate-700">
            Event Log
          </div>
          <div className="pt-7">
            <EventLog logs={eventLogs} actionHistory={state.actionHistory} />
          </div>
        </div>

        {/* ── Mentor Chat overlay ──────────────────────────────────── */}
        {showMentorChat && (
          <div className="fixed top-14 right-0 bottom-0 w-80 border-l border-slate-800 bg-[#0d0d10] flex flex-col z-50 shadow-2xl shadow-black/60">
            <MentorChat onClose={() => setShowMentorChat(false)} mode={state.mode} />
          </div>
        )}
      </div>
      </div>

      {/* ── Victory / Defeat Overlay ──────────────────────────────── */}
      {state.strategicDebrief && (
        <div className="fixed inset-0 bg-black/90 backdrop-blur-md z-[100] flex items-center justify-center p-4">
          <div className="bg-[#111] border-2 border-slate-700 rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col">
            <div className={`p-6 border-b-2 flex justify-between items-start ${state.strategicDebrief.outcome === 'victory'
                ? 'bg-emerald-900/40 border-emerald-500/50'
                : 'bg-red-900/40 border-red-500/50'
              }`}>
              <div>
                <h2 className={`text-3xl font-black uppercase tracking-widest ${state.strategicDebrief.outcome === 'victory' ? 'text-emerald-400' : 'text-red-400'
                  }`}>
                  {state.strategicDebrief.outcome === 'victory' ? '⬡ Mission Victory' : '⬢ Mission Defeat'}
                </h2>
                <p className="text-slate-300 mt-2 text-sm">{state.strategicDebrief.summary}</p>
              </div>
              {state.strategicDebrief.grade && (
                <div className="text-right flex flex-col items-end">
                  <div className="text-[10px] text-slate-400 uppercase tracking-widest font-bold mb-1">Performance Grade</div>
                  <div className={`text-5xl font-black leading-none ${
                    state.strategicDebrief.grade === 'S' ? 'text-purple-400 drop-shadow-[0_0_10px_rgba(192,132,252,0.5)]' :
                    state.strategicDebrief.grade === 'A' ? 'text-emerald-400' :
                    state.strategicDebrief.grade === 'B' ? 'text-blue-400' :
                    state.strategicDebrief.grade === 'C' ? 'text-yellow-400' :
                    state.strategicDebrief.grade === 'D' ? 'text-orange-400' : 'text-red-500'
                  }`}>
                    {state.strategicDebrief.grade}
                  </div>
                  <div className="text-xs text-slate-500 font-bold tracking-wider mt-2">SCORE: {state.strategicDebrief.score}</div>
                </div>
              )}
            </div>
            
            <div className="flex flex-col md:flex-row bg-[#0a0a0c]">
              <div className="flex-1 p-6 grid grid-cols-2 gap-6 border-r border-slate-800/60">
                <div className="space-y-4">
                  <div>
                    <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Turns Survived</div>
                    <div className="text-xl text-slate-200 font-bold">{state.strategicDebrief.turns}</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Final Pressure</div>
                    <div className={`text-xl font-bold ${state.strategicDebrief.final_pressure > 70 ? 'text-red-400' : 'text-slate-200'}`}>
                      {state.strategicDebrief.final_pressure}%
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">System Stability</div>
                    <div className={`text-xl font-bold ${state.strategicDebrief.final_stability < 30 ? 'text-red-400' : 'text-emerald-400'}`}>
                      {state.strategicDebrief.final_stability}%
                    </div>
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
                    <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Core Hypotheses</div>
                    <div className="text-xl text-emerald-400 font-bold">
                      {state.strategicDebrief.hypotheses_validated} / {state.strategicDebrief.hypotheses_validated + state.strategicDebrief.hypotheses_invalidated}
                    </div>
                  </div>
                </div>
              </div>

              {state.strategicDebrief.metrics_breakdown && (
                <div className="w-[40%] p-6 flex flex-col justify-center bg-[#0d0d10]">
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 border-b border-slate-800 pb-2">Analytics Breakdown</div>
                  <div className="space-y-3">
                    {Object.entries(state.strategicDebrief.metrics_breakdown).map(([key, metric]) => (
                      <div key={key} className="flex justify-between items-center text-sm">
                        <span className="text-slate-300 font-medium">
                          {metric.label} <span className="text-slate-600 font-mono text-[9px] ml-1">[{metric.raw}]</span>
                        </span>
                        <span className={`font-mono font-bold ${'bonus' in metric ? 'text-emerald-400' : 'text-red-400'}`}>
                          {'bonus' in metric ? metric.bonus : metric.penalty}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
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
