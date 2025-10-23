import React, { useState } from 'react';
import './App.css';
import ConsultationForm from './components/ConsultationForm';
import QuestionsPage from './components/QuestionsPage';
import RuleManagementPage from './components/RuleManagementPage';
import ValidationPage from './components/ValidationPage';
import QuestionOrderPage from './components/QuestionOrderPage';

function App() {
  const [currentPage, setCurrentPage] = useState('consultation');

  const renderPage = () => {
    switch (currentPage) {
      case 'consultation':
        return <ConsultationForm />;
      case 'questions':
        return <QuestionsPage onBack={() => setCurrentPage('consultation')} />;
      case 'rules':
        return <RuleManagementPage />;
      case 'validation':
        return <ValidationPage />;
      case 'question-order':
        return <QuestionOrderPage />;
      default:
        return <ConsultationForm />;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-top">
          <div className="header-title">
            <h1>米国ビザ選定エキスパートシステム</h1>
            <p>質問に答えて、最適なビザの種類を診断します</p>
          </div>
        </div>
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
            className={`nav-btn ${currentPage === 'rules' ? 'active' : ''}`}
            onClick={() => setCurrentPage('rules')}
          >
            ルール管理
          </button>
          <button
            className={`nav-btn ${currentPage === 'validation' ? 'active' : ''}`}
            onClick={() => setCurrentPage('validation')}
          >
            検証
          </button>
          <button
            className={`nav-btn ${currentPage === 'question-order' ? 'active' : ''}`}
            onClick={() => setCurrentPage('question-order')}
          >
            質問順序管理
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
