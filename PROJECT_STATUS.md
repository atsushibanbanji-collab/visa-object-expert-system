# 米国ビザ選定エキスパートシステム - プロジェクト状況

## 📌 プロジェクト概要

オブジェクト指向プロダクションシステムを使用した米国ビザ選定のエキスパートシステム。
Smalltalk資料（C:\Users\GPC999\Documents\works\Smalltalk資料.pdf）を参考に、
Python + React で実装した前向き推論エンジンベースの診断システム。

**目的**: ユーザーが質問に答えることで、最適な米国ビザの種類を診断する

---

## 🚀 現在の状況

### デプロイ状態
- ✅ **デプロイ完了** - Renderにデプロイ済み
- 🟡 **サービス前** - 機能改善・仕様変更の段階
- 📍 **GitHubリポジトリ**: https://github.com/atsushibanbanji-collab/visa-object-expert-system.git

### デプロイURL（Render）
- **フロントエンド**: https://visa-expert-frontend.onrender.com
- **バックエンドAPI**: https://visa-expert-backend.onrender.com

---

## 🛠️ 技術スタック

### バックエンド
- **言語**: Python 3.11
- **フレームワーク**: FastAPI 0.104.1
- **サーバー**: Uvicorn
- **推論エンジン**: カスタム実装（前向き推論 + 否定的推論）
- **アーキテクチャ**: オブジェクト指向プロダクションシステム

### フロントエンド
- **ライブラリ**: React 18.2.0
- **HTTPクライアント**: Axios 1.6.0
- **ビルドツール**: react-scripts 5.0.1
- **スタイル**: CSS（コンポーネント別）

### デプロイ
- **プラットフォーム**: Render
- **設定**: render.yaml（Blueprint方式）
- **バックエンド**: Web Service（Python）
- **フロントエンド**: Static Site

---

## 📂 プロジェクト構造

```
visa-expert-system/
├── backend/
│   ├── __init__.py
│   ├── main.py                          # FastAPIエントリポイント
│   ├── models/
│   │   ├── __init__.py
│   │   ├── rule.py                      # Ruleクラス（抽象）
│   │   ├── working_memory.py            # WorkingMemoryクラス
│   │   └── consultation.py              # Consultationクラス（推論エンジン）
│   ├── rules/
│   │   ├── __init__.py
│   │   └── visa_rules.py                # 30個のビザルール実装
│   ├── api/
│   │   ├── __init__.py
│   │   └── consultation_api.py          # REST APIエンドポイント
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── index.js
│   │   ├── App.js                       # メインアプリケーション
│   │   ├── App.css
│   │   ├── index.css
│   │   └── components/
│   │       ├── ConsultationForm.js      # 診断フォーム（メイン画面）
│   │       ├── ConsultationForm.css
│   │       ├── QuestionsPage.js         # 質問一覧ページ
│   │       ├── QuestionsPage.css
│   │       ├── FlowchartPage.js         # フローチャートページ
│   │       └── FlowchartPage.css
│   └── package.json
├── README.md
├── render.yaml                          # Render設定ファイル
└── PROJECT_STATUS.md                    # このファイル
```

---

## ✅ 実装済み機能

### コア機能
- [x] **オブジェクト指向プロダクションシステム**
  - Rule、WorkingMemory、Consultation クラス
- [x] **前向き推論エンジン**
  - 競合集合（Conflict Set）の生成と解決
  - ルールの優先度管理
- [x] **否定的推論**
  - 申請不可条件の早期判定
- [x] **AND/OR条件ロジック**
  - ルールごとにANDまたはOR条件を指定可能
- [x] **30個のビザルール**
  - Eビザ: ルール1-11（投資家・貿易駐在員）
  - Lビザ: ルール12-21（企業内転勤者）
  - Bビザ: ルール23-30（商用・観光）

### フロントエンド機能
- [x] **ビザタイプ選択画面**
  - E / L / B ビザから選択
- [x] **対話型診断**
  - はい/いいえ形式の質問応答
  - 最小質問数での診断（効率的な推論）
- [x] **診断結果表示**
  - 申請可能なビザの表示
  - 申請不可の判定
  - 回答履歴の表示
- [x] **質問一覧ページ**
  - 各ビザタイプの全質問を表示
- [x] **フローチャートページ**
  - ルールの依存関係を視覚化
  - AND/ORロジックの表示
- [x] **リセット機能**
  - 診断の最初からやり直し

### API エンドポイント
- [x] `POST /api/consultation/start` - 診断開始
- [x] `POST /api/consultation/answer` - 回答送信
- [x] `POST /api/consultation/reset` - リセット
- [x] `GET /api/consultation/status` - 現在の状態取得
- [x] `GET /api/consultation/questions` - 質問一覧取得
- [x] `GET /health` - ヘルスチェック

---

## 🔧 改善予定項目（優先度順）

### 🔥 高優先度（すぐ実装可能）
1. **戻るボタン機能** - 前の質問に戻れるようにする
2. **質問への補足説明** - 各質問にヘルプテキストを追加
3. **推論過程の可視化** - 適用されたルールを表示
4. **プログレスバー** - 診断の進行度を表示
5. **H-1Bビザの追加** - 需要の高いH-1Bビザのルール追加

