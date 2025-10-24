"""
質問の優先度を管理するデータベースモデル
"""
from sqlalchemy import Column, Integer, String, UniqueConstraint
from backend.database import Base, SessionLocal


class QuestionPriority(Base):
    """
    質問の優先度を管理するモデル
    """
    __tablename__ = 'question_priorities'
    __table_args__ = (
        UniqueConstraint('visa_type', 'question', name='uix_visa_question'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    visa_type = Column(String, nullable=False)  # E, L, B など
    question = Column(String, nullable=False)  # 質問文
    priority = Column(Integer, nullable=False, default=999)  # 優先度（小さいほど先）

    def to_dict(self):
        """辞書形式に変換"""
        return {
            'id': self.id,
            'visa_type': self.visa_type,
            'question': self.question,
            'priority': self.priority
        }


def init_db():
    """データベースを初期化"""
    from backend.database import init_db as database_init_db
    database_init_db()


def get_db():
    """データベースセッションを取得（ジェネレータ）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
