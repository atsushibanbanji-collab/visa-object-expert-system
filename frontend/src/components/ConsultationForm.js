import React, { useState } from 'react';
import axios from 'axios';
import './ConsultationForm.css';

const ConsultationForm = () => {
  const [selectedVisaType, setSelectedVisaType] = useState('');
  const [started, setStarted] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [results, setResults] = useState({});
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [questionHistory, setQuestionHistory] = useState([]);
  const [impossible, setImpossible] = useState(false);
  const [appliedRules, setAppliedRules] = useState([]);  // 適用されたルールの履歴

  const handleStart = async (visaType) => {
    setLoading(true);
    try {
      const response = await axios.post('/api/consultation/start', {
        visa_type: visaType
      });
      setSelectedVisaType(visaType);
      setStarted(true);
      setCompleted(false);
      setImpossible(false);
      setResults({});
      setQuestionHistory([]);

      if (response.data.status === 'need_input') {
        setCurrentQuestion(response.data.question);
      } else if (response.data.status === 'completed') {
        setResults(response.data.results);
        setAppliedRules(response.data.applied_rules || []);
        setCompleted(true);
      } else if (response.data.status === 'impossible') {
        setImpossible(true);
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
        setAppliedRules(response.data.applied_rules || []);
        setCompleted(true);
        setCurrentQuestion('');
      } else if (response.data.status === 'impossible') {
        setImpossible(true);
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
      setSelectedVisaType('');
      setStarted(false);
      setCompleted(false);
      setImpossible(false);
      setResults({});
      setCurrentQuestion('');
      setQuestionHistory([]);
      setAppliedRules([]);
    } catch (error) {
      console.error('リセットに失敗しました:', error);
      alert('リセットに失敗しました。もう一度お試しください。');
    } finally {
      setLoading(false);
    }
  };

  // ビザ選択画面
  if (!started) {
    return (
      <div className="consultation-container">
        <div className="welcome-card">
          <h2>診断するビザを選択してください</h2>
          <p>
            いくつかの質問に「はい」または「いいえ」で答えることで、
            選択したビザの申請可否を診断します。
          </p>
          <p className="note">
            ※ 最小限の質問数で診断を行います
          </p>

          <div className="visa-selection">
            <button
              className="btn btn-visa"
              onClick={() => handleStart('E')}
              disabled={loading}
            >
              <div className="visa-title">Eビザ</div>
              <div className="visa-description">投資家・貿易駐在員</div>
            </button>

            <button
              className="btn btn-visa"
              onClick={() => handleStart('L')}
              disabled={loading}
            >
              <div className="visa-title">Lビザ</div>
              <div className="visa-description">企業内転勤者</div>
            </button>

            <button
              className="btn btn-visa"
              onClick={() => handleStart('B')}
              disabled={loading}
            >
              <div className="visa-title">Bビザ</div>
              <div className="visa-description">商用・観光</div>
            </button>
          </div>

          {loading && (
            <div className="loading-message">
              <div className="loading-spinner"></div>
              <p>診断を準備しています...</p>
              <p className="loading-hint">※ 初回起動時は30秒ほどかかる場合があります</p>
            </div>
          )}
        </div>
      </div>
    );
  }

  // 結果画面
  if (completed) {
    const visaResults = Object.entries(results).filter(([key]) =>
      key.includes('ビザでの申請ができます') || key.includes('ビザの申請ができます')
    );

    const visaTypeNames = {
      'E': 'Eビザ',
      'L': 'Lビザ',
      'B': 'Bビザ'
    };

    return (
      <div className="consultation-container">
        <div className="result-card">
          <h2>診断結果</h2>

          {/* 質問履歴サマリー */}
          <div className="summary-section">
            <p className="summary-text">
              <strong>{visaTypeNames[selectedVisaType]}</strong>の診断で、
              <strong>{questionHistory.length}個</strong>の質問に回答しました
            </p>
          </div>

          {impossible ? (
            <>
              <div className="impossible-result">
                <span className="impossible-icon">✗</span>
                <h3>申請できません</h3>
              </div>
              <p className="impossible-message">
                現在の条件では、{visaTypeNames[selectedVisaType]}の申請ができません。
                他のビザタイプを試すか、専門家にご相談ください。
              </p>
            </>
          ) : visaResults.length > 0 ? (
            <>
              <div className="success-result">
                <span className="success-icon">✓</span>
                <h3>申請可能です</h3>
              </div>
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

          {/* 推論過程の詳細 */}
          {appliedRules.length > 0 && (
            <details className="inference-details">
              <summary className="inference-summary">
                推論過程を表示（適用されたルール: {appliedRules.length}個）
              </summary>
              <div className="inference-list">
                {appliedRules.map((ruleInfo, index) => (
                  <div key={index} className="inference-item">
                    <div className="inference-header">
                      <span className="inference-rule-number">ルール {ruleInfo.rule_name}</span>
                      <span className={`inference-badge ${ruleInfo.rule_type}`}>
                        {ruleInfo.rule_type === '#n!' ? '終了ルール' : '中間ルール'}
                      </span>
                      <span className={`inference-badge logic ${ruleInfo.condition_logic}`}>
                        {ruleInfo.condition_logic}
                      </span>
                    </div>

                    <div className="inference-conditions">
                      <strong>満たされた条件:</strong>
                      <ul>
                        {Object.entries(ruleInfo.satisfied_conditions).map(([condition, value], i) => (
                          <li key={i} className={value ? 'condition-true' : 'condition-false'}>
                            <span className={`condition-icon ${value ? 'true' : 'false'}`}>
                              {value ? '✓' : '✗'}
                            </span>
                            {condition}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="inference-arrow">↓</div>

                    <div className="inference-actions">
                      <strong>導出された結論:</strong>
                      <ul>
                        {ruleInfo.actions.map((action, i) => (
                          <li key={i} className="action-item">
                            <span className="action-icon">→</span>
                            {action}
                          </li>
                        ))}
                      </ul>
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
            <div className="loading-spinner"></div>
            <p>推論中...</p>
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
