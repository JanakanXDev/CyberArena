import React, { useEffect, useRef } from 'react';
import { GameState, GameEvent } from './types/game';

interface DashboardProps {
  state: GameState | null;
  actions: string[];
  onAction: (action: string) => void;
}

const ACTION_MAP: Record<string, { label: string; category: string; danger?: boolean }> = {
  // RECON
  'analyze_logs': { label: 'Analyze Application Logs', category: 'DIAGNOSIS' },
  'check_waf': { label: 'Check WAF Status', category: 'DIAGNOSIS', danger: true },
  'hypothesis_blind_sqli': { label: 'Hypothesis: Blind SQL Injection', category: 'HYPOTHESIS' },
  'hypothesis_waf': { label: 'Hypothesis: WAF False Positive', category: 'HYPOTHESIS', danger: true },

  // ATTACK
  'low_and_slow': { label: 'Execute "Low & Slow" Extraction', category: 'EXPLOITATION' },
  'aggressive_dump': { label: 'Execute Aggressive Dump (UNION)', category: 'EXPLOITATION', danger: true },

  // DEFENSE
  'prepared_statements': { label: 'Implement Prepared Statements', category: 'REMEDIATION' },
  'waf_rule': { label: 'Apply WAF Blocking Rule', category: 'REMEDIATION', danger: true },
};

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column' as const,
    height: '100vh',
    backgroundColor: '#050a10',
    color: '#cbd5e1',
    fontFamily: '"Fira Code", monospace',
    overflow: 'hidden',
  },
  header: {
    padding: '15px 20px',
    borderBottom: '1px solid #1e293b',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#0f172a',
  },
  main: {
    display: 'flex',
    flex: 1,
    minHeight: 0, // Critical for internal scrolling
    padding: '20px',
    gap: '20px',
  },
  panel: {
    display: 'flex',
    flexDirection: 'column' as const,
    backgroundColor: '#0f172a',
    border: '1px solid #1e293b',
    borderRadius: '4px',
    overflow: 'hidden',
  },
  panelHeader: {
    padding: '10px 15px',
    backgroundColor: '#1e293b',
    color: '#64748b',
    fontSize: '0.8em',
    textTransform: 'uppercase' as const,
    letterSpacing: '1px',
    fontWeight: 'bold',
  },
  scrollArea: {
    flex: 1,
    overflowY: 'auto' as const,
    padding: '15px',
    minHeight: 0, // Critical
  },
  button: {
    display: 'block',
    width: '100%',
    padding: '12px',
    marginBottom: '10px',
    backgroundColor: 'transparent',
    border: '1px solid #334155',
    color: '#94a3b8',
    cursor: 'pointer',
    textAlign: 'left' as const,
    fontFamily: 'inherit',
    transition: 'all 0.2s',
  },
  eventItem: {
    marginBottom: '15px',
    paddingBottom: '15px',
    borderBottom: '1px solid #1e293b',
  },
  tag: {
    display: 'inline-block',
    padding: '2px 6px',
    fontSize: '0.7em',
    borderRadius: '2px',
    marginRight: '8px',
    fontWeight: 'bold',
  }
};

const getEventColor = (type: string) => {
  switch (type) {
    case 'SUCCESS': return '#10b981';
    case 'FAILURE': return '#ef4444';
    case 'WARNING': return '#f59e0b';
    case 'LESSON': return '#3b82f6';
    default: return '#94a3b8';
  }
};

