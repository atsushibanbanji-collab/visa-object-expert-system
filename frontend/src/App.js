import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import ConsultationForm from './components/ConsultationForm';
import QuestionsPage from './components/QuestionsPage';
import RuleManagementPage from './components/RuleManagementPage';
import ValidationPage from './components/ValidationPage';

function App() {
  const [currentPage, setCurrentPage] = useState('consultation');
  const [backendReady, setBackendReady] = useState(false);
  const [backendWarming, setBackendWarming] = useState(true);

  // バックエンドのプリウォームアップ
  useEffect(() => {
    const warmUpBackend = async () => {
      console.log('🔥 Warming up backend...');
      setBackendWarming(true);

      try {
        const startTime = Date.now();
        await axios.get('/api/health', { timeout: 60000 }); // 60秒タイムアウト
        const duration = Date.now() - startTime;

        console.log(`✅ Backend ready! (${duration}ms)`);
        setBackendReady(true);
        setBackendWarming(false);
      } catch (error) {
        console.warn('⚠️ Backend warmup failed, it will start on first request:', error.message);
        // エラーでも続行（ユーザーがボタンを押したときに起動する）
        setBackendWarming(false);
      }
    };

    warmUpBackend();
  }, []);

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
          <div className="backend-status">
            {backendWarming && (
              <div className="status-badge warming">
                <span className="status-dot"></span>
                サーバー起動中...
              </div>
            )}
            {backendReady && (
              <div className="status-badge ready">
                <span className="status-dot"></span>
                準備完了
              </div>
            )}
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
        </nav>
      </header>
      <main className="App-main">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
