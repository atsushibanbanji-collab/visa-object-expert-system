# 米国ビザ選定エキスパートシステム - プロジェクト記録

**最終更新**: 2025-10-19
**プロジェクトステータス**: デプロイ済み（機能拡張中）

---

## 📋 プロジェクト概要

オブジェクト指向エキスパートシステムを用いた米国ビザ選定診断Webアプリケーション

- **目的**: 質問に答えて最適な米国ビザの種類を診断
- **技術スタック**:
  - Backend: Python (FastAPI, SQLAlchemy, SQLite)
  - Frontend: React 18
  - Deployment: Render.com
- **GitHubリポジトリ**: https://github.com/atsushibanbanji-collab/visa-object-expert-system.git

---

## 🏗️ プロジェクト構造

```
visa-expert-system/
├── backend/
│   ├── main.py                    # FastAPI メインアプリケーション
│   ├── database.db                # SQLiteデータベース
│   ├── models/
│   │   ├── consultation.py        # 診断制御クラス（推論エンジン）
│   │   ├── rule.py                # ルール基底クラス
│   │   ├── rule_db.py             # データベースモデル
│   │   ├── dynamic_rule.py        # 動的ルールクラス
│   │   └── working_memory.py      # 作業記憶クラス
│   ├── rules/
│   │   ├── visa_rules.py          # 30個のビザルール定義
│   │   └── rule_loader.py         # ルール読み込み
│   ├── api/
│   │   ├── consultation_api.py    # 診断API
│   │   ├── rule_management_api.py # ルール管理API
│   │   └── validation_api.py      # 検証API
│   └── migrate_rules.py           # ルールDB移行スクリプト
│
├── frontend/
│   ├── src/
│   │   ├── App.js                 # メインアプリ
│   │   ├── App.css                # グローバルスタイル
│   │   └── components/
│   │       ├── ConsultationForm.js    # 診断画面
│   │       ├── ConsultationForm.css
│   │       ├── QuestionsPage.js       # 質問一覧
│   │       ├── QuestionsPage.css
│   │       ├── RuleManagementPage.js  # ルール管理
│   │       ├── RuleManagementPage.css
│   │       ├── ValidationPage.js      # 検証画面
│   │       └── ValidationPage.css
│   └── package.json
│
└── works/                         # 仕様ドキュメント
    ├── ビザ選定知識.txt          # 30個のルール仕様
    └── システムイメージ.txt       # システム要件
```

---

## 🎯 主要機能

### 1. 診断機能（ConsultationForm）
質問に答えて最適なビザを診断する対話型システム

**特徴**:
- **Forward Chaining（前向き推論）**エンジン
- リアルタイムデバッグ情報表示
- 効率的な質問選択（最小質問数で診断）

**表示内容**:
- **WORKING MEMORY - FACTS**: 回答済みの質問
- **WORKING MEMORY - HYPOTHESES**: 導出された仮説
- **RULES BEING EVALUATED**: 評価中のルール
  - 🟢 緑: 肯定された条件 (true)
  - 🔴 赤: 否定された条件 (false)
  - 🟡 黄: 判定前の条件 (unknown)
- **APPLIED RULES**: 適用されたルール

### 2. 質問一覧（QuestionsPage）
各ビザタイプの全質問とルール詳細を表示

**機能**:
- ビザタイプごとのタブ切り替え（E / L / B）
- 統計表示（ルール数、質問数）
- ルール詳細の展開表示
  - 条件（IF）: AND/ORバッジ付き
  - 結論（THEN）
  - ルールタイプ（#i / #n!）

### 3. ルール管理（RuleManagementPage）
ルールのCRUD操作と順序管理を統合

**機能**:
- ルールの作成・編集・削除
- **ドラッグ&ドロップ**による順序変更
- 上下移動ボタン
- ビザタイプフィルター
- **インポート/エクスポート**（JSON形式）
  - 個別ビザタイプ
  - 全ビザタイプ一括
- リアルタイム変更検知と保存機能

### 4. 検証（ValidationPage）
ルールの整合性チェック

**検証項目**:
- **循環依存検出**（DFSアルゴリズム）
- ルール完全性チェック
- 条件・結論の存在確認
- 孤立ルールの検出

---

## 📊 ビザタイプとルール

| ビザタイプ | ルール番号 | ルール数 | 説明 |
|-----------|-----------|---------|------|
| Eビザ     | 1-11      | 11個    | 投資家・貿易駐在員ビザ |
| Lビザ     | 12-21     | 10個    | 企業内転勤者ビザ |
| Bビザ     | 23-27, 29-30 | 7個  | 商用・観光ビザ |
| H-1Bビザ  | 22        | 1個     | 専門職ビザ |
| J-1ビザ   | 28        | 1個     | 研修ビザ |

**合計**: 30ルール

---

## 🔧 技術詳細

