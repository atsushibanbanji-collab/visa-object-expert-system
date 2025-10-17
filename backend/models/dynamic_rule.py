"""
データベースから動的にRuleオブジェクトを生成するファクトリー
"""
from backend.models.rule import Rule
from backend.models.rule_db import RuleDB


class DynamicRule(Rule):
    """
    データベースから読み込んだ情報を使って動的に生成されるルール
    """

    def __init__(self, rule_db: RuleDB):
        """
        データベースのルール情報からRuleオブジェクトを作成

        Args:
            rule_db: データベースのルールモデル
        """
        self.rule_db = rule_db
        self._conditions = rule_db.get_conditions_list()
        self._actions = rule_db.get_actions_list()

        super().__init__(
            name=rule_db.name,
            conditions=self._conditions,
            actions=self._actions,
            rule_type=rule_db.rule_type,
            condition_logic=rule_db.condition_logic
        )

    def check_conditions(self, working_memory) -> bool:
        """
        条件をチェック

        Args:
            working_memory: 作業記憶

        Returns:
            条件が満たされている場合 True、そうでない場合 False
        """
        if self.condition_logic == "OR":
            # OR条件: いずれか1つでも満たされていればTrue
            for condition in self._conditions:
                value = working_memory.get_value(condition)
                if value:
                    return True
            return False
        else:
            # AND条件: すべて満たされている必要がある
            for condition in self._conditions:
                value = working_memory.get_value(condition)
                if not value:
                    return False
            return True

    def execute_actions(self, working_memory) -> None:
        """
        アクションを実行（仮説を導出）

        Args:
            working_memory: 作業記憶
        """
        for action in self._actions:
            working_memory.put_value_of_hypothesis(action, True)


def create_rule_from_db(rule_db: RuleDB) -> DynamicRule:
    """
    データベースのルールからRuleオブジェクトを作成

    Args:
        rule_db: データベースのルールモデル

    Returns:
        DynamicRuleインスタンス
    """
    return DynamicRule(rule_db)
