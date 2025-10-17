import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './RuleManagementPage.css';

const RuleManagementPage = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingRule, setEditingRule] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [visaTypeFilter, setVisaTypeFilter] = useState('ALL');

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
      const params = visaTypeFilter !== 'ALL' ? { visa_type: visaTypeFilter } : {};
      const response = await axios.get('/api/rules', { params });
      setRules(response.data);
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
      visa_type: 'E',
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

  return (
    <div className="rule-management-container">
      <div className="rule-management-header">
        <h2>ルール管理</h2>
        <div className="header-actions">
          <select
            value={visaTypeFilter}
            onChange={(e) => setVisaTypeFilter(e.target.value)}
            className="visa-filter"
          >
            <option value="ALL">すべてのビザ</option>
            <option value="E">Eビザ</option>
            <option value="L">Lビザ</option>
            <option value="B">Bビザ</option>
            <option value="H">H-1Bビザ</option>
            <option value="J">J-1ビザ</option>
          </select>
          <button onClick={handleCreateNew} className="btn btn-primary">
            新規ルール作成
          </button>
        </div>
      </div>

      {loading ? (
        <div className="loading">読み込み中...</div>
      ) : (
        <div className="rules-list">
          <table className="rules-table">
            <thead>
              <tr>
                <th>ルール名</th>
                <th>ビザタイプ</th>
                <th>ルールタイプ</th>
                <th>条件ロジック</th>
                <th>条件数</th>
                <th>アクション数</th>
                <th>優先度</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {rules.map((rule) => (
                <tr key={rule.id}>
                  <td>{rule.name}</td>
                  <td>{rule.visa_type}</td>
                  <td>
                    <span className={`badge ${rule.rule_type}`}>
                      {rule.rule_type}
                    </span>
                  </td>
                  <td>
                    <span className={`badge logic ${rule.condition_logic}`}>
                      {rule.condition_logic}
                    </span>
                  </td>
                  <td>{rule.conditions.length}</td>
                  <td>{rule.actions.length}</td>
                  <td>{rule.priority}</td>
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
  );
};

export default RuleManagementPage;
