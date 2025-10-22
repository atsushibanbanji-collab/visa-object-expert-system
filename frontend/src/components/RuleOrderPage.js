import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './RuleOrderPage.css';

const RuleOrderPage = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [visaTypeFilter, setVisaTypeFilter] = useState('E');
  const [draggedItem, setDraggedItem] = useState(null);
  const [hasChanges, setHasChanges] = useState(false);

  // ルール一覧を取得
  const fetchRules = async () => {
    try {
      setLoading(true);
      const params = { visa_type: visaTypeFilter };
      const response = await axios.get('/api/rules', { params });
      // 優先度順にソート
      const sortedRules = response.data.sort((a, b) => a.priority - b.priority);
      setRules(sortedRules);
      setHasChanges(false);
    } catch (error) {
      console.error('ルールの取得に失敗しました:', error);
      alert('ルールの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
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

    const newRules = [...rules];
    const draggedRule = newRules[draggedItem];

    // 配列から削除して新しい位置に挿入
    newRules.splice(draggedItem, 1);
    newRules.splice(index, 0, draggedRule);

    setRules(newRules);
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
      const updates = rules.map((rule, index) => ({
        id: rule.id,
        priority: index
      }));

      // 各ルールを個別に更新
      for (const update of updates) {
        await axios.put(`/api/rules/${update.id}`, {
          priority: update.priority
        });
      }

      alert('順序を保存しました');
      setHasChanges(false);
      fetchRules();
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
      fetchRules();
    }
  };

  // 上に移動
  const moveUp = (index) => {
    if (index === 0) return;

    const newRules = [...rules];
    [newRules[index - 1], newRules[index]] = [newRules[index], newRules[index - 1]];
    setRules(newRules);
    setHasChanges(true);
  };

  // 下に移動
  const moveDown = (index) => {
    if (index === rules.length - 1) return;

    const newRules = [...rules];
    [newRules[index], newRules[index + 1]] = [newRules[index + 1], newRules[index]];
    setRules(newRules);
    setHasChanges(true);
  };

  return (
    <div className="rule-order-container">
      <div className="rule-order-header">
        <div>
          <h2>ルール順序管理</h2>
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
      ) : (
        <div className="rules-order-list">
          <div className="order-list-header">
            <span className="order-number">順序</span>
            <span className="rule-name">ルール名</span>
            <span className="rule-info">ルール情報</span>
            <span className="actions">操作</span>
          </div>
          {rules.map((rule, index) => (
            <div
              key={rule.id}
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

              <div className="rule-content">
                <div className="rule-main-info">
                  <span className="rule-name">{rule.name}</span>
                  <div className="rule-badges">
                    <span className={`badge ${rule.rule_type === '#n!' ? 'final' : 'intermediate'}`}>
                      {rule.rule_type}
                    </span>
                    <span className={`badge logic ${rule.condition_logic}`}>
                      {rule.condition_logic}
                    </span>
                  </div>
                </div>
                <div className="rule-details">
                  <span>条件: {rule.conditions.length}個</span>
                  <span>アクション: {rule.actions.length}個</span>
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
                  disabled={index === rules.length - 1}
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
          <li>ルールをドラッグ&ドロップして順序を変更</li>
          <li>↑↓ボタンでも順序を変更可能</li>
          <li>順序が小さいほど優先的に評価されます</li>
          <li>変更後は「順序を保存」ボタンで保存してください</li>
        </ul>
      </div>
    </div>
  );
};

export default RuleOrderPage;
