"""
Rule クラス
ルールの基本構造を定義するクラス
"""
from typing import List, Callable, Any
from abc import ABC, abstractmethod


class Rule(ABC):
    """
    ルールの抽象クラス
    各ルールはこのクラスを継承して実装する
    """

    def __init__(
        self,
        name: str,
        conditions: List[str],
        actions: List[str],
        rule_type: str = "#i",
        flag: str = "#fire",
        condition_logic: str = "AND",
        priority: int = 0
    ):
        """
        ルールの初期化

        Args:
            name: ルールの名前（番号、識別子）
            conditions: ルールの条件部
            actions: ルールの結論部
            rule_type: ルールのタイプ（#i: 開始ルール、#m: 問結ルール、#n!: 終了ルール）
            flag: ルールの発火状態を示す
            condition_logic: 条件のロジック（"AND" または "OR"）
            priority: 優先度（小さいほど優先）
        """
        self.name = name
        self.conditions = conditions
        self.actions = actions
        self.type = rule_type
        self.flag = flag
        self.condition_logic = condition_logic
        self.priority = priority

    @abstractmethod
    def check_conditions(self, working_memory) -> bool:
        """
        ルールの条件部をチェックする抽象メソッド
        各ルールで具体的な条件チェックを実装

        Args:
            working_memory: 作業記憶（WorkingMemory インスタンス）

        Returns:
            条件が満たされた場合 True、そうでない場合 False
        """
        pass

    @abstractmethod
    def execute_actions(self, working_memory) -> None:
        """
        ルールのアクション部を実行する抽象メソッド
        各ルールで具体的なアクションを実装

        Args:
            working_memory: 作業記憶（WorkingMemory インスタンス）
        """
        pass

    def try_rule(self, working_memory) -> bool:
        """
        ルールの条件要素を引数とする

        Args:
            working_memory: 作業記憶

        Returns:
            条件が満たされた場合 True、そうでない場合 False
        """
        return self.check_conditions(working_memory)

    def hoist_flag(self) -> None:
        """
        一度活性化したルールに対して、それが再度競合集合に
        入ることによって、それ以降のルールの適用時に識別する
        ための指標とする
        """
        self.flag = "#fired"

    def is_fired(self) -> bool:
        """
        ルールが既に発火したかどうかをチェック

        Returns:
            発火済みの場合 True、そうでない場合 False
        """
        return self.flag == "#fired"

    def __repr__(self):
        return f"Rule(name={self.name}, type={self.type}, flag={self.flag})"
