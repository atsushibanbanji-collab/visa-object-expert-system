import React, { useState } from 'react';
import './App.css';
import ConsultationForm from './components/ConsultationForm';
import QuestionsPage from './components/QuestionsPage';
import FlowchartPage from './components/FlowchartPage';

function App() {
  const [currentPage, setCurrentPage] = useState('consultation');

  const renderPage = () => {
    switch (currentPage) {
      case 'consultation':
        return <ConsultationForm />;
      case 'questions':
        return <QuestionsPage onBack={() => setCurrentPage('consultation')} />;
      case 'flowchart':
        return <FlowchartPage onBack={() => setCurrentPage('consultation')} />;
      default:
        return <ConsultationForm />;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>米国ビザ選定エキスパートシステム</h1>
        <p>質問に答えて、最適なビザの種類を診断します</p>
        <nav className="App-nav">
          <button
            className={`nav-btn ${currentPage === 'consultation' ? 'active' : ''}`}
            onClick={() => setCurrentPage('consultation')}
          >
            診断
          </button>
          <button
            className={`nav-btn ${currentPage === 'questions' ? 'active' : ''}`}
            onClick={() => setCurrentPage('questions')}
          >
            質問一覧
          </button>
          <button
            className={`nav-btn ${currentPage === 'flowchart' ? 'active' : ''}`}
            onClick={() => setCurrentPage('flowchart')}
          >
            フローチャート
          </button>
        </nav>
      </header>
      <main className="App-main">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
