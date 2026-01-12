import CoreAnalyzer from './component/CoreAnalyzer.jsx'; // <-- ADD .jsx HERE


import React from 'react';
import './App.css';

function App() {
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>TriSense AI Companion</h1>
      </header>
      <main className="app-main">
        <CoreAnalyzer />
      </main>
    </div>
  );
}

export default App;
