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


@router.get("/debug")
def debug_question_priorities(visa_type: str = "E"):
    """
    質問優先度のデバッグ情報を取得

    Args:
        visa_type: ビザタイプ（E, L, B など）

    Returns:
        デバッグ情報
    """
    from backend.rules.visa_rules import get_rules_by_visa_type

    # ルールを取得
    rules = get_rules_by_visa_type(visa_type)

    # すべてのルールのアクション（導出可能な仮説）を収集
    derivable_hypotheses = set()
    hypothesis_to_rules = {}

    for rule in rules:
        for action in rule.actions:
            derivable_hypotheses.add(action)
            if action not in hypothesis_to_rules:
                hypothesis_to_rules[action] = []
            hypothesis_to_rules[action].append(rule.name)

    # ファイナルルール（#n!）を特定
    final_rules = [rule for rule in rules if rule.type == "#n!"]

    # 各ルールを導出するために必要な全質問を再帰的に収集する関数
    def collect_required_questions(rule, visited_rules=None):
        if visited_rules is None:
            visited_rules = set()

        if rule.name in visited_rules:
            return set()

        visited_rules.add(rule.name)
        questions = set()

        for condition in rule.conditions:
            if condition in derivable_hypotheses:
                if condition in hypothesis_to_rules:
                    for sub_rule_name in hypothesis_to_rules[condition]:
                        sub_rule = next((r for r in rules if r.name == sub_rule_name), None)
                        if sub_rule:
                            questions.update(collect_required_questions(sub_rule, visited_rules.copy()))
            else:
                questions.add(condition)

        return questions

    # 各質問について、関連するファイナルルール数と最小質問数を記録
    question_stats = {}
    final_rule_details = []

    for final_rule in final_rules:
        required_questions = collect_required_questions(final_rule)
        question_count = len(required_questions)

        final_rule_details.append({
            "rule_name": final_rule.name,
            "question_count": question_count,
            "questions": list(required_questions)
        })

        for question in required_questions:
            if question not in question_stats:
                question_stats[question] = {
                    "rule_count": 0,
                    "min_questions": question_count,
                    "related_rules": []
                }

            question_stats[question]["rule_count"] += 1
            question_stats[question]["related_rules"].append(final_rule.name)
            question_stats[question]["min_questions"] = min(
                question_stats[question]["min_questions"],
                question_count
            )

    # 優先度順にソート
    sorted_questions = sorted(
        question_stats.keys(),
        key=lambda q: (-question_stats[q]["rule_count"], question_stats[q]["min_questions"], q)
    )

    # トップ10
    top_10 = []
    for i, q in enumerate(sorted_questions[:10]):
        stats = question_stats[q]
        top_10.append({
            "priority": i,
            "question": q,
            "rule_count": stats["rule_count"],
            "min_questions": stats["min_questions"],
            "related_rules": stats["related_rules"]
        })

    return {
        "visa_type": visa_type,
        "total_rules": len(rules),
        "final_rules_count": len(final_rules),
        "total_questions": len(question_stats),
        "final_rule_details": final_rule_details,
        "top_10_questions": top_10
    }


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

    優先度は以下の基準で決定されます:
    1. より多くのファイナルルール（診断結果）に関連する質問を優先
    2. 同じ関連数の場合、最小質問数が少ない方を優先
    3. それも同じ場合はアルファベット順

    この方式により、国籍のような多くの診断結果に共通する基本的な質問が
    優先的に表示されます。

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

        # 各質問について、関連するファイナルルール数と最小質問数を記録
        question_stats = {}  # {質問: {"rule_count": X, "min_questions": Y}}

        for final_rule in final_rules:
            required_questions = collect_required_questions(final_rule)
            question_count = len(required_questions)
            print(f"[DEBUG] {final_rule.name}: {question_count}個の質問が必要")

            for question in required_questions:
                if question not in question_stats:
                    question_stats[question] = {
                        "rule_count": 0,
                        "min_questions": question_count
                    }

                # この質問が関連するファイナルルール数をカウント
                question_stats[question]["rule_count"] += 1

                # より少ない質問数で到達できるルートがあれば更新
                question_stats[question]["min_questions"] = min(
                    question_stats[question]["min_questions"],
                    question_count
                )

        print(f"[DEBUG] 全質問数: {len(question_stats)}")

        # 優先度の計算ロジック:
        # 1. より多くのファイナルルールに関連する質問を優先（rule_countが大きい順）
        # 2. 同じrule_countの場合、最小質問数が少ない方を優先
        # 3. それも同じ場合はアルファベット順
        sorted_questions = sorted(
            question_stats.keys(),
            key=lambda q: (-question_stats[q]["rule_count"], question_stats[q]["min_questions"], q)
        )

        # デバッグ: トップ10の質問を表示
        print("[DEBUG] 優先度トップ10:")
        for i, q in enumerate(sorted_questions[:10]):
            stats = question_stats[q]
            print(f"  {i}: {q} (ルール数:{stats['rule_count']}, 最小質問数:{stats['min_questions']})")

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
