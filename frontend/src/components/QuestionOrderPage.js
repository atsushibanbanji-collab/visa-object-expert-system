import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './QuestionOrderPage.css';

const QuestionOrderPage = () => {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [visaTypeFilter, setVisaTypeFilter] = useState('E');
  const [draggedItem, setDraggedItem] = useState(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [initializing, setInitializing] = useState(false);

  // 質問一覧を取得
  const fetchQuestions = async () => {
    try {
      setLoading(true);
      const params = { visa_type: visaTypeFilter };
      const response = await axios.get('/api/question-priorities', { params });
      // 優先度順にソート
      const sortedQuestions = response.data.sort((a, b) => a.priority - b.priority);
      setQuestions(sortedQuestions);
      setHasChanges(false);
    } catch (error) {
      console.error('質問の取得に失敗しました:', error);
      alert('質問の取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  // 質問を初期化
  const initializeQuestions = async () => {
    if (!window.confirm('質問の優先度を初期化しますか？\n（より多くの診断結果に関連する質問が優先されます）')) {
      return;
    }

    try {
      setInitializing(true);
      const response = await axios.post(`/api/question-priorities/initialize?visa_type=${visaTypeFilter}`);
      const { added, updated, total } = response.data;

      let message = '';
      if (added > 0 && updated > 0) {
        message = `${added}個の質問を追加、${updated}個の質問を更新しました（合計: ${total}個）`;
      } else if (added > 0) {
        message = `${added}個の質問を追加しました（合計: ${total}個）`;
      } else if (updated > 0) {
        message = `${updated}個の質問を更新しました（合計: ${total}個）`;
      } else {
        message = `質問はすでに最新です（合計: ${total}個）`;
      }

      alert(message);
      fetchQuestions();
    } catch (error) {
      console.error('質問の初期化に失敗しました:', error);
      const errorMessage = error.response?.data?.detail || error.message || '不明なエラー';
      alert(`質問の初期化に失敗しました:\n${errorMessage}`);
    } finally {
      setInitializing(false);
    }
  };

  useEffect(() => {
    fetchQuestions();
  }, [visaTypeFilter]);

  // ドラッグ開始
  const handleDragStart = (e, index) => {
    setDraggedItem(index);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', e.target);
  };

  // ドラッグオーバー
  const handleDragOver = (e, index) => {
    e.preventDefault();

    if (draggedItem === null || draggedItem === index) {
      return;
    }

    const newQuestions = [...questions];
    const draggedQuestion = newQuestions[draggedItem];

    // 配列から削除して新しい位置に挿入
    newQuestions.splice(draggedItem, 1);
    newQuestions.splice(index, 0, draggedQuestion);

    setQuestions(newQuestions);
    setDraggedItem(index);
    setHasChanges(true);
  };

  // ドラッグ終了
  const handleDragEnd = () => {
    setDraggedItem(null);
  };

  // 順序を保存
  const handleSave = async () => {
    if (!hasChanges) {
      return;
    }

    setSaving(true);
    try {
      // 新しい優先度を設定
      const updates = questions.map((question, index) => ({
        id: question.id,
        priority: index
      }));

      // 各質問を個別に更新
      for (const update of updates) {
        await axios.put(`/api/question-priorities/${update.id}`, {
          id: update.id,
          priority: update.priority
        });
      }

      alert('順序を保存しました');
      setHasChanges(false);
      fetchQuestions();
    } catch (error) {
      console.error('順序の保存に失敗しました:', error);
      alert('順序の保存に失敗しました');
    } finally {
      setSaving(false);
    }
  };

  // リセット
  const handleReset = () => {
    if (!hasChanges) {
      return;
    }

    if (window.confirm('変更を破棄して元の順序に戻しますか？')) {
      fetchQuestions();
    }
  };

  // 上に移動
  const moveUp = (index) => {
    if (index === 0) return;

    const newQuestions = [...questions];
    [newQuestions[index - 1], newQuestions[index]] = [newQuestions[index], newQuestions[index - 1]];
    setQuestions(newQuestions);
    setHasChanges(true);
  };

  // 下に移動
  const moveDown = (index) => {
    if (index === questions.length - 1) return;

    const newQuestions = [...questions];
    [newQuestions[index], newQuestions[index + 1]] = [newQuestions[index + 1], newQuestions[index]];
    setQuestions(newQuestions);
    setHasChanges(true);
  };

  return (
    <div className="question-order-container">
      <div className="question-order-header">
        <div>
          <h2>質問順序管理</h2>
          <p className="subtitle">ドラッグ&ドロップまたはボタンで順序を変更できます</p>
        </div>
        <div className="header-actions">
          <select
            value={visaTypeFilter}
            onChange={(e) => setVisaTypeFilter(e.target.value)}
            className="visa-filter"
          >
            <option value="E">Eビザ</option>
            <option value="L">Lビザ</option>
            <option value="B">Bビザ</option>
            <option value="H">H-1Bビザ</option>
            <option value="J">J-1ビザ</option>
          </select>
          <button
            onClick={initializeQuestions}
            disabled={initializing}
            className="btn btn-secondary"
          >
            {initializing ? '初期化中...' : '質問を初期化'}
          </button>
          {hasChanges && (
            <>
              <button
                onClick={handleSave}
                disabled={saving}
                className="btn btn-primary"
              >
                {saving ? '保存中...' : '順序を保存'}
              </button>
              <button
                onClick={handleReset}
                disabled={saving}
                className="btn btn-secondary"
              >
                リセット
              </button>
            </>
          )}
        </div>
      </div>

      {hasChanges && (
        <div className="changes-notice">
          変更があります。保存してください。
        </div>
      )}

      {loading ? (
        <div className="loading">読み込み中...</div>
      ) : questions.length === 0 ? (
        <div className="empty-message">
          <p>質問が登録されていません。</p>
          <p>「質問を初期化」ボタンをクリックして、ルールから質問を抽出してください。</p>
        </div>
      ) : (
        <div className="questions-order-list">
          <div className="order-list-header">
            <span className="order-number">順序</span>
            <span className="question-text">質問</span>
            <span className="actions">操作</span>
          </div>
          {questions.map((question, index) => (
            <div
              key={question.id}
              className={`order-item ${draggedItem === index ? 'dragging' : ''}`}
              draggable
              onDragStart={(e) => handleDragStart(e, index)}
              onDragOver={(e) => handleDragOver(e, index)}
              onDragEnd={handleDragEnd}
            >
              <div className="drag-handle">
                <span className="drag-icon">☰</span>
                <span className="order-number">{index + 1}</span>
              </div>

              <div className="question-content">
                <div className="question-main-info">
                  <span className="question-text">{question.question}</span>
                </div>
              </div>

              <div className="move-buttons">
                <button
                  onClick={() => moveUp(index)}
                  disabled={index === 0}
                  className="btn btn-small btn-move"
                  title="上に移動"
                >
                  ↑
                </button>
                <button
                  onClick={() => moveDown(index)}
                  disabled={index === questions.length - 1}
                  className="btn btn-small btn-move"
                  title="下に移動"
                >
                  ↓
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="help-text">
        <h3>使い方</h3>
        <ul>
          <li>質問をドラッグ&ドロップして順序を変更</li>
          <li>↑↓ボタンでも順序を変更可能</li>
          <li>順序が小さいほど優先的に質問されます</li>
          <li>変更後は「順序を保存」ボタンで保存してください</li>
          <li>初回は「質問を初期化」ボタンでルールから質問を抽出してください</li>
          <li>初期化時は、より多くの診断結果（ファイナルルール）に関連する質問が優先されます</li>
        </ul>
      </div>
    </div>
  );
};

export default QuestionOrderPage;
