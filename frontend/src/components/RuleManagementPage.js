import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './RuleManagementPage.css';

const RuleManagementPage = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingRule, setEditingRule] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [visaTypeFilter, setVisaTypeFilter] = useState('E');
  const [showImportModal, setShowImportModal] = useState(false);
  const [importData, setImportData] = useState('');
  const [overwriteExisting, setOverwriteExisting] = useState(false);

  // 順序変更用のステート
  const [draggedItem, setDraggedItem] = useState(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [originalRules, setOriginalRules] = useState([]);

  // フォームの状態
  const [formData, setFormData] = useState({
    name: '',
    visa_type: 'E',
    rule_type: '#n!',
    condition_logic: 'AND',
    conditions: [''],
    actions: [''],
    priority: 0
  });

  // ルール一覧を取得
  const fetchRules = async () => {
    try {
      setLoading(true);
      const params = { visa_type: visaTypeFilter };
      const response = await axios.get('/api/rules', { params });
      setRules(response.data);
      setOriginalRules(response.data);
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

  // 新規作成フォームを開く
  const handleCreateNew = () => {
    setEditingRule(null);
    setFormData({
      name: '',
      visa_type: visaTypeFilter,
      rule_type: '#n!',
      condition_logic: 'AND',
      conditions: [''],
      actions: [''],
      priority: rules.length
    });
    setShowForm(true);
  };

  // 編集フォームを開く
  const handleEdit = (rule) => {
    setEditingRule(rule);
    setFormData({
      name: rule.name,
      visa_type: rule.visa_type,
      rule_type: rule.rule_type,
      condition_logic: rule.condition_logic,
      conditions: rule.conditions,
      actions: rule.actions,
      priority: rule.priority
    });
    setShowForm(true);
  };

  // フォームを送信
  const handleSubmit = async (e) => {
    e.preventDefault();

    // バリデーション
    if (!formData.name.trim()) {
      alert('ルール名を入力してください');
      return;
    }

    const validConditions = formData.conditions.filter(c => c.trim());
    const validActions = formData.actions.filter(a => a.trim());

    if (validConditions.length === 0) {
      alert('少なくとも1つの条件を入力してください');
      return;
    }

    if (validActions.length === 0) {
      alert('少なくとも1つのアクションを入力してください');
      return;
    }

    try {
      const payload = {
        ...formData,
        conditions: validConditions,
        actions: validActions
      };

      if (editingRule) {
        // 更新
        await axios.put(`/api/rules/${editingRule.id}`, payload);
        alert('ルールを更新しました');
      } else {
        // 新規作成
        await axios.post('/api/rules', payload);
        alert('ルールを作成しました');
      }

      setShowForm(false);
      fetchRules();
    } catch (error) {
      console.error('ルールの保存に失敗しました:', error);
      alert(error.response?.data?.detail || 'ルールの保存に失敗しました');
    }
  };

  // ルールを削除
  const handleDelete = async (rule) => {
    if (!window.confirm(`ルール「${rule.name}」を削除しますか？`)) {
      return;
    }

    try {
      await axios.delete(`/api/rules/${rule.id}`);
      alert('ルールを削除しました');
      fetchRules();
    } catch (error) {
      console.error('ルールの削除に失敗しました:', error);
      alert('ルールの削除に失敗しました');
    }
  };

  // 条件を追加
  const addCondition = () => {
    setFormData({
      ...formData,
      conditions: [...formData.conditions, '']
    });
  };

  // 条件を削除
  const removeCondition = (index) => {
    setFormData({
      ...formData,
      conditions: formData.conditions.filter((_, i) => i !== index)
    });
  };

  // 条件を更新
  const updateCondition = (index, value) => {
    const newConditions = [...formData.conditions];
    newConditions[index] = value;
    setFormData({
      ...formData,
      conditions: newConditions
    });
  };

  // アクションを追加
  const addAction = () => {
    setFormData({
      ...formData,
      actions: [...formData.actions, '']
    });
  };

  // アクションを削除
  const removeAction = (index) => {
    setFormData({
      ...formData,
      actions: formData.actions.filter((_, i) => i !== index)
    });
  };

  // アクションを更新
  const updateAction = (index, value) => {
    const newActions = [...formData.actions];
    newActions[index] = value;
    setFormData({
      ...formData,
      actions: newActions
    });
  };

  // エクスポート
  const handleExport = async () => {
    try {
      const params = { visa_type: visaTypeFilter };
      const response = await axios.get('/api/rules/export', { params });

      // JSONファイルとしてダウンロード
      const dataStr = JSON.stringify(response.data, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `visa-rules-${visaTypeFilter}-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      alert('ルールをエクスポートしました');
    } catch (error) {
      console.error('エクスポートに失敗しました:', error);
      alert('エクスポートに失敗しました');
    }
  };

  // インポート
  const handleImport = async () => {
    try {
      const data = JSON.parse(importData);

      if (!data.rules || !Array.isArray(data.rules)) {
        alert('無効なデータ形式です。rules配列が必要です。');
        return;
      }

      const response = await axios.post('/api/rules/import', {
        rules: data.rules,
        overwrite: overwriteExisting
      });

      alert(
        `インポートが完了しました\n` +
        `新規: ${response.data.imported}件\n` +
        `更新: ${response.data.updated}件\n` +
        `スキップ: ${response.data.skipped}件\n` +
        (response.data.errors.length > 0 ? `\nエラー:\n${response.data.errors.join('\n')}` : '')
      );

      setShowImportModal(false);
      setImportData('');
      fetchRules();
    } catch (error) {
      console.error('インポートに失敗しました:', error);
      if (error.message.includes('JSON')) {
        alert('JSONの形式が正しくありません');
      } else {
        alert('インポートに失敗しました');
      }
    }
  };

  // ファイルから読み込み
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setImportData(e.target.result);
      };
      reader.readAsText(file);
    }
  };

  // 順序変更: ドラッグ開始
  const handleDragStart = (e, index) => {
    setDraggedItem(index);
    e.dataTransfer.effectAllowed = 'move';
  };

  // 順序変更: ドラッグオーバー
  const handleDragOver = (e, index) => {
    e.preventDefault();
    if (draggedItem === null || draggedItem === index) return;

    const newRules = [...rules];
    const draggedRule = newRules[draggedItem];
    newRules.splice(draggedItem, 1);
    newRules.splice(index, 0, draggedRule);

    setRules(newRules);
    setDraggedItem(index);
    setHasChanges(true);
  };

  // 順序変更: ドラッグ終了
  const handleDragEnd = () => {
    setDraggedItem(null);
  };

  // 順序変更: 上に移動
  const handleMoveUp = (index) => {
    if (index === 0) return;
    const newRules = [...rules];
    [newRules[index - 1], newRules[index]] = [newRules[index], newRules[index - 1]];
    setRules(newRules);
    setHasChanges(true);
  };

  // 順序変更: 下に移動
  const handleMoveDown = (index) => {
    if (index === rules.length - 1) return;
    const newRules = [...rules];
    [newRules[index], newRules[index + 1]] = [newRules[index + 1], newRules[index]];
    setRules(newRules);
    setHasChanges(true);
  };

  // 順序を保存
  const handleSaveOrder = async () => {
    try {
      // 各ルールのpriorityを更新
      for (let i = 0; i < rules.length; i++) {
        await axios.put(`/api/rules/${rules[i].id}`, {
          ...rules[i],
          priority: i
        });
      }
      alert('順序を保存しました');
      setOriginalRules(rules);
      setHasChanges(false);
    } catch (error) {
      console.error('順序の保存に失敗しました:', error);
      alert('順序の保存に失敗しました');
    }
  };

  // 順序をリセット
  const handleResetOrder = () => {
    setRules(originalRules);
    setHasChanges(false);
  };

  return (
    <div className="rule-management-container">
      <div className="rule-management-header">
        <h2>ルール管理</h2>
      </div>

      {/* ビザタイプタブ */}
      <div className="visa-tabs">
        <button
          className={`visa-tab ${visaTypeFilter === 'E' ? 'active' : ''}`}
          onClick={() => setVisaTypeFilter('E')}
        >
          Eビザ
        </button>
        <button
          className={`visa-tab ${visaTypeFilter === 'L' ? 'active' : ''}`}
          onClick={() => setVisaTypeFilter('L')}
        >
          Lビザ
        </button>
        <button
          className={`visa-tab ${visaTypeFilter === 'B' ? 'active' : ''}`}
          onClick={() => setVisaTypeFilter('B')}
        >
          Bビザ
        </button>
        <button
          className={`visa-tab ${visaTypeFilter === 'H' ? 'active' : ''}`}
          onClick={() => setVisaTypeFilter('H')}
        >
          H-1Bビザ
        </button>
        <button
          className={`visa-tab ${visaTypeFilter === 'J' ? 'active' : ''}`}
          onClick={() => setVisaTypeFilter('J')}
        >
          J-1ビザ
        </button>
      </div>

      <div className="rule-management-content">
        <div className="header-actions">
          <button onClick={handleCreateNew} className="btn btn-primary">
            新規ルール作成
          </button>
          <button onClick={handleExport} className="btn btn-secondary">
            エクスポート
          </button>
          <button onClick={() => setShowImportModal(true)} className="btn btn-secondary">
            インポート
          </button>
          {hasChanges && (
            <>
              <button onClick={handleSaveOrder} className="btn btn-save">
                順序を保存
              </button>
              <button onClick={handleResetOrder} className="btn btn-secondary">
                リセット
              </button>
            </>
          )}
        </div>
      </div>

      {loading ? (
        <div className="loading">読み込み中...</div>
      ) : (
        <div className="rules-list">
          <table className="rules-table">
            <thead>
              <tr>
                <th style={{width: '40px'}}>#</th>
                <th style={{width: '60px'}}>移動</th>
                <th style={{width: '100px'}}>ルール名</th>
                <th style={{width: '80px'}}>ビザ</th>
                <th style={{width: '35%'}}>条件</th>
                <th style={{width: '35%'}}>アクション</th>
                <th style={{width: '120px'}}>操作</th>
              </tr>
            </thead>
            <tbody>
              {rules.map((rule, index) => (
                <tr
                  key={rule.id}
                  draggable
                  onDragStart={(e) => handleDragStart(e, index)}
                  onDragOver={(e) => handleDragOver(e, index)}
                  onDragEnd={handleDragEnd}
                  className={draggedItem === index ? 'dragging' : ''}
                >
                  <td style={{textAlign: 'center', fontWeight: 'bold', color: '#666'}}>
                    {index + 1}
                  </td>
                  <td>
                    <div className="move-buttons">
                      <button
                        onClick={() => handleMoveUp(index)}
                        disabled={index === 0}
                        className="btn btn-tiny btn-move"
                        title="上に移動"
                      >
                        ↑
                      </button>
                      <button
                        onClick={() => handleMoveDown(index)}
                        disabled={index === rules.length - 1}
                        className="btn btn-tiny btn-move"
                        title="下に移動"
                      >
                        ↓
                      </button>
                    </div>
                  </td>
                  <td>
                    <span className="drag-handle" title="ドラッグして並び替え">≡</span>
                    {rule.name}
                  </td>
                  <td>{rule.visa_type}</td>
                  <td>
                    <div className="rule-text-list">
                      {rule.conditions.map((condition, idx) => (
                        <div key={idx} className="rule-text-item">
                          {rule.condition_logic === 'OR' && idx > 0 && (
                            <span className="logic-separator">OR</span>
                          )}
                          {rule.condition_logic === 'AND' && idx > 0 && (
                            <span className="logic-separator">AND</span>
                          )}
                          {condition}
                        </div>
                      ))}
                    </div>
                  </td>
                  <td>
                    <div className="rule-text-list">
                      {rule.actions.map((action, idx) => (
                        <div key={idx} className="rule-text-item">
                          {action}
                        </div>
                      ))}
                    </div>
                  </td>
                  <td>
                    <button
                      onClick={() => handleEdit(rule)}
                      className="btn btn-small btn-edit"
                    >
                      編集
                    </button>
                    <button
                      onClick={() => handleDelete(rule)}
                      className="btn btn-small btn-delete"
                    >
                      削除
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showImportModal && (
        <div className="modal-overlay" onClick={() => setShowImportModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>ルールのインポート</h3>

            <div className="form-group">
              <label>JSONファイルを選択</label>
              <input
                type="file"
                accept=".json"
                onChange={handleFileUpload}
                className="file-input"
              />
            </div>

            <div className="form-group">
              <label>またはJSONデータを貼り付け</label>
              <textarea
                value={importData}
                onChange={(e) => setImportData(e.target.value)}
                placeholder='{"rules": [...]}'
                rows={10}
                className="import-textarea"
              />
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={overwriteExisting}
                  onChange={(e) => setOverwriteExisting(e.target.checked)}
                />
                既存のルールを上書きする
              </label>
              <p className="help-text-small">
                チェックしない場合、同じ名前のルールはスキップされます
              </p>
            </div>

            <div className="form-actions">
              <button onClick={handleImport} className="btn btn-primary">
                インポート
              </button>
              <button
                onClick={() => {
                  setShowImportModal(false);
                  setImportData('');
                }}
                className="btn btn-secondary"
              >
                キャンセル
              </button>
            </div>
          </div>
        </div>
      )}

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>{editingRule ? 'ルール編集' : '新規ルール作成'}</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>ルール名</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>ビザタイプ</label>
                  <select
                    value={formData.visa_type}
                    onChange={(e) => setFormData({ ...formData, visa_type: e.target.value })}
                  >
                    <option value="E">Eビザ</option>
                    <option value="L">Lビザ</option>
                    <option value="B">Bビザ</option>
                    <option value="H">H-1Bビザ</option>
                    <option value="J">J-1ビザ</option>
                    <option value="ALL">すべて</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>ルールタイプ</label>
                  <select
                    value={formData.rule_type}
                    onChange={(e) => setFormData({ ...formData, rule_type: e.target.value })}
                  >
                    <option value="#n!">終了ルール (#n!)</option>
                    <option value="#i">中間ルール (#i)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>条件ロジック</label>
                  <select
                    value={formData.condition_logic}
                    onChange={(e) => setFormData({ ...formData, condition_logic: e.target.value })}
                  >
                    <option value="AND">AND</option>
                    <option value="OR">OR</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>優先度</label>
                  <input
                    type="number"
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>条件</label>
                {formData.conditions.map((condition, index) => (
                  <div key={index} className="input-group">
                    <input
                      type="text"
                      value={condition}
                      onChange={(e) => updateCondition(index, e.target.value)}
                      placeholder="条件を入力"
                    />
                    <button
                      type="button"
                      onClick={() => removeCondition(index)}
                      className="btn btn-small btn-remove"
                    >
                      削除
                    </button>
                  </div>
                ))}
                <button type="button" onClick={addCondition} className="btn btn-small btn-add">
                  条件を追加
                </button>
              </div>

              <div className="form-group">
                <label>アクション（結論）</label>
                {formData.actions.map((action, index) => (
                  <div key={index} className="input-group">
                    <input
                      type="text"
                      value={action}
                      onChange={(e) => updateAction(index, e.target.value)}
                      placeholder="アクションを入力"
                    />
                    <button
                      type="button"
                      onClick={() => removeAction(index)}
                      className="btn btn-small btn-remove"
                    >
                      削除
                    </button>
                  </div>
                ))}
                <button type="button" onClick={addAction} className="btn btn-small btn-add">
                  アクションを追加
                </button>
              </div>

              <div className="form-actions">
                <button type="submit" className="btn btn-primary">
                  {editingRule ? '更新' : '作成'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="btn btn-secondary"
                >
                  キャンセル
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      </div>
    </div>
  );
};

export default RuleManagementPage;
