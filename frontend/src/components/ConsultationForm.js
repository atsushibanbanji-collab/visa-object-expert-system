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
  const [appliedRules, setAppliedRules] = useState([]);  // 適用されたルールの履歴（結果画面用）
  const [debugInfo, setDebugInfo] = useState({ findings: {}, hypotheses: {}, conflict_set: [], applied_rules: [] });  // デバッグ用の推論状態

  // 推論状態を取得する関数
  const fetchDebugInfo = async () => {
    try {
      const response = await axios.get('/api/consultation/status');
      setDebugInfo(response.data);
    } catch (error) {
      console.error('推論状態の取得に失敗しました:', error);
    }
  };

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

      // 推論状態を取得（デバッグ用）
      await fetchDebugInfo();
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

      // 推論状態を取得（デバッグ用）
      await fetchDebugInfo();
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
      setDebugInfo({ findings: {}, hypotheses: {}, conflict_set: [], applied_rules: [] });
    } catch (error) {
      console.error('リセットに失敗しました:', error);
      alert('リセットに失敗しました。もう一度お試しください。');
    } finally {
      setLoading(false);
    }
  };

  const handleGoBack = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/consultation/go_back');

      // 履歴から最後の質問を削除
      setQuestionHistory(prev => prev.slice(0, -1));

      // 次の質問または状態を処理
      if (response.data.status === 'need_input') {
        setCurrentQuestion(response.data.question);
        setCompleted(false);
        setImpossible(false);
      } else if (response.data.status === 'completed') {
        setResults(response.data.results);
        setAppliedRules(response.data.applied_rules || []);
        setCompleted(true);
        setCurrentQuestion('');
      } else if (response.data.status === 'impossible') {
        setImpossible(true);
        setCompleted(true);
        setCurrentQuestion('');
      } else if (response.data.status === 'error') {
        // これ以上戻れない場合
        alert(response.data.message);
      }

      // 推論状態を取得（デバッグ用）
      await fetchDebugInfo();
    } catch (error) {
      console.error('前の質問に戻るのに失敗しました:', error);
      alert('前の質問に戻るのに失敗しました。');
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
                <h3>申請不可</h3>
              </div>
              <p className="impossible-message">
                現在の条件では、{visaTypeNames[selectedVisaType]}の申請ができません。
                他のビザタイプを試すか、専門家にご相談ください。
              </p>
            </>
          ) : visaResults.length > 0 ? (
            <>
              <div className="success-result">
                <h3>申請可能</h3>
              </div>
              <p className="result-intro">以下のビザ申請が可能です：</p>
              <ul className="visa-list">
                {visaResults.map(([visa], index) => (
                  <li key={index} className="visa-item">
                    {visa}
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
                      <strong>条件:</strong>
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

                    <div className="inference-actions">
                      <strong>結論:</strong>
                      <ul>
                        {ruleInfo.actions.map((action, i) => (
                          <li key={i} className="action-item">
                            → {action}
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
    <div className="consultation-container split-view">
      {/* 左側：診断画面 */}
      <div className="left-panel">
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

          {/* 戻るボタン */}
          {questionHistory.length > 0 && (
            <div className="navigation-buttons">
              <button
                className="btn btn-back"
                onClick={handleGoBack}
                disabled={loading}
              >
                ← 前の質問に戻る
              </button>
              <button
                className="btn btn-reset"
                onClick={handleReset}
                disabled={loading}
              >
                最初に戻る
              </button>
            </div>
          )}

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

      {/* 右側：推論過程のリアルタイム表示 */}
      <div className="right-panel">
        <div className="debug-panel">
          <h3 className="debug-title">INFERENCE PROCESS</h3>

          {/* 評価中のルール */}
          <div className="debug-section">
            <h4 className="debug-section-title">RULES BEING EVALUATED</h4>
            <div className="debug-content">
              {(!debugInfo.conflict_set || debugInfo.conflict_set.length === 0) ? (
                <p className="debug-empty">評価中のルールがありません</p>
              ) : (
                <div className="debug-rules-list">
                  {debugInfo.conflict_set.map((ruleInfo, index) => (
                    <div key={index} className="debug-rule-item">
                      <div className="debug-rule-header">
                        <span className="debug-rule-name">ルール {ruleInfo.rule_name}</span>
                        <span className={`debug-badge ${ruleInfo.rule_type}`}>
                          {ruleInfo.rule_type}
                        </span>
                        <span className={`debug-badge logic ${ruleInfo.condition_logic}`}>
                          {ruleInfo.condition_logic}
                        </span>
                      </div>
                      <div className="debug-rule-conditions">
                        <strong>条件:</strong>
                        <ul>
                          {ruleInfo.conditions.map((condition, i) => {
                            const value = ruleInfo.satisfied_conditions[condition];
                            const hasValue = condition in ruleInfo.satisfied_conditions;
                            return (
                              <li key={i} className={hasValue ? (value ? 'true' : 'false') : 'unknown'}>
                                <span className={`debug-icon ${hasValue ? (value ? 'true' : 'false') : 'unknown'}`}>
                                  {hasValue ? (value ? '✓' : '✗') : '?'}
                                </span>
                                {condition}
                              </li>
                            );
                          })}
                        </ul>
                      </div>
                      <div className="debug-rule-actions">
                        <strong>結論:</strong>
                        <ul>
                          {ruleInfo.actions.map((action, i) => (
                            <li key={i}>→ {action}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* 適用されたルール */}
          <div className="debug-section">
            <h4 className="debug-section-title">APPLIED RULES</h4>
            <div className="debug-content">
              {(!debugInfo.applied_rules || debugInfo.applied_rules.length === 0) ? (
                <p className="debug-empty">まだルールが適用されていません</p>
              ) : (
                <div className="debug-rules-list">
                  {debugInfo.applied_rules.map((ruleInfo, index) => (
                    <div key={index} className="debug-rule-item">
                      <div className="debug-rule-header">
                        <span className="debug-rule-name">ルール {ruleInfo.rule_name}</span>
                        <span className={`debug-badge ${ruleInfo.rule_type}`}>
                          {ruleInfo.rule_type}
                        </span>
                        <span className={`debug-badge logic ${ruleInfo.condition_logic}`}>
                          {ruleInfo.condition_logic}
                        </span>
                      </div>
                      <div className="debug-rule-conditions">
                        <strong>条件:</strong>
                        <ul>
                          {Object.entries(ruleInfo.satisfied_conditions).map(([condition, value], i) => (
                            <li key={i} className={value ? 'true' : 'false'}>
                              <span className={`debug-icon ${value ? 'true' : 'false'}`}>
                                {value ? '✓' : '✗'}
                              </span>
                              {condition}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div className="debug-rule-actions">
                        <strong>結論:</strong>
                        <ul>
                          {ruleInfo.actions.map((action, i) => (
                            <li key={i}>→ {action}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* 作業記憶：Findings */}
          <div className="debug-section">
            <h4 className="debug-section-title">WORKING MEMORY - FACTS</h4>
            <div className="debug-content">
              {Object.keys(debugInfo.findings).length === 0 ? (
                <p className="debug-empty">まだ回答がありません</p>
              ) : (
                <ul className="debug-list">
                  {Object.entries(debugInfo.findings).map(([key, value]) => (
                    <li key={key} className={`debug-item ${value ? 'true' : 'false'}`}>
                      <span className={`debug-icon ${value ? 'true' : 'false'}`}>
                        {value ? '✓' : '✗'}
                      </span>
                      <span className="debug-text">{key}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConsultationForm;
