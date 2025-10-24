"""
質問優先度管理API
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.question_priority_db import QuestionPriority, get_db

router = APIRouter(prefix="/api/question-priorities", tags=["question-priorities"])


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

    優先度は、ファイナルルール（#n!）を導出するために必要な質問数が
    少ない順に設定されます。

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
        hypothesis_to_rules = {}  # 仮説 -> その仮説を導出するルールのマッピング

        for rule in rules:
            for action in rule.actions:
                derivable_hypotheses.add(action)
                if action not in hypothesis_to_rules:
                    hypothesis_to_rules[action] = []
                hypothesis_to_rules[action].append(rule)

        # ファイナルルール（#n!）を特定
        final_rules = [rule for rule in rules if rule.type == "#n!"]
        print(f"[DEBUG] ファイナルルール数: {len(final_rules)}")

        # 各ルールを導出するために必要な全質問を再帰的に収集する関数
        def collect_required_questions(rule, visited_rules=None):
            """
            あるルールを導出するために必要な全質問を再帰的に収集

            Args:
                rule: 対象のルール
                visited_rules: 循環参照を避けるために訪問済みルールを記録

            Returns:
                必要な質問のセット
            """
            if visited_rules is None:
                visited_rules = set()

            # 循環参照を避ける
            if rule.name in visited_rules:
                return set()

            visited_rules.add(rule.name)
            questions = set()

            for condition in rule.conditions:
                if condition in derivable_hypotheses:
                    # この条件は他のルールから導出される仮説
                    # そのルールの質問も再帰的に収集
                    if condition in hypothesis_to_rules:
                        for sub_rule in hypothesis_to_rules[condition]:
                            questions.update(collect_required_questions(sub_rule, visited_rules.copy()))
                else:
                    # この条件はユーザーに質問する必要がある
                    questions.add(condition)

            return questions

        # 各質問について、それが関連する最小の質問数を記録
        question_min_count = {}

        for final_rule in final_rules:
            required_questions = collect_required_questions(final_rule)
            question_count = len(required_questions)
            print(f"[DEBUG] {final_rule.name}: {question_count}個の質問が必要")

            for question in required_questions:
                if question not in question_min_count:
                    question_min_count[question] = question_count
                else:
                    # より少ない質問数で到達できるルートがあれば更新
                    question_min_count[question] = min(question_min_count[question], question_count)

        print(f"[DEBUG] 全質問数: {len(question_min_count)}")

        # 質問数が少ない順にソート（同じ質問数の場合はアルファベット順）
        sorted_questions = sorted(
            question_min_count.keys(),
            key=lambda q: (question_min_count[q], q)
        )

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
