import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './QuestionsPage.css';

const QuestionsPage = ({ onBack }) => {
  const [questionsData, setQuestionsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedVisa, setSelectedVisa] = useState('E');

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const response = await axios.get('/api/consultation/questions');
        setQuestionsData(response.data);
        setLoading(false);
      } catch (error) {
        console.error('質問データの取得に失敗しました:', error);
        setLoading(false);
      }
    };

    fetchQuestions();
  }, []);

  if (loading) {
    return (
      <div className="questions-container">
        <div className="questions-card">
          <p>読み込み中...</p>
        </div>
      </div>
    );
  }

  if (!questionsData) {
    return (
      <div className="questions-container">
        <div className="questions-card">
          <p>データの取得に失敗しました</p>
          <button className="btn btn-secondary" onClick={onBack}>
            戻る
          </button>
        </div>
      </div>
    );
  }

  const visaData = questionsData[selectedVisa];

  return (
    <div className="questions-container">
      <div className="questions-card">
        <div className="questions-header">
          <h1>質問一覧</h1>
          <button className="btn btn-secondary btn-back" onClick={onBack}>
            ← 診断ページに戻る
          </button>
        </div>

        <div className="visa-tabs">
          {Object.keys(questionsData).map((visaType) => (
            <button
              key={visaType}
              className={`visa-tab ${selectedVisa === visaType ? 'active' : ''}`}
              onClick={() => setSelectedVisa(visaType)}
            >
              {questionsData[visaType].name}
            </button>
          ))}
        </div>

        <div className="questions-content">
          <h2>{visaData.name}</h2>

          <div className="stats">
            <div className="stat-item">
              <span className="stat-number">{visaData.rules.length}</span>
              <span className="stat-label">ルール数</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{visaData.all_questions.length}</span>
              <span className="stat-label">質問数</span>
            </div>
          </div>

          <section className="section">
            <h3>すべての質問</h3>
            <ul className="questions-list">
              {visaData.all_questions.map((question, index) => (
                <li key={index} className="question-list-item">
                  <span className="question-number">{index + 1}</span>
                  <span className="question-text">{question}</span>
                </li>
              ))}
            </ul>
          </section>

          <section className="section">
            <h3>ルール詳細</h3>
            <div className="rules-list">
              {visaData.rules.map((rule, index) => (
                <details key={index} className="rule-item">
                  <summary className="rule-summary">
                    ルール {rule.name}
                    <span className={`rule-type ${rule.type}`}>{rule.type}</span>
                  </summary>
                  <div className="rule-details">
                    <div className="rule-section">
                      <h4>
                        条件（IF）
                        <span className={`condition-logic ${rule.condition_logic}`}>
                          {rule.condition_logic}
                        </span>
                      </h4>
                      <ul>
                        {rule.conditions.map((cond, i) => (
                          <li key={i}>{cond}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="rule-section">
                      <h4>結論（THEN）</h4>
                      <ul>
                        {rule.actions.map((action, i) => (
                          <li key={i}>{action}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </details>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default QuestionsPage;
