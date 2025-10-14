"""
WorkingMemory クラス
作業記憶（findings, hypotheses）を管理するクラス
"""
from typing import Dict, Any


class WorkingMemory:
    """
    作業記憶クラス
    診断に関する状態、知見（findings）、仮説（hypotheses）を保持する
    """

    def __init__(self):
        """
        インスタンス変数を初期化
        """
        self.findings: Dict[str, Any] = {}      # ユーザーの回答（事実）
        self.hypotheses: Dict[str, Any] = {}    # 推論結果（仮説）

    def get_value(self, key: str) -> Any:
        """
        作業記憶から指定された要素の値を取り出して返す
        ユーザーに問い合わせはしない

        Args:
            key: 取得する要素のキー

        Returns:
            findings または hypotheses に含まれる値、存在しない場合は None
        """
        if key in self.findings:
            return self.findings[key]
        elif key in self.hypotheses:
            return self.hypotheses[key]
        else:
            return None

    def get_value_all(self, key: str) -> Any:
        """
        作業記憶から指定された要素の値を取り出して返す
        存在しない場合はユーザーに問い合わせる（実際の実装では別途処理）

        Args:
            key: 取得する要素のキー

        Returns:
            findings または hypotheses に含まれる値
        """
        return self.get_value(key)

    def put_value_of_hypothesis(self, key: str, value: Any) -> None:
        """
        仮説記憶へ追加

        Args:
            key: 追加する要素のキー
            value: 追加する値
        """
        self.hypotheses[key] = value

    def has_key(self, key: str) -> bool:
        """
        指定されたキーが存在するかチェック

        Args:
            key: チェックするキー

        Returns:
            キーが存在する場合 True、そうでない場合 False
        """
        return key in self.findings or key in self.hypotheses

    def set_finding(self, key: str, value: Any) -> None:
        """
        知見（事実）を設定

        Args:
            key: 設定する要素のキー
            value: 設定する値
        """
        self.findings[key] = value

    def clear(self) -> None:
        """
        作業記憶をクリア
        """
        self.findings.clear()
        self.hypotheses.clear()
