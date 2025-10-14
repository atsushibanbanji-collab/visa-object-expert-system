import React, { useState } from 'react';
import axios from 'axios';
import './ConsultationForm.css';

const ConsultationForm = () => {
  const [started, setStarted] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [results, setResults] = useState({});
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [questionHistory, setQuestionHistory] = useState([]);

  const handleStart = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/consultation/start', {});
      setStarted(true);
      setCompleted(false);
      setResults({});
      setQuestionHistory([]);

      if (response.data.status === 'need_input') {
        setCurrentQuestion(response.data.question);
      } else if (response.data.status === 'completed') {
        setResults(response.data.results);
        setCompleted(true);
      }
    } catch (error) {
      console.error('診断の開始に失敗しました:', error);
      alert('診断の開始に失敗しました。もう一度お試しください。');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = async (answer) => {
    setLoading(true);

    // 質問と回答を履歴に追加
    setQuestionHistory(prev => [...prev, { question: currentQuestion, answer }]);

    try {
      // 回答をバックエンドに送信
      const response = await axios.post('/api/consultation/answer', {
        key: currentQuestion,
        value: answer
      });

      // 次の質問または結果を処理
      if (response.data.status === 'need_input') {
        setCurrentQuestion(response.data.question);
      } else if (response.data.status === 'completed') {
        setResults(response.data.results);
        setCompleted(true);
        setCurrentQuestion('');
      }
    } catch (error) {
      console.error('回答の送信に失敗しました:', error);
      alert('回答の送信に失敗しました。もう一度お試しください。');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    setLoading(true);
    try {
      await axios.post('/api/consultation/reset');
      setStarted(false);
      setCompleted(false);
      setResults({});
      setCurrentQuestion('');
      setQuestionHistory([]);
    } catch (error) {
      console.error('リセットに失敗しました:', error);
      alert('リセットに失敗しました。もう一度お試しください。');
    } finally {
      setLoading(false);
    }
  };

  // 開始画面
  if (!started) {
    return (
      <div className="consultation-container">
        <div className="welcome-card">
          <h2>ビザ診断を開始します</h2>
          <p>
            このエキスパートシステムは、あなたの状況に基づいて最適な米国ビザの種類を診断します。
          </p>
          <p>
            いくつかの質問に「はい」または「いいえ」で答えてください。
          </p>
          <p className="note">
            ※ 最小限の質問数で診断を行います
          </p>
          <button
            className="btn btn-primary btn-large"
            onClick={handleStart}
            disabled={loading}
          >
            {loading ? '開始中...' : '診断を開始'}
          </button>
        </div>
      </div>
    );
  }

  // 結果画面
  if (completed) {
    const visaResults = Object.entries(results).filter(([key]) =>
      key.includes('ビザでの申請ができます') || key.includes('ビザの申請ができます')
    );

    return (
      <div className="consultation-container">
        <div className="result-card">
          <h2>診断結果</h2>

          {/* 質問履歴サマリー */}
          <div className="summary-section">
            <p className="summary-text">
              <strong>{questionHistory.length}個</strong>の質問に回答しました
            </p>
          </div>

          {visaResults.length > 0 ? (
            <>
              <p className="result-intro">以下のビザ申請が可能です：</p>
              <ul className="visa-list">
                {visaResults.map(([visa], index) => (
                  <li key={index} className="visa-item">
                    <span className="visa-icon">✓</span>
                    <span className="visa-text">{visa}</span>
                  </li>
                ))}
              </ul>
            </>
          ) : (
            <p className="no-result">
              現在の条件では、該当するビザが見つかりませんでした。
              条件を見直すか、専門家にご相談ください。
            </p>
          )}

          {/* 回答履歴の詳細 */}
          {questionHistory.length > 0 && (
            <details className="history-details">
              <summary className="history-summary">回答履歴を表示</summary>
              <div className="history-list">
                {questionHistory.map((item, index) => (
                  <div key={index} className="history-item">
                    <div className="history-question">Q{index + 1}: {item.question}</div>
                    <div className={`history-answer ${item.answer ? 'yes' : 'no'}`}>
                      A: {item.answer ? 'はい' : 'いいえ'}
                    </div>
                  </div>
                ))}
              </div>
            </details>
          )}

          <div className="result-actions">
            <button
              className="btn btn-secondary"
              onClick={handleReset}
              disabled={loading}
            >
              もう一度診断する
            </button>
          </div>
        </div>
      </div>
    );
  }

  // 質問画面
  return (
    <div className="consultation-container">
      <div className="question-card">
        <div className="progress-indicator">
          <span className="progress-count">質問 {questionHistory.length + 1}</span>
        </div>

        <h2>{currentQuestion}</h2>

        <div className="answer-buttons">
          <button
            className="btn btn-answer btn-yes"
            onClick={() => handleAnswer(true)}
            disabled={loading}
          >
            はい
          </button>
          <button
            className="btn btn-answer btn-no"
            onClick={() => handleAnswer(false)}
            disabled={loading}
          >
            いいえ
          </button>
        </div>

        {loading && (
          <div className="loading-message">
            推論中...
          </div>
        )}

        {/* 回答済み質問の数を表示 */}
        {questionHistory.length > 0 && (
          <div className="answered-count">
            これまでに {questionHistory.length} 個の質問に回答しました
          </div>
        )}

        <div className="form-actions">
          <button
            className="btn btn-secondary btn-small"
            onClick={handleReset}
            disabled={loading}
          >
            最初から
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConsultationForm;