### エキスパートシステムアーキテクチャ

#### 1. ルールタイプ
- `#i`: 中間ルール（仮説を導出）
- `#n!`: 終了ルール（最終結論）

#### 2. 条件ロジック
- `AND`: すべての条件を満たす必要がある
- `OR`: いずれか1つの条件を満たせばよい

#### 3. 推論エンジン (`consultation.py`)

**主要メソッド**:
```python
start_deduce()              # 推論開始
_select_applicable_rules()  # 競合集合生成
apply_rule()                # ルール適用
_find_next_question()       # 次の質問を探索
_get_rules_with_condition() # 質問に関連するルール取得
_is_question_necessary()    # 質問の必要性判定
_check_if_impossible()      # 否定的推論
```

**推論フロー**:
```
start_up()
  ↓
start_deduce()
  ↓
_check_if_impossible() ──→ 申請不可？ ──Yes→ 終了
  ↓ No
_select_applicable_rules() ──→ 競合集合
  ↓
apply_rule() ──→ ルール適用 ──→ #n! ルール？ ──Yes→ 終了
  ↓ No                              ↓ No
_find_next_question() ──→ 次の質問 ──→ ユーザー回答
  ↓                                    ↓
start_deduce() に戻る ←────────────────┘
```

#### 4. Working Memory (`working_memory.py`)
```python
findings: Dict[str, bool]     # 回答済み質問（事実）
hypotheses: Dict[str, bool]   # 導出された仮説
```

#### 5. データベース (SQLite)
```python
RuleDB テーブル:
- id: INTEGER (主キー)
- visa_type: VARCHAR (E/L/B/H/J)
- name: VARCHAR (ルール番号)
- conditions: JSON
- actions: JSON
- rule_type: VARCHAR (#i/#n!)
- condition_logic: VARCHAR (AND/OR)
- priority: INTEGER
```

---

## 🎨 UIデザイン

### デザインコンセプト
- **フォーマルでシステマチック**な印象
- ポップさを排除
- 画面を広く使う
- 色分けによる視認性向上

### カラースキーム
```css
/* プライマリー */
--primary-blue: #2c5282

/* 背景 */
--bg-light: #f7fafc
--bg-white: #ffffff

/* 条件状態 */
--condition-true-bg: #f0fff4
--condition-true-border: #48bb78
--condition-false-bg: #fff5f5
--condition-false-border: #fc8181
--condition-unknown-bg: #fffbeb
--condition-unknown-border: #f59e0b

/* AND/OR */
--logic-and: #333
--logic-or: #666
```

---

## ⚠️ 重要な修正履歴

### 2025-10-19: AND条件の動作修正

**問題点**:
AND条件のルールで1つの条件に「いいえ」を選択しても、そのルールがpending_rulesに残り続け、仮説の表示が切り替わらない。

**影響範囲**:
- Lビザ（ルール12, 14, 16, 17, 18, 19, 20, 21）
- Bビザ（ルール24, 25, 26, 27, 29, 30）
- Eビザ（ルール1, 4, 6, 8, 11）

**修正内容** (`backend/models/consultation.py`):

1. **`_get_rules_with_condition()`メソッド**:
```python
# AND条件のルールで他の条件が既にFalseの場合は除外
if rule.condition_logic == "AND":
    can_be_satisfied = True
    for cond in rule.conditions:
        if cond == condition:
            continue
        value = self.status.get_value(cond)
        if value is False:
            can_be_satisfied = False
            break
    if not can_be_satisfied:
        continue
```

2. **`_is_question_necessary()`メソッド**:
```python
# AND条件のルールで他の条件が既にFalseの場合は質問不要
if rule.condition_logic == "AND":
    # (同様のチェックロジック)
```

**コミット**: e8e9fe0

**効果**:
- AND条件で1つでも「いいえ」を選択すると即座にそのルールが除外
- 仮説の表示が正しく次の有効なルールに切り替わる
- 不要な質問をスキップして診断が効率化

---

## 📝 既知の問題

### 1. Rule 19 の不足条件（未修正）

**場所**: `backend/rules/visa_rules.py:467-489`

**問題**: ビザ選定知識.txt の19行目によると、本来3つの条件があるべきだが、実装では2つのみ

**実装されている条件**:
1. 直近3年のうち1年以上、アメリカ以外のグループ会社に所属していました
2. Lビザ（Individual）のマネージャーまたはスタッフの条件を満たします

**欠けている条件**:
「Lビザ 質問6」

**状態**: 特定済み、未修正（ユーザーリクエストにより保留中）

### 2. サーバー起動時間

**問題**: Render.comの無料プランではコールドスタート時に時間がかかる（30-60秒）

**対策**: `App.js`でバックエンドのウォームアップ処理を実装済み
```javascript
useEffect(() => {
  const warmUpBackend = async () => {
    await axios.get('/api/health', { timeout: 60000 });
  };
  warmUpBackend();
}, []);
```

