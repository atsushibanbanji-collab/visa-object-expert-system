from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.consultation_api import router as consultation_router
from backend.rules.visa_rules import get_rules_by_visa_type

app = FastAPI(title="Visa Expert System API")

# CORS設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルールキャッシュ：アプリ起動時に全ビザタイプのルールを事前生成
print("🚀 Initializing rules cache...")
RULES_CACHE = {
    "E": get_rules_by_visa_type("E"),
    "L": get_rules_by_visa_type("L"),
    "B": get_rules_by_visa_type("B"),
}
print(f"✅ Rules cache initialized: E={len(RULES_CACHE['E'])} rules, L={len(RULES_CACHE['L'])} rules, B={len(RULES_CACHE['B'])} rules")

# APIルーターを登録（ルールキャッシュを渡す）
app.include_router(consultation_router)

@app.get("/")
def read_root():
    return {"message": "Visa Expert System API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/health")
def api_health_check():
    """フロントエンドのプリウォームアップ用"""
    return {"status": "healthy", "rules_cached": len(RULES_CACHE)}
