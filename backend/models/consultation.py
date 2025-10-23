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
        self.applied_rules: List = []  # 適用されたルールの履歴
        self.pending_rules: List = []  # 評価待ちのルール（質問中）
        self.evaluating_rules: set = set()  # 推論が開始されたルール名のセット（fireするまで保持）
        self.history_stack: List[Dict[str, Any]] = []  # 各ステップのスナップショット

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
        self.pending_rules = []
        self.evaluating_rules = set()

        # 推論を開始
        return self.start_deduce()

    def start_deduce(self) -> Dict[str, Any]:
        """
        推論プロセスを開始

        Returns:
            推論結果
        """
        # 否定的推論: 申請不可の判定
        impossibility_result = self._check_if_impossible()
        if impossibility_result:
            return impossibility_result

        # 競合集合を生成
        self.conflict_set = self._select_applicable_rules()

        # 実行可能なルールがある場合は実行
        if self.conflict_set:
            selected_rule = self.conflict_set[0]
            return self.apply_rule(selected_rule)

        # 実行可能なルールがない場合、次に必要な質問を探す
        next_question = self._find_next_question()

        if next_question:
            # この質問を含む未発火ルールをpending_rulesに格納
            self.pending_rules = self._get_rules_with_condition(next_question)

            # pending_rulesのルールをevaluating_rulesに追加（推論が開始されたことを記録）
            for rule in self.pending_rules:
                self.evaluating_rules.add(rule.name)

            # pending_rulesのルールのアクション（結論）を条件として必要とするルールも追加
            # 例: ルール3のアクション"会社がEビザの条件を満たします"を条件として使うルール2も表示
            # 再帰的に依存ルールを追加（ルール3 → ルール2 → ルール1）
            def add_dependent_rules_recursively(actions_to_check):
                for action in actions_to_check:
                    dependent_rules = self._get_rules_that_need_hypothesis(action)
                    for dep_rule in dependent_rules:
                        if not dep_rule.is_fired() and dep_rule.name not in self.evaluating_rules:
                            self.evaluating_rules.add(dep_rule.name)
                            # さらにこのルールのアクションの依存ルールも追加
                            add_dependent_rules_recursively(dep_rule.actions)

            for rule in self.pending_rules:
                add_dependent_rules_recursively(rule.actions)

            # デバッグ情報
            pending_rule_names = [r.name for r in self.pending_rules]
            print(f"DEBUG: next_question='{next_question}'")
            print(f"DEBUG: pending_rules={pending_rule_names}")
            print(f"DEBUG: evaluating_rules={self.evaluating_rules}")

            reasoning_chain = self._build_reasoning_chain(next_question)
            print(f"DEBUG: reasoning_chain length={len(reasoning_chain)}")
            print(f"DEBUG: reasoning_chain rules={[r['rule_name'] for r in reasoning_chain]}")

            return {
                "status": "need_input",
                "message": "次の質問に答えてください",
                "question": next_question,
                "need_input": True,
                "reasoning_chain": reasoning_chain,
                "debug_pending_rules": pending_rule_names  # デバッグ用
            }

        # 質問もルールもない場合は推論完了
        return {
            "status": "completed",
            "message": "推論が完了しました",
            "results": dict(self.status.hypotheses),
            "need_input": False
        }

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
        # ルール適用時は pending_rules をクリア
        self.pending_rules = []

        # 適用されたルールの情報を記録
        rule_info = {
            "rule_name": rule.name,
            "rule_type": rule.type,
            "conditions": rule.conditions.copy(),
            "actions": rule.actions.copy(),
            "condition_logic": rule.condition_logic,
            "satisfied_conditions": {}
        }

        # 実際に回答された条件だけを記録（未回答の条件は除外）
        for condition in rule.conditions:
            # findingsまたはhypothesesに存在する条件のみ記録
            if self.status.has_key(condition):
                value = self.status.get_value(condition)
                rule_info["satisfied_conditions"][condition] = value

        self.applied_rules.append(rule_info)

        # ルールのアクションを実行
        rule.execute_actions(self.status)

        # ルールを発火済みにする
        rule.hoist_flag()

        # evaluating_rulesからは削除しない（fireしたルールも表示し続けるため）

        # ルールのタイプに応じて次の処理を決定
        if rule.type == "#n!":  # 終了ルール
            return {
                "status": "completed",
                "message": "推論が完了しました",
                "results": dict(self.status.hypotheses),
                "need_input": False,
                "applied_rule": rule.name,
                "applied_rules": self.applied_rules
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

    def _get_rules_that_need_hypothesis(self, hypothesis: str) -> List:
        """
        指定された仮説を条件として必要とするルールを取得

        Args:
            hypothesis: 仮説（ルールのアクション）

        Returns:
            この仮説を条件とするルールのリスト
        """
        rules_needing_hypothesis = []
        for rule in self.collection_of_rules.values():
            if rule.is_fired():
                continue
            if hypothesis in rule.conditions:
                rules_needing_hypothesis.append(rule)
        return rules_needing_hypothesis

    def _get_rules_with_condition(self, condition: str) -> List:
        """
        指定された条件を含む未発火のルールを取得
        AND条件のルールで、他の条件が既にFalseになっている場合は除外

        Args:
            condition: 条件（質問）

        Returns:
            この条件を含むルールのリスト
        """
        rules_with_condition = []
        for rule in self.collection_of_rules.values():
            if rule.is_fired():
                continue
            if condition in rule.conditions:
                # AND条件のルールの場合、他の条件が既にFalseになっていないかチェック
                if rule.condition_logic == "AND":
                    can_be_satisfied = True
                    for cond in rule.conditions:
                        if cond == condition:
                            # 今質問している条件はスキップ
                            continue
                        value = self.status.get_value(cond)
                        # 他の条件が明示的にFalseの場合、このルールは適用不可
                        if value is False:
                            can_be_satisfied = False
                            break
                    if not can_be_satisfied:
                        # このルールは除外
                        continue

                rules_with_condition.append(rule)
        return rules_with_condition

    def _is_hypothesis_needed(self, hypothesis: str) -> bool:
        """
        この仮説が必要かどうかを再帰的にチェック
        この仮説を使うルールのいずれかが満たされていない場合、必要

        Args:
            hypothesis: チェックする仮説

        Returns:
            仮説が必要な場合 True、不要な場合 False
        """
        # この仮説を条件として使うルールを探す
        dependent_rules = self._get_rules_that_need_hypothesis(hypothesis)

        # 依存するルールがない場合、この仮説は不要
        if not dependent_rules:
            return False

        # いずれかの依存ルールが満たされていないかチェック
        for rule in dependent_rules:
            # このルールが既に満たされているかチェック
            if not rule.check_conditions(self.status):
                # まだ満たされていない
                # このルールのアクションが更に必要とされているかチェック
                for action in rule.actions:
                    if self._is_hypothesis_needed(action):
                        return True
                # このルールのアクションが不要でも、ルール自体が終了ルールなら必要
                if rule.type == "#n!":
                    return True

        # すべての依存ルールが既に満たされている
        return False

    def _is_question_necessary(self, condition: str) -> bool:
        """
        この質問が本当に必要かチェック
        この質問を含むルール、およびその結果を使うルールをチェック
        AND条件のルールで、他の条件が既にFalseになっている場合は不要

        Args:
            condition: チェックする条件

        Returns:
            質問が必要な場合 True、不要な場合 False
        """
        # この条件を含むルールをチェック
        for rule in self.collection_of_rules.values():
            if rule.is_fired():
                continue

            if condition not in rule.conditions:
                continue

            # AND条件のルールの場合、他の条件が既にFalseになっていないかチェック
            if rule.condition_logic == "AND":
                can_be_satisfied = True
                for cond in rule.conditions:
                    if cond == condition:
                        # 今チェックしている条件はスキップ
                        continue
                    value = self.status.get_value(cond)
                    # 他の条件が明示的にFalseの場合、このルールは適用不可
                    if value is False:
                        can_be_satisfied = False
                        break
                if not can_be_satisfied:
                    # このルールは適用不可なので、この質問は不要（次のルールをチェック）
                    continue

            # このルールが既に満たされているかチェック
            if not rule.check_conditions(self.status):
                # まだ満たされていない
                # このルールのアクション（仮説）が必要とされているかチェック
                for action in rule.actions:
                    if self._is_hypothesis_needed(action):
                        return True
                # アクションが不要でも、ルール自体が終了ルールなら必要
                if rule.type == "#n!":
                    return True

        # すべてのルールで不要
        return False

    def _check_if_impossible(self) -> Optional[Dict[str, Any]]:
        """
        否定的推論: 申請が不可能かどうかをチェック
        終了ルール（#n!）が絶対に適用できない場合、申請不可と判定

        Returns:
            申請不可の場合は結果辞書、そうでない場合は None
        """
        # 終了ルール（#n!）を探す
        terminal_rules = [rule for rule in self.collection_of_rules.values() if rule.type == "#n!"]

        for rule in terminal_rules:
            # このルールが既に発火済みならスキップ
            if rule.is_fired():
                continue

            # ルールの条件をチェック
            can_be_satisfied = True
            for condition in rule.conditions:
                value = self.status.get_value(condition)

                # 条件が明示的に False の場合
                if value is False:
                    can_be_satisfied = False
                    break

            # このルールが絶対に適用できないと判明した場合
            if not can_be_satisfied:
                return {
                    "status": "impossible",
                    "message": "現在の条件では申請ができません",
                    "results": {},
                    "need_input": False
                }

        return None

    def _find_next_question(self) -> Optional[str]:
        """
        次に必要な質問を見つける
        他のルールから導出できる仮説は質問せず、基本的な事実のみを質問する
        OR条件で他の条件が既に満たされている場合も質問しない

        Returns:
            次に尋ねるべき質問、なければ None
        """
        # すべてのルールのアクション（導出可能な仮説）を収集
        derivable_hypotheses = set()
        for rule in self.collection_of_rules.values():
            derivable_hypotheses.update(rule.actions)

        # すべてのルールの条件をチェック
        for rule_name, rule in self.collection_of_rules.items():
            # 既に発火したルールはスキップ
            if rule.is_fired():
                continue

            # ルールの条件を確認
            for condition in rule.conditions:
                # まだ回答されていない（WorkingMemoryにない）質問を探す
                if not self.status.has_key(condition):
                    # 他のルールから導出できる仮説は質問しない
                    if condition not in derivable_hypotheses:
                        # OR条件で他の条件が既に満たされている場合も質問しない
                        if self._is_question_necessary(condition):
                            return condition

        return None

    def reset(self) -> None:
        """
        診断をリセット
        """
        self.status.clear()
        self.conflict_set = []
        self.applied_rules = []  # 適用ルール履歴もリセット
        self.pending_rules = []  # 評価待ちルールもリセット
        self.evaluating_rules = set()  # 評価中ルールもリセット
        self.history_stack = []  # 履歴スタックもリセット

        # すべてのルールの flag をリセット
        for rule in self.collection_of_rules.values():
            rule.flag = "#fire"

    def save_snapshot(self) -> None:
        """
        現在の診断状態のスナップショットを保存
        ユーザーが回答する前の状態を保存して、後で戻れるようにする
        """
        import copy

        # 現在の状態をディープコピーして保存
        snapshot = {
            "findings": copy.deepcopy(self.status.findings),
            "hypotheses": copy.deepcopy(self.status.hypotheses),
            "applied_rules": copy.deepcopy(self.applied_rules),
            "rule_flags": {rule_name: rule.flag for rule_name, rule in self.collection_of_rules.items()},
            "evaluating_rules": copy.deepcopy(self.evaluating_rules)
        }
        self.history_stack.append(snapshot)

    def go_back(self) -> Dict[str, Any]:
        """
        前の質問に戻る
        履歴スタックから前の状態を復元して、その時点の質問を返す

        Returns:
            前の質問の情報、または戻れない場合はエラー情報
        """
        if not self.history_stack:
            return {
                "status": "error",
                "message": "これ以上戻れません",
                "need_input": False
            }

        # 最後のスナップショットを取り出す
        snapshot = self.history_stack.pop()

        # 状態を復元
        self.status.findings = snapshot["findings"]
        self.status.hypotheses = snapshot["hypotheses"]
        self.applied_rules = snapshot["applied_rules"]
        self.evaluating_rules = snapshot.get("evaluating_rules", set())

        # ルールのフラグを復元
        for rule_name, flag in snapshot["rule_flags"].items():
            if rule_name in self.collection_of_rules:
                self.collection_of_rules[rule_name].flag = flag

        # 復元後に推論を実行して次の質問を取得
        return self.start_deduce()

    def _build_reasoning_chain(self, current_question: str) -> List[Dict[str, Any]]:
        """
        評価中のルールチェーンを構築
        evaluating_rulesに含まれる全てのルール（fireしたものも含む）を表示

        Args:
            current_question: 現在の質問

        Returns:
            推論チェーン情報のリスト（優先度順）
        """
        # evaluating_rulesに含まれる全てのルールを取得（fireしたものも含む）
        chain_rules = []
        for rule_name in self.evaluating_rules:
            if rule_name in self.collection_of_rules:
                rule = self.collection_of_rules[rule_name]
                chain_rules.append(rule)

        # 優先度順にソート
        chain_rules.sort(key=lambda r: r.priority)

        # ルール情報を構築
        chain = []
        for rule in chain_rules:
            rule_info = {
                "rule_name": rule.name,
                "rule_type": rule.type,
                "condition_logic": rule.condition_logic,
                "conditions": [],
                "actions": rule.actions.copy(),
                "is_fired": rule.is_fired(),  # fireしたかどうか
                "priority": rule.priority  # 優先度
            }

            # 各条件の状態を評価
            for condition in rule.conditions:
                condition_info = {
                    "text": condition,
                    "status": "unknown",
                    "is_current": condition == current_question
                }

                if condition == current_question:
                    condition_info["status"] = "current"
                else:
                    value = self.status.get_value(condition)
                    if value is True:
                        condition_info["status"] = "satisfied"
                    elif value is False:
                        condition_info["status"] = "unsatisfied"
                    else:
                        condition_info["status"] = "unknown"

                rule_info["conditions"].append(condition_info)

            chain.append(rule_info)

        return chain