### 3. セッション管理

**現状**: グローバル変数で1セッションのみ対応

**課題**: 複数ユーザー同時利用不可

**将来の対策**:
- セッションIDの導入
- Redis等のセッションストア
- データベースへのセッション保存

---

## 🚀 デプロイメント

### Render.com設定

**リポジトリ**: https://github.com/atsushibanbanji-collab/visa-object-expert-system.git

**ブランチ**: main

**自動デプロイ**: `git push` でトリガー

**デプロイ時間**: 5-10分

### ローカル開発

```bash
# バックエンド起動
cd backend
python main.py

# フロントエンド起動
cd frontend
npm start
```

### データベース操作

**ルールの移行**:
```bash
cd backend
python migrate_rules.py
```

これにより`visa_rules.py`の30ルールが`database.db`に書き込まれる。

---

## 🔍 デバッグ方法

### 1. フロントエンド

**ブラウザコンソール**:
```javascript
console.log('質問データの取得に失敗しました:', error);
```

**診断画面のデバッグセクション**:
- WORKING MEMORY: 現在の状態確認
- RULES BEING EVALUATED: 評価中のルール確認
- APPLIED RULES: 適用済みルール確認

### 2. バックエンド

**FastAPI自動ドキュメント**:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

**ログ出力**:
```python
print(f"DEBUG: {variable}")
```

### 3. データベース

**SQLite確認**:
```bash
sqlite3 backend/database.db
.tables
SELECT * FROM rules WHERE visa_type='L';
.quit
```

---

## 📚 参考資料

### プロジェクトドキュメント

**作業ディレクトリ**: `C:\Users\GPC999\Documents\visa-expert-system`

**仕様ドキュメント**:
- `works/ビザ選定知識.txt`: 30個のルール仕様
- `works/システムイメージ.txt`: システム要件（5項目）

### エキスパートシステム理論
- Forward Chaining（前向き推論）
- Working Memory（作業記憶）
- Conflict Set（競合集合）
- Rule-based System（ルールベースシステム）

---

## 💡 次回作業時のチェックリスト

開発を再開する際の確認事項:

- [ ] プロジェクトディレクトリに移動: `cd C:\Users\GPC999\Documents\visa-expert-system`
- [ ] 最新のコミット確認: `git log --oneline -5`
- [ ] ブランチ確認: `git status`
- [ ] `backend/database.db` の存在確認
- [ ] `frontend/node_modules` の存在確認（なければ `npm install`）
- [ ] このファイル（PROJECT_STATUS.md）を読む

---

## 🆘 トラブルシューティング

### 診断が進まない

**確認項目**:
1. ブラウザのコンソールでエラー確認
2. バックエンドのログ確認
3. Working Memoryの状態確認
4. ルールの条件ロジック（AND/OR）確認

**よくある原因**:
- AND条件で全条件が満たされていない
- ルールが既に発火済み（flag = "#fired"）
- 質問が導出可能な仮説になっている

### ルールが適用されない

**確認項目**:
1. ルールの順序を確認（ルール管理画面）
2. 検証ページで循環依存をチェック
3. 条件が正しく入力されているか確認

### デプロイ後に動作しない

**確認項目**:
1. Render.comのログ確認
2. `database.db`が正しく作成されているか
3. 環境変数の設定確認
4. ビルドログでエラー確認

### データベースが空

**対処法**:
```bash
cd backend
python migrate_rules.py
```

---

## 📊 統計情報

- **総ルール数**: 30個
- **対応ビザタイプ**: 5種類（E, L, B, H-1B, J-1）
- **質問候補数**: 約90個
- **平均質問数**: 5-15個（効率的な推論により最小化）
- **総コード行数**: 約5,000行
- **主要ファイル数**: 15個
- **最新コミット**: e8e9fe0（AND条件の動作修正）

---

## 🎯 今後の改善予定

### 短期（実装容易）
1. 戻るボタン機能
2. 質問への補足説明
3. プログレスバー
4. Rule 19 の修正

### 中期（ビジネス価値）
5. PDF診断レポート出力
6. 診断履歴の保存
7. 多言語対応（英語）
8. モバイル対応改善

### 長期（本格運用）
9. PostgreSQL移行
10. ユーザーアカウント管理
11. 料金プラン機能
12. 専門家への相談機能
13. 利用統計・アナリティクス

---

## 📞 リソース

- **GitHub**: https://github.com/atsushibanbanji-collab/visa-object-expert-system
- **Render**: https://dashboard.render.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/

---

**作成者**: Claude Code
**プロジェクト開始**: 2025年10月
**最終更新**: 2025年10月19日

このドキュメントは開発記録として作成されました。プロジェクトの変更に応じて適宜更新してください。
