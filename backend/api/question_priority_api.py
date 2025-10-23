"""
質問優先度管理API
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.question_priority_db import QuestionPriority, get_db, init_db

router = APIRouter(prefix="/api/question-priorities", tags=["question-priorities"])

# 起動時にテーブルを作成
init_db()


class QuestionPriorityUpdate(BaseModel):
    """質問優先度更新リクエスト"""
    id: int
    priority: int


class QuestionPriorityResponse(BaseModel):
    """質問優先度レスポンス"""
    id: int
    visa_type: str
    question: str
    priority: int


@router.get("", response_model=List[QuestionPriorityResponse])
def get_question_priorities(visa_type: str, db: Session = Depends(get_db)):
    """
    指定されたビザタイプの質問優先度一覧を取得

    Args:
        visa_type: ビザタイプ（E, L, B など）
        db: データベースセッション

    Returns:
        質問優先度のリスト
    """
    priorities = db.query(QuestionPriority).filter(
        QuestionPriority.visa_type == visa_type
    ).order_by(QuestionPriority.priority).all()

    return [p.to_dict() for p in priorities]


@router.put("/{question_id}")
def update_question_priority(
    question_id: int,
    update: QuestionPriorityUpdate,
    db: Session = Depends(get_db)
):
    """
    質問の優先度を更新

    Args:
        question_id: 質問ID
        update: 更新内容
        db: データベースセッション

    Returns:
        更新後の質問優先度
    """
    priority = db.query(QuestionPriority).filter(QuestionPriority.id == question_id).first()

    if not priority:
        raise HTTPException(status_code=404, detail="Question priority not found")

    priority.priority = update.priority
    db.commit()
    db.refresh(priority)

    return priority.to_dict()


@router.post("/initialize")
def initialize_question_priorities(visa_type: str, db: Session = Depends(get_db)):
    """
    質問優先度を初期化（全ての質問をデータベースに登録）

    Args:
        visa_type: ビザタイプ（E, L, B など）
        db: データベースセッション

    Returns:
        初期化された質問数
    """
    from backend.rules.visa_rules import get_rules_by_visa_type

    # ルールを取得
    rules = get_rules_by_visa_type(visa_type)

    # 既存の質問を取得
    existing_questions = {
        p.question: p for p in db.query(QuestionPriority).filter(
            QuestionPriority.visa_type == visa_type
        ).all()
    }

    # すべてのルールのアクション（導出可能な仮説）を収集
    derivable_hypotheses = set()
    for rule in rules:
        derivable_hypotheses.update(rule.actions)

    # すべてのルールの条件から質問を抽出
    questions = set()
    for rule in rules:
        for condition in rule.conditions:
            # 他のルールから導出できる仮説は質問ではない
            if condition not in derivable_hypotheses:
                questions.add(condition)

    # 質問を優先度順に並べる（デフォルトは出現順）
    added_count = 0
    for index, question in enumerate(sorted(questions)):
        if question not in existing_questions:
            # 新しい質問を追加
            new_priority = QuestionPriority(
                visa_type=visa_type,
                question=question,
                priority=index
            )
            db.add(new_priority)
            added_count += 1

    db.commit()

    return {"added": added_count, "total": len(questions)}
