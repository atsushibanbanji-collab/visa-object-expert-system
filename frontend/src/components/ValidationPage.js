import React, { useState } from 'react';
import axios from 'axios';
import './ValidationPage.css';

const ValidationPage = () => {
  const [validationResult, setValidationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [visaTypeFilter, setVisaTypeFilter] = useState('E');
  const [showFixDialog, setShowFixDialog] = useState(false);
  const [fixPreview, setFixPreview] = useState(null);

  const runValidation = async () => {
    setLoading(true);
    try {
      const params = { visa_type: visaTypeFilter };
      const response = await axios.get('/api/validation/check', { params });
      setValidationResult(response.data);
    } catch (error) {
      console.error('検証に失敗しました:', error);
      alert('検証に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleAutoFix = async (fixType, violations) => {
    // 修正内容のプレビューを生成
    let preview = null;
    if (fixType === 'dependency_order') {
      preview = {
        title: '依存関係の順序違反を自動修正',
        description: '以下のルールのpriorityを変更します：',
        changes: violations.map(v => ({
          rule: v.producer_rule,
          oldPriority: v.producer_priority,
          newPriority: Math.max(0, v.consumer_priority - 10),
          reason: `ルール ${v.consumer_rule} (priority=${v.consumer_priority}) より前に配置`
        })),
        fixType,
        violations
      };
    }

    setFixPreview(preview);
    setShowFixDialog(true);
  };

  const applyFix = async () => {
    setLoading(true);
    setShowFixDialog(false);

    try {
      const response = await axios.post('/api/validation/auto-fix', {
        visa_type: visaTypeFilter,
        fix_type: fixPreview.fixType,
        violations: fixPreview.violations
      });

      if (response.data.success) {
        alert(`修正完了: ${response.data.message}`);
        // 修正後に再検証
        await runValidation();
      } else {
        alert(`修正失敗: ${response.data.message}`);
      }
    } catch (error) {
      console.error('自動修正に失敗しました:', error);
      alert('自動修正に失敗しました');
    } finally {
      setLoading(false);
      setFixPreview(null);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'ok':
        return '✓';
      case 'warning':
        return '⚠';
      case 'error':
        return '✗';
      default:
        return '?';
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'ok':
        return 'status-ok';
      case 'warning':
        return 'status-warning';
      case 'error':
        return 'status-error';
      default:
        return '';
    }
  };

  return (
    <div className="validation-container">
      <div className="validation-header">
        <div>
          <h2>ルール検証</h2>
          <p className="subtitle">ルールの整合性、循環参照、到達不能ルールをチェック</p>
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
            onClick={runValidation}
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? '検証中...' : '検証を実行'}
          </button>
        </div>
      </div>

      {validationResult && (
        <div className="validation-results">
          {/* サマリー */}
          <div className={`validation-summary ${getStatusClass(validationResult.status)}`}>
            <div className="summary-icon">{getStatusIcon(validationResult.status)}</div>
            <div className="summary-content">
              <h3>
                {validationResult.status === 'ok' && '問題ありません'}
                {validationResult.status === 'warning' && '警告があります'}
                {validationResult.status === 'error' && 'エラーがあります'}
              </h3>
              <p>
                {validationResult.total_rules}個のルールを検証しました
                （{validationResult.visa_type}ビザ）
              </p>
              <div className="summary-stats">
                <span className="stat-error">エラー: {validationResult.error_count}</span>
                <span className="stat-warning">警告: {validationResult.warning_count}</span>
              </div>
            </div>
          </div>

          {/* 整合性エラー */}
          {validationResult.consistency_errors.length > 0 && (
            <div className="validation-section error-section">
              <h4>整合性エラー ({validationResult.consistency_errors.length})</h4>
              <ul className="issue-list">
                {validationResult.consistency_errors.map((error, index) => (
                  <li key={index} className="issue-item error">
                    <span className="issue-icon">✗</span>
                    <div className="issue-content">
                      <div className="issue-title">{error.description}</div>
                      {error.rule_name && (
                        <div className="issue-detail">ルール: {error.rule_name}</div>
                      )}
                      <div className="issue-type">タイプ: {error.type}</div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* 循環参照 */}
          {validationResult.circular_dependencies.length > 0 && (
            <div className="validation-section warning-section">
              <h4>循環参照 ({validationResult.circular_dependencies.length})</h4>
              <p className="section-description">
                ルール間で循環依存が発生しています。推論が無限ループになる可能性があります。
              </p>
              <ul className="issue-list">
                {validationResult.circular_dependencies.map((cycle, index) => (
                  <li key={index} className="issue-item warning">
                    <span className="issue-icon">⚠</span>
                    <div className="issue-content">
                      <div className="issue-title">循環: {cycle.description}</div>
                      <div className="issue-detail">
                        関連ルール: {cycle.cycle.join(', ')}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* 到達不能ルール */}
          {validationResult.unreachable_rules.length > 0 && (
            <div className="validation-section warning-section">
              <h4>到達不能ルール ({validationResult.unreachable_rules.length})</h4>
              <p className="section-description">
                以下のルールは条件が満たされないため、到達できない可能性があります。
              </p>
              <ul className="issue-list">
                {validationResult.unreachable_rules.map((rule, index) => (
                  <li key={index} className="issue-item warning">
                    <span className="issue-icon">⚠</span>
                    <div className="issue-content">
                      <div className="issue-title">ルール {rule.rule_name}</div>
                      <div className="issue-detail">
                        到達不能な条件: {rule.unreachable_conditions.join(', ')}
                      </div>
                      <div className="issue-type">ルールタイプ: {rule.rule_type}</div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* 依存関係の順序違反 */}
          {validationResult.dependency_order_violations && validationResult.dependency_order_violations.length > 0 && (
            <div className="validation-section error-section">
              <div className="section-header-with-action">
                <h4>依存関係の順序違反 ({validationResult.dependency_order_violations.length})</h4>
                <button
                  className="btn btn-fix"
                  onClick={() => handleAutoFix('dependency_order', validationResult.dependency_order_violations)}
                  disabled={loading}
                >
                  🔧 自動修正
                </button>
              </div>
              <p className="section-description">
                アクションを生成するルールが、そのアクションを条件として使うルールより後ろにあります。
                推論が正しく動作しない可能性があります。
              </p>
              <ul className="issue-list">
                {validationResult.dependency_order_violations.map((violation, index) => (
                  <li key={index} className="issue-item error">
                    <span className="issue-icon">✗</span>
                    <div className="issue-content">
                      <div className="issue-title">{violation.description}</div>
                      <div className="issue-detail">
                        <strong>生成側:</strong> ルール {violation.producer_rule} (priority={violation.producer_priority})
                        が「{violation.action}」を生成
                      </div>
                      <div className="issue-detail">
                        <strong>使用側:</strong> ルール {violation.consumer_rule} (priority={violation.consumer_priority})
                        が「{violation.action}」を条件として使用
                      </div>
                      <div className="issue-solution">
                        → ルール {violation.producer_rule} の priority を {violation.consumer_rule} より小さくしてください
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* 問題なし */}
          {validationResult.status === 'ok' && (
            <div className="validation-section success-section">
              <p className="success-message">
                すべてのルールが正常です。整合性エラー、循環参照、到達不能ルール、依存関係の順序違反は検出されませんでした。
              </p>
            </div>
          )}
        </div>
      )}

      {!validationResult && !loading && (
        <div className="validation-placeholder">
          <p>ビザタイプを選択して「検証を実行」ボタンをクリックしてください</p>
        </div>
      )}

      <div className="help-text">
        <h3>検証内容</h3>
        <ul>
          <li><strong>整合性エラー:</strong> ルール名の重複、空の条件/アクション、終了ルールの不足など</li>
          <li><strong>循環参照:</strong> ルール間で相互に依存して無限ループになる問題</li>
          <li><strong>到達不能ルール:</strong> 条件が満たされず実行されないルール</li>
          <li><strong>依存関係の順序違反:</strong> アクションを生成するルールが、そのアクションを条件として使うルールより後ろにある問題（推論順序の違反）</li>
        </ul>
      </div>

      {/* 自動修正確認ダイアログ */}
      {showFixDialog && fixPreview && (
        <div className="modal-overlay" onClick={() => setShowFixDialog(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{fixPreview.title}</h3>
              <button className="modal-close" onClick={() => setShowFixDialog(false)}>×</button>
            </div>
            <div className="modal-body">
              <p className="modal-description">{fixPreview.description}</p>
              <div className="fix-preview-list">
                {fixPreview.changes.map((change, index) => (
                  <div key={index} className="fix-preview-item">
                    <div className="fix-preview-rule">
                      <strong>ルール {change.rule}</strong>
                    </div>
                    <div className="fix-preview-change">
                      priority: {change.oldPriority} → {change.newPriority}
                    </div>
                    <div className="fix-preview-reason">
                      {change.reason}
                    </div>
                  </div>
                ))}
              </div>
              <div className="modal-warning">
                ⚠️ この変更により、ルールの評価順序が変わります。よろしいですか？
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowFixDialog(false)}>
                キャンセル
              </button>
              <button className="btn btn-primary" onClick={applyFix}>
                修正を適用
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ValidationPage;
