import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './FlowchartPage.css';

const FlowchartPage = ({ onBack }) => {
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

  const buildFlowTree = (rules) => {
    // 終了ルールから逆向きにツリーを構築
    const terminalRules = rules.filter(rule => rule.type === '#n!');

    const tree = terminalRules.map(terminalRule => {
      return buildRuleTree(terminalRule, rules);
    });

    return tree;
  };

  const buildRuleTree = (rule, allRules) => {
    const dependencies = [];

    // このルールの条件を満たすために必要な他のルールを探す
    rule.conditions.forEach(condition => {
      const dependentRule = allRules.find(r => r.actions.includes(condition));
      if (dependentRule && dependentRule.name !== rule.name) {
        dependencies.push(buildRuleTree(dependentRule, allRules));
      }
    });

    return {
      rule,
      dependencies
    };
  };

  const renderRuleNode = (node, depth = 0) => {
    const { rule, dependencies } = node;
    const hasChildren = dependencies && dependencies.length > 0;

    return (
      <div key={`${rule.name}-${depth}`} className="rule-node">
        <div className={`rule-card ${rule.type}`}>
          <div className="rule-header">
            <span className="rule-name">ルール {rule.name}</span>
            <div className="rule-badges">
              <span className={`rule-badge ${rule.type}`}>
                {rule.type === '#n!' ? '終了' : '中間'}
              </span>
              <span className={`rule-badge logic-badge ${rule.condition_logic}`}>
                {rule.condition_logic}
              </span>
            </div>
          </div>
          <div className="rule-body">
            <div className="rule-section-flow">
              <strong>条件 (IF):</strong>
              <ul>
                {rule.conditions.map((cond, i) => (
                  <li key={i}>{cond}</li>
                ))}
              </ul>
            </div>
            <div className="arrow-down">↓</div>
            <div className="rule-section-flow">
              <strong>結論 (THEN):</strong>
              <ul>
                {rule.actions.map((action, i) => (
                  <li key={i}>{action}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {hasChildren && (
          <div className="dependencies">
            <div className="dependency-line"></div>
            <div className="dependency-nodes">
              {dependencies.map((dep, i) => renderRuleNode(dep, depth + 1))}
            </div>
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flowchart-container">
        <div className="flowchart-card">
          <p>読み込み中...</p>
        </div>
      </div>
    );
  }

  if (!questionsData) {
    return (
      <div className="flowchart-container">
        <div className="flowchart-card">
          <p>データの取得に失敗しました</p>
          <button className="btn btn-secondary" onClick={onBack}>
            戻る
          </button>
        </div>
      </div>
    );
  }

  const visaData = questionsData[selectedVisa];
  const flowTree = buildFlowTree(visaData.rules);

  return (
    <div className="flowchart-container">
      <div className="flowchart-card">
        <div className="flowchart-header">
          <h1>診断フローチャート</h1>
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

        <div className="flowchart-content">
          <h2>{visaData.name}の診断フロー</h2>
          <p className="flow-description">
            終了ルール（申請可否の判定）から逆向きに、必要な条件を満たすルールが表示されます。
          </p>

          <div className="flow-tree">
            {flowTree.map((node, i) => (
              <div key={i} className="flow-branch">
                {renderRuleNode(node)}
              </div>
            ))}
          </div>

          <div className="legend">
            <h3>凡例</h3>
            <div className="legend-items">
              <div className="legend-item">
                <span className="legend-badge terminal">終了</span>
                <span>最終判定ルール（申請可否を決定）</span>
              </div>
              <div className="legend-item">
                <span className="legend-badge intermediate">中間</span>
                <span>中間ルール（条件を推論）</span>
              </div>
              <div className="legend-item">
                <span className="legend-badge logic and">AND</span>
                <span>すべての条件を満たす必要がある</span>
              </div>
              <div className="legend-item">
                <span className="legend-badge logic or">OR</span>
                <span>いずれか1つの条件を満たせばよい</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FlowchartPage;
