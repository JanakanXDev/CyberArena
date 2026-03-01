import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { MissionSelect } from './components/pages/MissionSelect';
import { GameSession } from './components/game/GameSession';
import { LearningCenter } from './components/pages/LearningCenter';

const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-slate-950 text-slate-200">
        <Routes>
          {/* Default Route: Show Mission Selection */}
          <Route path="/" element={<MissionSelect />} /> 
          
          {/* Learning Center */}
          <Route path="/learn" element={<LearningCenter />} />

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