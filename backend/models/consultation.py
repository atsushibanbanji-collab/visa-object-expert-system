"""
Consultation クラス
診断を制御するクラス
"""
from typing import List, Optional, Dict, Any
from collections import OrderedDict


class Consultation:
    """
    診断を制御するクラス
    """

    def __init__(self, rules: List):
        """
        Consultation の初期化

        Args:
            rules: ルールのリスト
        """
        from .working_memory import WorkingMemory

        self.status: WorkingMemory = WorkingMemory()
        self.collection_of_rules: OrderedDict = OrderedDict()
        self.conflict_set: List = []

        # ルールをコレクションに追加
        for rule in rules:
            self.collection_of_rules[rule.name] = rule

    def start_up(self) -> Dict[str, Any]:
        """
        推論を開始する

        Returns:
            推論結果
        """
        # 競合集合を初期化
        self.conflict_set = []

        # 推論を開始
        return self.start_deduce()

    def start_deduce(self) -> Dict[str, Any]:
        """
        推論プロセスを開始

        Returns:
            推論結果
        """
        # 競合集合が空かチェック
        if not self.conflict_set:
            result = self.deduce_first()
        else:
            result = self.deduce_second()

        return result

    def deduce_first(self) -> Dict[str, Any]:
        """
        最初の推論ステップ
        競合集合を作成し、最初のルールを適用する

        Returns:
            推論結果
        """
        # 競合集合を生成
        self.conflict_set = self._select_applicable_rules()

        # 競合集合が空の場合
        if not self.conflict_set:
            return {
                "status": "completed",
                "message": "推論が完了しました",
                "results": dict(self.status.hypotheses),
                "need_input": False
            }

        # 最初のルールを選択して実行
        selected_rule = self.conflict_set[0]
        return self.apply_rule(selected_rule)

    def deduce_second(self) -> Dict[str, Any]:
        """
        2回目以降の推論ステップ

        Returns:
            推論結果
        """
        # 競合集合を再生成
        self.conflict_set = self._select_applicable_rules()

        # 競合集合が空の場合
        if not self.conflict_set:
            return {
                "status": "completed",
                "message": "推論が完了しました",
                "results": dict(self.status.hypotheses),
                "need_input": False
            }

        # 次のルールを選択して実行
        selected_rule = self.conflict_set[0]
        return self.apply_rule(selected_rule)

    def deduce_third(self) -> Dict[str, Any]:
        """
        3回目の推論ステップ（バッチ型処理で複数のルールが同時に適用される場合）

        Returns:
            推論結果
        """
        # ルールのタイプが"#i"（開始型）の場合に該当
        # この実装では deduce_second と同様に処理
        return self.deduce_second()

    def apply_rule(self, rule) -> Dict[str, Any]:
        """
        選択されたルールを適用

        Args:
            rule: 適用するルール

        Returns:
            ルール適用結果
        """
        # ルールのアクションを実行
        rule.execute_actions(self.status)

        # ルールを発火済みにする
        rule.hoist_flag()

        # ルールのタイプに応じて次の処理を決定
        if rule.type == "#n!":  # 終了ルール
            return {
                "status": "completed",
                "message": "推論が完了しました",
                "results": dict(self.status.hypotheses),
                "need_input": False,
                "applied_rule": rule.name
            }
        else:
            # 次の推論ステップへ
            return self.start_deduce()

    def _select_applicable_rules(self) -> List:
        """
        実行可能なルールを選択して競合集合を作成

        Returns:
            実行可能なルールのリスト
        """
        applicable_rules = []

        for rule_name, rule in self.collection_of_rules.items():
            # 既に発火したルールはスキップ
            if rule.is_fired():
                continue

            # 条件をチェック
            if rule.check_conditions(self.status):
                applicable_rules.append(rule)

        return applicable_rules

    def check_all(self, conditions: List[str]) -> bool:
        """
        すべての条件が満たされているかチェック

        Args:
            conditions: チェックする条件のリスト

        Returns:
            すべての条件が満たされている場合 True、そうでない場合 False
        """
        for condition in conditions:
            value = self.status.get_value(condition)
            if not value:
                return False
        return True

    def reset(self) -> None:
        """
        診断をリセット
        """
        self.status.clear()
        self.conflict_set = []

        # すべてのルールの flag をリセット
        for rule in self.collection_of_rules.values():
            rule.flag = "#fire"
