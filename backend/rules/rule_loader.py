"""
データベースからルールを読み込む
"""
from typing import List
from backend.database import SessionLocal
from backend.models.rule_db import RuleDB
from backend.models.dynamic_rule import create_rule_from_db
from backend.models.rule import Rule


def get_rules_from_db(visa_type: str = None) -> List[Rule]:
    """
    データベースからルールを読み込む

    Args:
        visa_type: ビザタイプ（"E", "L", "B" など）。Noneの場合は全ルールを取得

    Returns:
        Ruleオブジェクトのリスト
    """
    db = SessionLocal()
    try:
        query = db.query(RuleDB)

        # ビザタイプでフィルタ
        if visa_type:
            query = query.filter(
                (RuleDB.visa_type == visa_type) | (RuleDB.visa_type == "ALL")
            )

        # 優先順位順にソート
        query = query.order_by(RuleDB.priority)

        # データベースからルールを取得
        rule_dbs = query.all()

        # DynamicRuleオブジェクトに変換
        rules = [create_rule_from_db(rule_db) for rule_db in rule_dbs]

        return rules

    finally:
        db.close()


def get_rules_by_visa_type_from_db(visa_type: str) -> List[Rule]:
    """
    指定されたビザタイプに関連するルールをデータベースから取得

    Args:
        visa_type: ビザタイプ（"E", "L", "B"）

    Returns:
        指定されたビザタイプに関連するルールのリスト
    """
    return get_rules_from_db(visa_type)
