from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.consultation_api import router as consultation_router

app = FastAPI(title="Visa Expert System API")

# CORS設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターを登録
app.include_router(consultation_router)

@app.get("/")
def read_root():
    return {"message": "Visa Expert System API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
