"""
ルールのデータベースモデル
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from backend.database import Base
import json


class RuleDB(Base):
    """
    ルールのデータベースモデル
    """
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    visa_type = Column(String, nullable=False)  # "E", "L", "B", or "ALL"
    rule_type = Column(String, nullable=False)  # "#n!" or "#i"
    condition_logic = Column(String, default="AND")  # "AND" or "OR"
    conditions = Column(Text, nullable=False)  # JSON string
    actions = Column(Text, nullable=False)  # JSON string
    priority = Column(Integer, default=0)  # 質問の優先順位（小さいほど優先）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        """
        辞書形式に変換

        Returns:
            辞書形式のルール情報
        """
        return {
            "id": self.id,
            "name": self.name,
            "visa_type": self.visa_type,
            "rule_type": self.rule_type,
            "condition_logic": self.condition_logic,
            "conditions": json.loads(self.conditions),
            "actions": json.loads(self.actions),
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def get_conditions_list(self):
        """
        条件をリストとして取得

        Returns:
            条件のリスト
        """
        return json.loads(self.conditions)

    def get_actions_list(self):
        """
        アクションをリストとして取得

        Returns:
            アクションのリスト
        """
        return json.loads(self.actions)

    @classmethod
    def from_dict(cls, data):
        """
        辞書からRuleDBインスタンスを作成

        Args:
            data: ルール情報の辞書

        Returns:
            RuleDBインスタンス
        """
        return cls(
            name=data["name"],
            visa_type=data["visa_type"],
            rule_type=data["rule_type"],
            condition_logic=data.get("condition_logic", "AND"),
            conditions=json.dumps(data["conditions"], ensure_ascii=False),
            actions=json.dumps(data["actions"], ensure_ascii=False),
            priority=data.get("priority", 0)
        )
