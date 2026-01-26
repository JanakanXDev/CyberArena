import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { MissionSelect } from './components/pages/MissionSelect'; // <--- NEW IMPORT
import { GameSession } from './components/game/GameSession';

const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-slate-950 text-slate-200">
        <Routes>
          {/* Default Route: Show Mission Selection */}
          <Route path="/" element={<MissionSelect />} /> 
          
          {/* Old /learn route can also redirect to home now */}
          <Route path="/learn" element={<Navigate to="/" replace />} />

          {/* Game Route */}
          <Route path="/game" element={<GameSession />} />
          
          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;