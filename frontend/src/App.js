import React from 'react';
import './App.css';
import ConsultationForm from './components/ConsultationForm';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>米国ビザ選定エキスパートシステム</h1>
        <p>質問に答えて、最適なビザの種類を診断します</p>
      </header>
      <main className="App-main">
        <ConsultationForm />
      </main>
    </div>
  );
}

export default App;