### ⭐ 中優先度（ビジネス価値高い）
6. **PDF診断レポート出力** - 診断結果をPDFでダウンロード
7. **診断履歴の保存** - ローカルストレージに保存
8. **管理者ダッシュボード** - ルール管理・統計表示
9. **多言語対応（英語）** - 英語版の実装

### 🎯 長期的（本格運用向け）
10. **データベース導入** - PostgreSQL/MongoDB
11. **ユーザーアカウント管理** - ログイン機能
12. **料金プラン機能** - フリー/プレミアムプラン
13. **専門家への相談機能** - 診断結果から相談リクエスト
14. **利用統計・アナリティクス** - Google Analytics連携

---

## 🎯 推論エンジンの仕組み

### Smalltalkベースの設計思想
このシステムは `C:\Users\GPC999\Documents\works\Smalltalk資料.pdf` の
プロダクションシステム設計を参考にしています。

### 主要コンポーネント

#### 1. **Rule（ルール）**
- `name`: ルール番号/識別子
- `conditions`: 条件部（前件）
- `actions`: 結論部（後件）
- `type`: ルールタイプ
  - `#i`: 開始ルール（中間推論）
  - `#n!`: 終了ルール（最終結論）
- `condition_logic`: "AND" または "OR"
- `flag`: 発火状態（`#fire` / `#fired`）

#### 2. **WorkingMemory（作業記憶）**
- `findings`: ユーザーの回答（事実）
- `hypotheses`: 推論された仮説

#### 3. **Consultation（診断制御）**
- `collection_of_rules`: ルールの集合
- `conflict_set`: 競合集合（実行可能なルール）
- `status`: 作業記憶

### 推論プロセス

```
1. start_up() - 診断開始
   ↓
2. start_deduce() - 推論開始
   ↓
3. _check_if_impossible() - 否定的推論（申請不可チェック）
   ↓
4. _select_applicable_rules() - 競合集合を生成
   ↓
5. apply_rule() - ルールを適用
   ↓
6. _find_next_question() - 次の質問を探す
   ↓
7. ユーザーが回答 → status.set_finding()
   ↓
8. start_deduce() に戻る（ループ）
   ↓
9. 終了ルール適用 or 質問なし → 推論完了
```

### 効率的な質問選択
- **導出可能な仮説は質問しない** - 他のルールから推論できる内容は質問に含めない
- **OR条件の最適化** - OR条件のうち1つが満たされれば、残りは質問しない
- **不要な質問の排除** - 終了ルールに到達できない質問は行わない

---

## 📝 参考資料

### プロジェクト関連
- **Smalltalk資料**: `C:\Users\GPC999\Documents\works\Smalltalk資料.pdf`
- **ビザ選定知識**: `C:\Users\GPC999\documents\works\ビザ選定知識.txt`
- **システムイメージ**: `C:\Users\GPC999\documents\works\システムイメージ.txt`

### 開発環境
- **作業ディレクトリ**: `C:\Users\GPC999\Documents\visa-expert-system`
- **Git**: main ブランチ、origin = GitHub

---

## 🚧 既知の課題

1. **セッション管理**
   - 現在はグローバル変数で1セッションのみ対応
   - 複数ユーザー対応にはセッションストア（Redis等）が必要

2. **CORS設定**
   - 現在は `allow_origins=["*"]` で全許可
   - 本番環境では特定ドメインのみ許可すべき

3. **エラーハンドリング**
   - フロントエンドのエラー表示が簡素
   - リトライ機能なし

4. **テスト**
   - ユニットテストが未実装
   - E2Eテストが未実装

5. **パフォーマンス**
   - ルール数が増えると推論速度が低下する可能性
   - キャッシュ機能なし

---

## 💬 よくある作業パターン

### 新しい改善機能を追加する場合
```bash
# 1. プロジェクトディレクトリに移動
cd "C:\Users\GPC999\Documents\visa-expert-system"

# 2. 現在のブランチ確認
git status

# 3. ファイルを編集後、コミット
git add .
git commit -m "機能追加: [機能名]"
git push origin main

# 4. Renderが自動デプロイ（約5-10分）
```

### ローカルでテストする場合
```bash
# バックエンド起動
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# フロントエンド起動（別ターミナル）
cd frontend
npm install
npm start
```

### Renderダッシュボードにアクセス
```
https://dashboard.render.com/
```

---

## 📊 統計情報

- **総ルール数**: 30個
- **対応ビザタイプ**: 3種類（E, L, B）
- **質問候補数**: 約80個（ビザタイプによって異なる）
- **平均質問数**: 5-15個（効率的な推論により最小化）
- **コミット数**: 5+ （最新: "機能追加: フローチャートにAND/ORロジック表示"）

---

## 🎉 次回のセッションで使うコマンド例

```bash
# このファイルを読む
Read C:\Users\GPC999\Documents\visa-expert-system\PROJECT_STATUS.md

# プロジェクトの状況を確認
cd "C:\Users\GPC999\Documents\visa-expert-system"
git status
git log --oneline -5

# 改善作業を開始
「[具体的な改善内容] を実装してください」
```

---

**最終更新**: 2025年10月17日
**作成者**: Claude Code
**プロジェクトステータス**: デプロイ済み（改善段階）
