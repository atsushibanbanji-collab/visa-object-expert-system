"""
質問の優先度を管理するデータベースモデル
"""
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()


class QuestionPriority(Base):
    """
    質問の優先度を管理するモデル
    """
    __tablename__ = 'question_priorities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    visa_type = Column(String, nullable=False)  # E, L, B など
    question = Column(String, nullable=False, unique=True)  # 質問文
    priority = Column(Integer, nullable=False, default=999)  # 優先度（小さいほど先）

    def to_dict(self):
        """辞書形式に変換"""
        return {
            'id': self.id,
            'visa_type': self.visa_type,
            'question': self.question,
            'priority': self.priority
        }


# データベース接続の設定
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./visa_expert.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """データベースを初期化"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """データベースセッションを取得"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
