"""
質問優先度管理API
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.question_priority_db import QuestionPriority, get_db

router = APIRouter(prefix="/api/question-priorities", tags=["question-priorities"])


@router.post("/reset-table")
def reset_question_priorities_table():
    """
    質問優先度テーブルを削除して再作成する

    注意: すべての質問優先度データが削除されます

    Returns:
        リセット完了メッセージ
    """
    try:
        from backend.models.question_priority_db import QuestionPriority
        from backend.database import engine

        # テーブルを削除
        QuestionPriority.__table__.drop(engine, checkfirst=True)
        print("[DEBUG] question_priorities テーブルを削除しました")

        # テーブルを再作成
        QuestionPriority.__table__.create(engine, checkfirst=True)
        print("[DEBUG] question_priorities テーブルを再作成しました")

        return {"message": "質問優先度テーブルをリセットしました"}
    except Exception as e:
        print(f"[ERROR] テーブルのリセットに失敗: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"テーブルのリセットに失敗しました: {str(e)}")


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

    シンプルに五十音順（アルファベット順）で登録します。
    ユーザーは質問順序管理画面でドラッグ&ドロップで自由に並べ替えできます。

    Args:
        visa_type: ビザタイプ（E, L, B など）
        db: データベースセッション

    Returns:
        初期化された質問数
    """
    try:
        from backend.rules.visa_rules import get_rules_by_visa_type

        # ルールを取得
        rules = get_rules_by_visa_type(visa_type)
        print(f"[DEBUG] ルール数: {len(rules)}")

        # 既存の質問を取得
        existing_questions = {
            p.question: p for p in db.query(QuestionPriority).filter(
                QuestionPriority.visa_type == visa_type
            ).all()
        }
        print(f"[DEBUG] 既存の質問数: {len(existing_questions)}")

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

        print(f"[DEBUG] 全質問数: {len(questions)}")

        # シンプルに五十音順（アルファベット順）でソート
        sorted_questions = sorted(questions)

        # データベースに保存
        added_count = 0
        updated_count = 0

        for index, question in enumerate(sorted_questions):
            if question in existing_questions:
                # 既存の質問の優先度を更新
                existing_questions[question].priority = index
                updated_count += 1
            else:
                # 新しい質問を追加
                new_priority = QuestionPriority(
                    visa_type=visa_type,
                    question=question,
                    priority=index
                )
                db.add(new_priority)
                added_count += 1

        db.commit()
        print(f"[DEBUG] 保存完了: added={added_count}, updated={updated_count}")

        return {
            "added": added_count,
            "updated": updated_count,
            "total": len(sorted_questions)
        }
    except Exception as e:
        print(f"[ERROR] 質問優先度の初期化に失敗: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"質問優先度の初期化に失敗しました: {str(e)}")
