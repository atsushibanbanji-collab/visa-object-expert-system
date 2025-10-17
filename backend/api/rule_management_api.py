"""
ルール管理API エンドポイント
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.rule_db import RuleDB
from datetime import datetime
import json

router = APIRouter(prefix="/api/rules", tags=["rule_management"])


class RuleCreateRequest(BaseModel):
    """ルール作成リクエスト"""
    name: str
    visa_type: str  # "E", "L", "B", "H", "J", "ALL"
    rule_type: str  # "#n!" or "#i"
    condition_logic: str = "AND"  # "AND" or "OR"
    conditions: List[str]
    actions: List[str]
    priority: int = 0


class RuleUpdateRequest(BaseModel):
    """ルール更新リクエスト"""
    name: Optional[str] = None
    visa_type: Optional[str] = None
    rule_type: Optional[str] = None
    condition_logic: Optional[str] = None
    conditions: Optional[List[str]] = None
    actions: Optional[List[str]] = None
    priority: Optional[int] = None


class RuleResponse(BaseModel):
    """ルールレスポンス"""
    id: int
    name: str
    visa_type: str
    rule_type: str
    condition_logic: str
    conditions: List[str]
    actions: List[str]
    priority: int
    created_at: Optional[str]
    updated_at: Optional[str]


@router.get("", response_model=List[RuleResponse])
def get_all_rules(
    visa_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    すべてのルールを取得

    Args:
        visa_type: ビザタイプでフィルタ（オプション）
        db: データベースセッション

    Returns:
        ルールのリスト
    """
    query = db.query(RuleDB)

    if visa_type:
        query = query.filter(
            (RuleDB.visa_type == visa_type) | (RuleDB.visa_type == "ALL")
        )

    query = query.order_by(RuleDB.priority)
    rules = query.all()

    return [rule.to_dict() for rule in rules]


@router.get("/{rule_id}", response_model=RuleResponse)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    """
    指定されたIDのルールを取得

    Args:
        rule_id: ルールID
        db: データベースセッション

    Returns:
        ルール情報
    """
    rule = db.query(RuleDB).filter(RuleDB.id == rule_id).first()

    if not rule:
        raise HTTPException(status_code=404, detail="ルールが見つかりません")

    return rule.to_dict()


@router.post("", response_model=RuleResponse)
def create_rule(request: RuleCreateRequest, db: Session = Depends(get_db)):
    """
    新しいルールを作成

    Args:
        request: ルール作成リクエスト
        db: データベースセッション

    Returns:
        作成されたルール情報
    """
    # 同じ名前のルールが既に存在するかチェック
    existing_rule = db.query(RuleDB).filter(RuleDB.name == request.name).first()
    if existing_rule:
        raise HTTPException(status_code=400, detail="同じ名前のルールが既に存在します")

    # ルールを作成
    rule = RuleDB(
        name=request.name,
        visa_type=request.visa_type,
        rule_type=request.rule_type,
        condition_logic=request.condition_logic,
        conditions=json.dumps(request.conditions, ensure_ascii=False),
        actions=json.dumps(request.actions, ensure_ascii=False),
        priority=request.priority
    )

    db.add(rule)
    db.commit()
    db.refresh(rule)

    return rule.to_dict()


