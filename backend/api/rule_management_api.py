"""
ルール管理API エンドポイント
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.rule_db import RuleDB
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
