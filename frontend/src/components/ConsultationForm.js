import React, { useState } from 'react';
import axios from 'axios';
import './ConsultationForm.css';

const ConsultationForm = () => {
  const [started, setStarted] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [results, setResults] = useState({});
  const [currentAnswers, setCurrentAnswers] = useState({});
  const [loading, setLoading] = useState(false);

  // すべての可能な質問をリスト化
  const allQuestions = [
    "申請者と会社の国籍が同じです",
    "減価償却前の設備や建物が30万ドル以上財務諸表の資産に計上されています",
    "30万ドル以上で企業を買収した会社か、買収された会社です",
    "まだ十分な売り上げがなく、これまでに人件費などのランニングコストを含め、30万ドル以上支出しています",
    "会社設立のために、30万ドル以上支出しました（不動産を除く）",
    "会社の行う貿易の50％が日米間です",
    "会社の行う貿易は継続的です",
    "貿易による利益が会社の経費の80％以上をカバーしています",
    "米国拠点でEビザでマネージャー以上として認められるポジションに就きます",
    "CEOなどのオフィサーのポジションに就きます",
    "経営企画のマネージャーなど、米国拠点の経営に関わるポジションに就きます",
    "評価・雇用に責任を持つ複数のフルタイムのスタッフを部下に持つマネージャー以上のポジションに就きます",
    "米国拠点のポジションの業務に深く関連する業務の経験が2年以上あります",
    "2年以上のマネージャー経験があります",
    "マネジメントが求められるプロジェクトマネージャーなどの2年以上の経験があります",
    "理系の大学院卒で、米国拠点の技術系の業務に深く関連する3年以上の業務経験があります",
    "理系の学部卒で、米国拠点の技術系の業務に深く関連する4年以上の業務経験があります",
    "米国拠点の業務に深く関連する5年以上の業務経験があります",
    "2年以内の期間で、目的を限定した派遣理由を説明できます",
    "米国拠点の業務に深く関連する2年以上の業務経験があります",
    "アメリカ以外からアメリカへのグループ内での異動です",
    "アメリカにある子会社の売り上げの合計が25百万ドル以上です",
    "アメリカにある子会社が1,000人以上ローカル採用をしています",
    "1年間に10人以上Lビザのペティション申請をしています",
    "直近3年のうち1年以上、アメリカ以外のグループ会社に所属していました",
    "マネージャーとしての経験があります",
    "アメリカでの業務はマネージャーとみなされます",
    "アメリカでは大卒、フルタイムの部下が2名以上います",
    "specialized knowledgeがあります",
    "アメリカでの業務はspecialized knowledgeを必要とします",
    "大卒以上で、専攻内容と業務内容が一致しています",
    "大卒以上で、専攻内容と業務内容が異なりますが、実務経験が3年以上あります",
    "大卒以上ではありませんが、実務経験が(高卒は12年以上、高専卒は3年以上）あります",
    "アメリカでの活動は商用の範囲です",
    "1回の滞在期間は90日を越えます",
    "1回の滞在期間は6か月を越えません",
    "アメリカの会社に販売した装置や設備のための作業をします",
    "装置や設備の販売を示す契約書や発注書があります",
    "H-1Bビザが必要な専門性の高い作業をします",
    "研修にOJTが含まれます",
    "研修期間は18か月以内です",
    "申請者に研修に必要な英語力はあります",
    "研修内容は商用の範囲です",
    "研修期間は６か月以内です"
  ];

  const handleStart = async () => {
    setLoading(true);
    try {
      await axios.post('/api/consultation/start', {});
      setStarted(true);
      setCompleted(false);
      setResults({});
      setCurrentAnswers({});
    } catch (error) {
      console.error('診断の開始に失敗しました:', error);
      alert('診断の開始に失敗しました。もう一度お試しください。');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (question, value) => {
    setCurrentAnswers(prev => ({
      ...prev,
      [question]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // すべての回答をバックエンドに送信
      for (const [key, value] of Object.entries(currentAnswers)) {
        const response = await axios.post('/api/consultation/answer', {
          key,
          value
        });

        // 推論が完了した場合
        if (response.data.status === 'completed') {
          setResults(response.data.results);
          setCompleted(true);
          break;
        }
      }

      // まだ完了していない場合、statusを確認
      if (!completed) {
        const statusResponse = await axios.get('/api/consultation/status');
        if (Object.keys(statusResponse.data.hypotheses).length > 0) {
          setResults(statusResponse.data.hypotheses);
          setCompleted(true);
        }
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
      setCurrentAnswers({});
    } catch (error) {
      console.error('リセットに失敗しました:', error);
      alert('リセットに失敗しました。もう一度お試しください。');
    } finally {
      setLoading(false);
    }
  };

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

  if (completed) {
    const visaResults = Object.entries(results).filter(([key]) =>
      key.includes('ビザでの申請ができます') || key.includes('ビザの申請ができます')
    );

    return (
      <div className="consultation-container">
        <div className="result-card">
          <h2>診断結果</h2>
          {visaResults.length > 0 ? (
            <>
              <p className="result-intro">以下のビザ申請が可能です：</p>
              <ul className="visa-list">
                {visaResults.map(([visa], index) => (
                  <li key={index} className="visa-item">
                    <span className="visa-icon">✓</span>
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

  return (
    <div className="consultation-container">
      <div className="question-card">
        <h2>質問に答えてください</h2>
        <p className="question-intro">
          該当する項目すべてに「はい」を選択してください。
        </p>
        <form onSubmit={handleSubmit}>
          <div className="questions-list">
            {allQuestions.map((question, index) => (
              <div key={index} className="question-item">
                <label className="question-label">
                  <span className="question-text">{question}</span>
                  <div className="question-options">
                    <label className="radio-label">
                      <input
                        type="radio"
                        name={question}
                        value="true"
                        checked={currentAnswers[question] === true}
                        onChange={() => handleAnswerChange(question, true)}
                      />
                      <span>はい</span>
                    </label>
                    <label className="radio-label">
                      <input
                        type="radio"
                        name={question}
                        value="false"
                        checked={currentAnswers[question] === false}
                        onChange={() => handleAnswerChange(question, false)}
                      />
                      <span>いいえ</span>
                    </label>
                  </div>
                </label>
              </div>
            ))}
          </div>
          <div className="form-actions">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || Object.keys(currentAnswers).length === 0}
            >
              {loading ? '診断中...' : '診断結果を見る'}
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleReset}
              disabled={loading}
            >
              リセット
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ConsultationForm;