@router.put("/{rule_id}", response_model=RuleResponse)
def update_rule(
    rule_id: int,
    request: RuleUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    ルールを更新

    Args:
        rule_id: ルールID
        request: ルール更新リクエスト
        db: データベースセッション

    Returns:
        更新されたルール情報
    """
    rule = db.query(RuleDB).filter(RuleDB.id == rule_id).first()

    if not rule:
        raise HTTPException(status_code=404, detail="ルールが見つかりません")

    # 更新
    if request.name is not None:
        # 名前の重複チェック
        existing = db.query(RuleDB).filter(
            RuleDB.name == request.name,
            RuleDB.id != rule_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="同じ名前のルールが既に存在します")
        rule.name = request.name

    if request.visa_type is not None:
        rule.visa_type = request.visa_type

    if request.rule_type is not None:
        rule.rule_type = request.rule_type

    if request.condition_logic is not None:
        rule.condition_logic = request.condition_logic

    if request.conditions is not None:
        rule.conditions = json.dumps(request.conditions, ensure_ascii=False)

    if request.actions is not None:
        rule.actions = json.dumps(request.actions, ensure_ascii=False)

    if request.priority is not None:
        rule.priority = request.priority

    db.commit()
    db.refresh(rule)

    return rule.to_dict()


@router.delete("/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """
    ルールを削除

    Args:
        rule_id: ルールID
        db: データベースセッション

    Returns:
        削除完了メッセージ
    """
    rule = db.query(RuleDB).filter(RuleDB.id == rule_id).first()

    if not rule:
        raise HTTPException(status_code=404, detail="ルールが見つかりません")

    db.delete(rule)
    db.commit()

    return {"message": f"ルール{rule.name}を削除しました"}


@router.put("/reorder")
def reorder_rules(rule_ids: List[int], db: Session = Depends(get_db)):
    """
    ルールの順序を変更

    Args:
        rule_ids: 新しい順序でのルールIDのリスト
        db: データベースセッション

    Returns:
        更新完了メッセージ
    """
    for index, rule_id in enumerate(rule_ids):
        rule = db.query(RuleDB).filter(RuleDB.id == rule_id).first()
        if rule:
            rule.priority = index

    db.commit()

    return {"message": f"{len(rule_ids)}個のルールの順序を更新しました"}


@router.get("/export")
def export_rules(visa_type: Optional[str] = None, db: Session = Depends(get_db)):
    """
    ルールをJSON形式でエクスポート

    Args:
        visa_type: ビザタイプでフィルタ（オプション）
        db: データベースセッション

    Returns:
        JSON形式のルールデータ
    """
    query = db.query(RuleDB)

    if visa_type:
        query = query.filter(
            (RuleDB.visa_type == visa_type) | (RuleDB.visa_type == "ALL")
        )

    query = query.order_by(RuleDB.priority)
    rules = query.all()

    # エクスポート用のデータ形式に変換
    export_data = {
        "version": "1.0",
        "exported_at": datetime.now().isoformat(),
        "visa_type": visa_type or "ALL",
        "rules": [
            {
                "name": rule.name,
                "visa_type": rule.visa_type,
                "rule_type": rule.rule_type,
                "condition_logic": rule.condition_logic,
                "conditions": rule.get_conditions_list(),
                "actions": rule.get_actions_list(),
                "priority": rule.priority
            }
            for rule in rules
        ]
    }

    return export_data


class ImportRequest(BaseModel):
    """ルールインポートリクエスト"""
    rules: List[dict]
    overwrite: bool = False  # 既存ルールを上書きするか


@router.post("/import")
def import_rules(request: ImportRequest, db: Session = Depends(get_db)):
    """
    JSON形式のルールをインポート

    Args:
        request: インポートリクエスト
        db: データベースセッション

    Returns:
        インポート結果
    """
    imported_count = 0
    skipped_count = 0
    updated_count = 0
    errors = []

    for rule_data in request.rules:
        try:
            # 必須フィールドのチェック
            required_fields = ["name", "visa_type", "rule_type", "conditions", "actions"]
            for field in required_fields:
                if field not in rule_data:
                    errors.append(f"ルール {rule_data.get('name', 'unknown')}: {field} が不足しています")
                    continue

            # 同じ名前のルールが既に存在するかチェック
            existing_rule = db.query(RuleDB).filter(RuleDB.name == rule_data["name"]).first()

            if existing_rule:
                if request.overwrite:
                    # 上書き
                    existing_rule.visa_type = rule_data["visa_type"]
                    existing_rule.rule_type = rule_data["rule_type"]
                    existing_rule.condition_logic = rule_data.get("condition_logic", "AND")
                    existing_rule.conditions = json.dumps(rule_data["conditions"], ensure_ascii=False)
                    existing_rule.actions = json.dumps(rule_data["actions"], ensure_ascii=False)
                    existing_rule.priority = rule_data.get("priority", existing_rule.priority)
                    updated_count += 1
                else:
                    # スキップ
                    skipped_count += 1
                    continue
            else:
                # 新規作成
                new_rule = RuleDB(
                    name=rule_data["name"],
                    visa_type=rule_data["visa_type"],
                    rule_type=rule_data["rule_type"],
                    condition_logic=rule_data.get("condition_logic", "AND"),
                    conditions=json.dumps(rule_data["conditions"], ensure_ascii=False),
                    actions=json.dumps(rule_data["actions"], ensure_ascii=False),
                    priority=rule_data.get("priority", 0)
                )
                db.add(new_rule)
                imported_count += 1

        except Exception as e:
            errors.append(f"ルール {rule_data.get('name', 'unknown')}: {str(e)}")

    db.commit()

    return {
        "message": "インポートが完了しました",
        "imported": imported_count,
        "updated": updated_count,
        "skipped": skipped_count,
        "errors": errors
    }