export const Dashboard: React.FC<DashboardProps> = ({ state, actions, onAction }) => {
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [state?.events]);

  if (!state) return <div style={styles.container}>Loading System...</div>;

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <span style={{ fontSize: '1.2em', fontWeight: 'bold', color: '#10b981' }}>CYBER ARENA 2.0</span>
          <span style={{ fontSize: '0.9em', color: '#64748b' }}>// OPERATION: ECHO CHAMBER</span>
        </div>
        <div style={{ display: 'flex', gap: '20px', fontSize: '0.9em' }}>
          <div>PHASE: <span style={{ color: '#f59e0b' }}>{state.phase}</span></div>
          <div>RISK: <span style={{ color: state.risk_score > 2 ? '#ef4444' : '#10b981' }}>{state.risk_score.toFixed(1)}</span></div>
        </div>
      </header>

      <main style={styles.main}>
        {/* Left Panel: Notebook / Actions */}
        <div style={{ ...styles.panel, flex: 1 }}>
          <div style={styles.panelHeader}>Command Module</div>
          <div style={styles.scrollArea}>
            <h4 style={{ marginTop: 0, color: '#e2e8f0' }}>Command Actions</h4>
            {Object.keys(ACTION_MAP).map(actionKey => {
                const meta = ACTION_MAP[actionKey];
                const isUnlocked = actions.includes(actionKey);

                return (
                  <button
                    key={actionKey}
                    onClick={() => isUnlocked && onAction(actionKey)}
                    disabled={!isUnlocked}
                    style={{
                      ...styles.button,
                      borderColor: isUnlocked
                          ? (meta.category === 'HYPOTHESIS' ? '#3b82f6' : '#334155')
                          : '#1e293b',
                      color: isUnlocked
                          ? (meta.danger ? '#f87171' : '#e2e8f0')
                          : '#334155',
                      cursor: isUnlocked ? 'pointer' : 'not-allowed',
                      opacity: isUnlocked ? 1 : 0.6,
                      background: isUnlocked ? 'transparent' : 'rgba(15, 23, 42, 0.5)'
                    }}
                    onMouseOver={(e) => {
                        if (isUnlocked) {
                            e.currentTarget.style.backgroundColor = '#1e293b';
                            e.currentTarget.style.borderColor = '#64748b';
                        }
                    }}
                    onMouseOut={(e) => {
                        if (isUnlocked) {
                            e.currentTarget.style.backgroundColor = 'transparent';
                            e.currentTarget.style.borderColor = meta.category === 'HYPOTHESIS' ? '#3b82f6' : '#334155';
                        }
                    }}
                  >
                    <div style={{ fontSize: '0.7em', color: isUnlocked ? '#64748b' : '#1e293b', marginBottom: '4px' }}>
                        [{isUnlocked ? meta.category : 'LOCKED'}]
                    </div>
                    {meta.label}
                    {!isUnlocked && <span style={{ float: 'right', fontSize: '1.2em' }}>🔒</span>}
                  </button>
                );
            })}
          </div>
        </div>

        {/* Right Panel: Logs & Events */}
        <div style={{ ...styles.panel, flex: 2 }}>
          <div style={styles.panelHeader}>System Monitor</div>
          <div style={styles.scrollArea}>
            {state.events.length === 0 && (
                <div style={{ color: '#64748b' }}>System initialized. Monitoring...</div>
            )}
            {state.events.map((event) => (
              <div key={event.id} style={styles.eventItem}>
                <div style={{ display: 'flex', alignItems: 'baseline', marginBottom: '5px' }}>
                    <span style={{
                        ...styles.tag,
                        backgroundColor: getEventColor(event.type) + '20', // 20% opacity
                        color: getEventColor(event.type),
                        border: `1px solid ${getEventColor(event.type)}`
                    }}>
                        {event.type}
                    </span>
                    <span style={{ fontWeight: 'bold', color: '#f1f5f9' }}>{event.title}</span>
                </div>
                <div style={{ color: '#94a3b8', lineHeight: '1.5', fontSize: '0.9em' }}>
                    {event.description}
                </div>
                {event.impact && (
                    <div style={{ marginTop: '8px', color: '#cbd5e1', fontSize: '0.85em', fontStyle: 'italic', borderLeft: '2px solid #3b82f6', paddingLeft: '10px' }}>
                        Impact: {event.impact}
                    </div>
                )}
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </div>
      </main>
    </div>
  );
};
