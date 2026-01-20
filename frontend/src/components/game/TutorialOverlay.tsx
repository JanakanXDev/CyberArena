import React from 'react';

interface TutorialOverlayProps {
  visible: boolean;
  title: string;
  message: string;
  onClose: () => void;
}

export const TutorialOverlay: React.FC<TutorialOverlayProps> = ({ visible, title, message, onClose }) => {
  if (!visible) return null;

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0, 10, 20, 0.85)', zIndex: 2000,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      backdropFilter: 'blur(4px)'
    }}>
      <div style={{
        backgroundColor: '#0f172a',
        border: '1px solid #10b981',
        boxShadow: '0 0 20px rgba(16, 185, 129, 0.2)',
        padding: '24px',
        maxWidth: '600px',
        width: '90%',
        color: '#e2e8f0',
        fontFamily: '"Fira Code", monospace',
        position: 'relative'
      }}>
        <div style={{
            position: 'absolute', top: '-10px', left: '20px',
            backgroundColor: '#0f172a', padding: '0 10px',
            color: '#10b981', fontWeight: 'bold', border: '1px solid #10b981'
        }}>
            MENTOR LINK ESTABLISHED
        </div>
        <h3 style={{ color: '#10b981', marginTop: '10px', textTransform: 'uppercase', letterSpacing: '1px' }}>
            {title}
        </h3>
        <p style={{ lineHeight: '1.6', fontSize: '1.1em' }}>{message}</p>
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
            <button onClick={onClose} style={{
            backgroundColor: 'transparent',
            border: '1px solid #10b981',
            padding: '10px 24px',
            color: '#10b981',
            cursor: 'pointer',
            fontWeight: 'bold',
            textTransform: 'uppercase',
            transition: 'all 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(16, 185, 129, 0.1)'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
            >
            Acknowledge
            </button>
        </div>
      </div>
    </div>
  );
};
