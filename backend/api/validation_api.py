"""
ルール検証API エンドポイント
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.rule_db import RuleDB
from typing import List, Dict, Set
from pydantic import BaseModel

router = APIRouter(prefix="/api/validation", tags=["validation"])


class AutoFixRequest(BaseModel):
    """自動修正リクエスト"""
    visa_type: str
    fix_type: str  # "dependency_order"
    violations: List[Dict]


def find_circular_dependencies(rules: List[RuleDB]) -> List[Dict]:
    """
    循環参照を検出

    Args:
        rules: ルールのリスト

    Returns:
        循環参照のリスト
    """
    circular_refs = []

    # 各ルールのアクション→条件のマッピングを作成
    action_to_rules = {}  # アクション -> そのアクションを使用するルール
    rule_to_actions = {}  # ルール -> そのルールが生成するアクション

    for rule in rules:
        rule_to_actions[rule.name] = rule.get_actions_list()

        for condition in rule.get_conditions_list():
            if condition not in action_to_rules:
                action_to_rules[condition] = []
            action_to_rules[condition].append(rule.name)

    # 深さ優先探索で循環を検出
    def dfs(rule_name: str, path: List[str], visited: Set[str]) -> bool:
        if rule_name in path:
            # 循環を発見
            cycle_start = path.index(rule_name)
            cycle = path[cycle_start:] + [rule_name]
            circular_refs.append({
                "cycle": cycle,
                "description": " → ".join(cycle)
            })
            return True

        if rule_name in visited:
            return False

        visited.add(rule_name)
        path.append(rule_name)

        # このルールが生成するアクションを使用する他のルールを探索
        if rule_name in rule_to_actions:
            for action in rule_to_actions[rule_name]:
                if action in action_to_rules:
                    for dependent_rule in action_to_rules[action]:
                        if dfs(dependent_rule, path.copy(), visited):
                            return True

        return False

    visited_global = set()
    for rule in rules:
        if rule.name not in visited_global:
            dfs(rule.name, [], visited_global)

    return circular_refs


def find_unreachable_rules(rules: List[RuleDB]) -> List[Dict]:
    """
    到達不能なルールを検出

    Args:
        rules: ルールのリスト

    Returns:
        到達不能なルールのリスト
    """
    unreachable = []

    # すべてのアクション（導出可能な仮説）を収集
    all_actions = set()
    for rule in rules:
        all_actions.update(rule.get_actions_list())

    # 各ルールについて、その条件がすべて導出可能かチェック
    for rule in rules:
        conditions = rule.get_conditions_list()
        unreachable_conditions = []

        for condition in conditions:
            # この条件が他のルールのアクションとして導出可能か、または基本的な質問か
            if condition not in all_actions:
                # 基本的な質問（ユーザーに聞く質問）の可能性があるのでOK
                continue
            else:
                # このアクションを生成するルールが存在するか確認
                can_be_derived = False
                for other_rule in rules:
                    if rule.name == other_rule.name:
                        continue
                    if condition in other_rule.get_actions_list():
                        can_be_derived = True
                        break

                if not can_be_derived:
                    unreachable_conditions.append(condition)

        if unreachable_conditions:
            unreachable.append({
                "rule_name": rule.name,
                "rule_type": rule.rule_type,
                "unreachable_conditions": unreachable_conditions,
                "description": f"ルール {rule.name}: 条件 '{', '.join(unreachable_conditions)}' が導出不可能"
            })

    return unreachable


def check_rule_consistency(rules: List[RuleDB]) -> List[Dict]:
    """
    ルールの整合性をチェック

    Args:
        rules: ルールのリスト

    Returns:
        整合性エラーのリスト
    """
    errors = []

    # 重複したルール名のチェック
    rule_names = {}
    for rule in rules:
        if rule.name in rule_names:
            errors.append({
                "type": "duplicate_name",
                "rule_name": rule.name,
                "description": f"ルール名 '{rule.name}' が重複しています"
            })
        rule_names[rule.name] = True

    # 空の条件・アクションのチェック
    for rule in rules:
        if not rule.get_conditions_list():
            errors.append({
                "type": "empty_conditions",
                "rule_name": rule.name,
                "description": f"ルール {rule.name}: 条件が空です"
            })

        if not rule.get_actions_list():
            errors.append({
                "type": "empty_actions",
                "rule_name": rule.name,
                "description": f"ルール {rule.name}: アクションが空です"
            })

    # 終了ルールのチェック（少なくとも1つは必要）
    terminal_rules = [r for r in rules if r.rule_type == "#n!"]
    if not terminal_rules:
        errors.append({
            "type": "no_terminal_rules",
            "description": "終了ルール (#n!) が1つもありません"
        })

    return errors


def check_dependency_order(rules: List[RuleDB]) -> List[Dict]:
    """
    依存関係の順序をチェック
    アクションを生成するルールが、そのアクションを条件として使うルールより前（priority が小さい）にあるかを確認

    Args:
        rules: ルールのリスト

    Returns:
        順序違反のリスト
    """
    violations = []

    # アクション → そのアクションを生成するルールのマッピング
    action_to_producer = {}
    for rule in rules:
        for action in rule.get_actions_list():
            if action not in action_to_producer:
                action_to_producer[action] = []
            action_to_producer[action].append(rule)

    # 各ルールについて、その条件が他のルールのアクションの場合、順序をチェック
    for rule in rules:
        for condition in rule.get_conditions_list():
            # この条件が他のルールのアクションとして生成される場合
            if condition in action_to_producer:
                for producer_rule in action_to_producer[condition]:
                    # 自分自身は除外
                    if producer_rule.name == rule.name:
                        continue

                    # producer_rule が rule より後ろにある（priority が大きい）場合は違反
                    if producer_rule.priority > rule.priority:
                        violations.append({
                            "type": "wrong_order",
                            "producer_rule": producer_rule.name,
                            "producer_priority": producer_rule.priority,
                            "consumer_rule": rule.name,
                            "consumer_priority": rule.priority,
                            "action": condition,
                            "description": f"ルール {producer_rule.name} (priority={producer_rule.priority}) が '{condition}' を生成しますが、それを条件として使うルール {rule.name} (priority={rule.priority}) より後ろにあります"
                        })

    return violations


@router.get("/check")
def validate_rules(visa_type: str = None, db: Session = Depends(get_db)):
    """
    ルールを検証

    Args:
        visa_type: ビザタイプでフィルタ（オプション）
        db: データベースセッション

    Returns:
        検証結果
    """
    query = db.query(RuleDB)

    if visa_type:
        query = query.filter(
            (RuleDB.visa_type == visa_type) | (RuleDB.visa_type == "ALL")
        )

    rules = query.all()

    # 各種検証を実行
    consistency_errors = check_rule_consistency(rules)
    circular_dependencies = find_circular_dependencies(rules)
    unreachable_rules = find_unreachable_rules(rules)
    dependency_order_violations = check_dependency_order(rules)

    # 警告とエラーをカウント
    error_count = len(consistency_errors) + len(dependency_order_violations)
    warning_count = len(circular_dependencies) + len(unreachable_rules)

    return {
        "total_rules": len(rules),
        "visa_type": visa_type or "ALL",
        "status": "error" if error_count > 0 else ("warning" if warning_count > 0 else "ok"),
        "error_count": error_count,
        "warning_count": warning_count,
        "consistency_errors": consistency_errors,
        "circular_dependencies": circular_dependencies,
        "unreachable_rules": unreachable_rules,
        "dependency_order_violations": dependency_order_violations
    }


@router.post("/auto-fix")
def auto_fix_violations(request: AutoFixRequest, db: Session = Depends(get_db)):
    """
    検証エラーを自動修正

    Args:
        request: 修正リクエスト
        db: データベースセッション

    Returns:
        修正結果
    """
    if request.fix_type == "dependency_order":
        return fix_dependency_order(request.violations, request.visa_type, db)
    else:
        raise HTTPException(status_code=400, detail=f"未対応の修正タイプ: {request.fix_type}")


def fix_dependency_order(violations: List[Dict], visa_type: str, db: Session) -> Dict:
    """
    依存関係の順序違反を自動修正
    consumer_ruleのpriorityを、producer_ruleより大きい値に変更（後ろに配置）

    Args:
        violations: 順序違反のリスト
        visa_type: ビザタイプ
        db: データベースセッション

    Returns:
        修正結果
    """
    if not violations:
        return {
            "success": False,
            "message": "修正する違反がありません"
        }

    changes = []
    modified_rules = set()

    for violation in violations:
        consumer_name = violation["consumer_rule"]
        producer_priority = violation["producer_priority"]

        # consumer_ruleを取得
        consumer_rule = db.query(RuleDB).filter(
            RuleDB.name == consumer_name,
            (RuleDB.visa_type == visa_type) | (RuleDB.visa_type == "ALL")
        ).first()

        if not consumer_rule:
            continue

        # 既に修正済みの場合はスキップ
        if consumer_rule.name in modified_rules:
            continue

        # 新しいpriorityを計算（producer_priorityより10大きくする）
        old_priority = consumer_rule.priority
        new_priority = producer_priority + 10

        # priorityを更新
        consumer_rule.priority = new_priority
        modified_rules.add(consumer_rule.name)

        changes.append({
            "rule_name": consumer_rule.name,
            "old_priority": old_priority,
            "new_priority": new_priority,
            "reason": f"ルール {violation['producer_rule']} (priority={producer_priority}) より後ろに配置"
        })

    # 変更をコミット
    db.commit()

    return {
        "success": True,
        "message": f"{len(changes)}個のルールを修正しました",
        "changes": changes
    }
