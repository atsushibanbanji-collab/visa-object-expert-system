"""
データベース接続設定
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# データベースファイルのパス
# 環境変数DATABASE_DIRが設定されている場合はそれを使用（本番環境）
# 設定されていない場合はローカルのdataディレクトリを使用（開発環境）
DATABASE_DIR = os.getenv("DATABASE_DIR", os.path.join(os.path.dirname(__file__), "data"))
os.makedirs(DATABASE_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'visa_rules.db')}"

# SQLAlchemyエンジンの作成
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite用
)

# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラス
Base = declarative_base()


def get_db():
    """
    データベースセッションを取得

    Yields:
        データベースセッション
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    データベースを初期化（テーブルを作成）
    """
    Base.metadata.create_all(bind=engine)
