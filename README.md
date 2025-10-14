# Visa Expert System

オブジェクト指向プロダクションシステムを使用した米国ビザ選定エキスパートシステム

## 技術スタック

- **Backend**: Python + FastAPI
- **Frontend**: React
- **Deploy**: Render

## プロジェクト構造

```
visa-expert-system/
├── backend/
│   ├── models/          # WorkingMemory, Rule, Consultation クラス
│   ├── rules/           # 31個のビザルール定義
│   ├── api/             # FastAPI エンドポイント
│   └── main.py          # エントリポイント
├── frontend/            # React アプリケーション
└── README.md
```

## セットアップ

### バックエンド

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### フロントエンド

```bash
cd frontend
npm install
npm start
```

## デプロイ

### Renderでのデプロイ手順

1. **GitHubリポジトリを準備**
   - このリポジトリをGitHubにプッシュ済み

2. **Renderダッシュボードにアクセス**
   - https://dashboard.render.com/

3. **新しいBlueprint作成**
   - 「New +」→ 「Blueprint」を選択
   - GitHubリポジトリを接続
   - `visa-object-expert-system` を選択
   - `render.yaml` が自動的に検出されます

4. **デプロイ開始**
   - 「Apply」をクリック
   - バックエンドとフロントエンドが自動的にデプロイされます

5. **公開URL**
   - バックエンド: `https://visa-expert-backend.onrender.com`
   - フロントエンド: `https://visa-expert-frontend.onrender.com`

### 手動デプロイ（render.yaml を使わない場合）

**バックエンド:**
- Type: Web Service
- Environment: Python 3
- Build Command: `pip install -r backend/requirements.txt`
- Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

**フロントエンド:**
- Type: Static Site
- Build Command: `cd frontend && npm install && npm run build`
- Publish Directory: `frontend/build`
