"""
Consultation API エンドポイント
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from backend.models.consultation import Consultation
from backend.rules.visa_rules import get_rules_by_visa_type

router = APIRouter(prefix="/api/consultation", tags=["consultation"])

# グローバルな診断セッション（本番環境ではセッション管理が必要）
consultation_session: Optional[Consultation] = None


class StartRequest(BaseModel):
    """診断開始リクエスト"""
    visa_type: str  # "E", "L", "B"


class AnswerRequest(BaseModel):
    """回答リクエスト"""
    key: str
    value: Any


class ConsultationResponse(BaseModel):
    """診断レスポンス"""
    status: str
    message: str
    results: Optional[Dict[str, Any]] = None
    need_input: bool
    applied_rule: Optional[str] = None
    question: Optional[str] = None


@router.post("/start", response_model=ConsultationResponse)
def start_consultation(request: StartRequest):
    """
    新しい診断セッションを開始

    Args:
        request: visa_type を含む開始リクエスト

    Returns:
        診断開始レスポンス
    """
    global consultation_session

    # 選択されたビザタイプのルールのみを取得
    rules = get_rules_by_visa_type(request.visa_type)

    # 新しい診断セッションを作成
    consultation_session = Consultation(rules)

    # 推論を開始
    result = consultation_session.start_up()

    return ConsultationResponse(**result)


@router.post("/answer", response_model=ConsultationResponse)
def submit_answer(request: AnswerRequest):
    """
    ユーザーの回答を記録して推論を進める

    Args:
        request: 回答リクエスト

    Returns:
        推論結果
    """
    global consultation_session

    if consultation_session is None:
        raise HTTPException(status_code=400, detail="診断セッションが開始されていません")

    # ユーザーの回答を作業記憶に記録
    consultation_session.status.set_finding(request.key, request.value)

    # 推論を進める
    result = consultation_session.start_deduce()

    return ConsultationResponse(**result)


@router.get("/status", response_model=Dict[str, Any])
def get_status():
    """
    現在の診断状態を取得

    Returns:
        現在の作業記憶（findings と hypotheses）
    """
    global consultation_session

    if consultation_session is None:
        raise HTTPException(status_code=400, detail="診断セッションが開始されていません")

    return {
        "findings": consultation_session.status.findings,
        "hypotheses": consultation_session.status.hypotheses
    }


@router.post("/reset")
def reset_consultation():
    """
    診断をリセット

    Returns:
        リセット完了メッセージ
    """
    global consultation_session

    if consultation_session is not None:
        consultation_session.reset()

    return {"message": "診断がリセットされました"}


@router.get("/questions")
def get_all_questions():
    """
    各ビザタイプの質問一覧を取得

    Returns:
        ビザタイプごとのルールと質問のリスト
    """
    visa_types = {
        "E": "Eビザ（投資家・貿易駐在員）",
        "L": "Lビザ（企業内転勤者）",
        "B": "Bビザ（商用・観光）"
    }

    result = {}

    for visa_type, visa_name in visa_types.items():
        rules = get_rules_by_visa_type(visa_type)

        rules_data = []
        all_conditions = set()

        for rule in rules:
            rule_data = {
                "name": rule.name,
                "type": rule.type,
                "conditions": rule.conditions,
                "actions": rule.actions,
                "condition_logic": rule.condition_logic
            }
            rules_data.append(rule_data)
            all_conditions.update(rule.conditions)

        result[visa_type] = {
            "name": visa_name,
            "rules": rules_data,
            "all_questions": sorted(list(all_conditions))
        }

    return result
