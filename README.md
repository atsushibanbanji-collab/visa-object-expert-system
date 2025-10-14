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

Renderを使用してデプロイします。
