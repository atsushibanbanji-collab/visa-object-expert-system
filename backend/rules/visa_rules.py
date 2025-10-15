"""
ビザ選定のための31個のルール実装
"""
from backend.models.rule import Rule


class VisaRule1(Rule):
    """
    ルール1: Eビザでの申請が可能かチェック
    条件: 申請者と会社の国籍が同じ、会社がEビザ条件を満たす、申請者がEビザ条件を満たす
    """
    def __init__(self):
        super().__init__(
            name="1",
            conditions=[
                "申請者と会社の国籍が同じです",
                "会社がEビザの条件を満たします",
                "申請者がEビザの条件を満たします"
            ],
            actions=["Eビザでの申請ができます"],
            rule_type="#n!"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("申請者と会社の国籍が同じです")
        cond2 = working_memory.get_value("会社がEビザの条件を満たします")
        cond3 = working_memory.get_value("申請者がEビザの条件を満たします")
        return cond1 and cond2 and cond3

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("Eビザでの申請ができます", True)


class VisaRule2(Rule):
    """
    ルール2: 会社がEビザの条件を満たすかチェック
    条件: 投資条件 OR 貿易条件
    """
    def __init__(self):
        super().__init__(
            name="2",
            conditions=[
                "会社がEビザの投資の条件を満たします",
                "会社がEビザの貿易の条件を満たします"
            ],
            actions=["会社がEビザの条件を満たします"],
            rule_type="#i",
            condition_logic="OR"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("会社がEビザの投資の条件を満たします")
        cond2 = working_memory.get_value("会社がEビザの貿易の条件を満たします")
        return cond1 or cond2

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("会社がEビザの条件を満たします", True)


class VisaRule3(Rule):
    """
    ルール3: 会社がEビザの投資条件を満たすかチェック
    """
    def __init__(self):
        super().__init__(
            name="3",
            conditions=[
                "減価償却前の設備や建物が30万ドル以上財務諸表の資産に計上されています",
                "30万ドル以上で企業を買収した会社か、買収された会社です",
                "まだ十分な売り上げがなく、これまでに人件費などのランニングコストを含め、30万ドル以上支出しています",
                "会社設立のために、30万ドル以上支出しました（不動産を除く）"
            ],
            actions=["会社がEビザの投資の条件を満たします"],
            rule_type="#i",
            condition_logic="OR"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("減価償却前の設備や建物が30万ドル以上財務諸表の資産に計上されています")
        cond2 = working_memory.get_value("30万ドル以上で企業を買収した会社か、買収された会社です")
        cond3 = working_memory.get_value("まだ十分な売り上げがなく、これまでに人件費などのランニングコストを含め、30万ドル以上支出しています")
        cond4 = working_memory.get_value("会社設立のために、30万ドル以上支出しました（不動産を除く）")
        return cond1 or cond2 or cond3 or cond4

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("会社がEビザの投資の条件を満たします", True)


class VisaRule4(Rule):
    """
    ルール4: 会社がEビザの貿易条件を満たすかチェック
    """
    def __init__(self):
        super().__init__(
            name="4",
            conditions=[
                "会社の行う貿易の50％が日米間です",
                "会社の行う貿易は継続的です",
                "貿易による利益が会社の経費の80％以上をカバーしています"
            ],
            actions=["会社がEビザの貿易の条件を満たします"],
            rule_type="#i"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("会社の行う貿易の50％が日米間です")
        cond2 = working_memory.get_value("会社の行う貿易は継続的です")
        cond3 = working_memory.get_value("貿易による利益が会社の経費の80％以上をカバーしています")
        return cond1 and cond2 and cond3

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("会社がEビザの貿易の条件を満たします", True)


class VisaRule5(Rule):
    """
    ルール5: 申請者がEビザの条件を満たすかチェック
    """
    def __init__(self):
        super().__init__(
            name="5",
            conditions=[
                "申請者がEビザのマネージャー以上の条件を満たします",
                "申請者がEビザのスタッフの条件を満たします",
                "EビザTDY(short-term needs)の条件を満たします"
            ],
            actions=["申請者がEビザの条件を満たします"],
            rule_type="#i",
            condition_logic="OR"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("申請者がEビザのマネージャー以上の条件を満たします")
        cond2 = working_memory.get_value("申請者がEビザのスタッフの条件を満たします")
        cond3 = working_memory.get_value("EビザTDY(short-term needs)の条件を満たします")
        return cond1 or cond2 or cond3

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("申請者がEビザの条件を満たします", True)


class VisaRule6(Rule):
    """
    ルール6: 申請者がEビザのマネージャー以上の条件を満たすかチェック
    """
    def __init__(self):
        super().__init__(
            name="6",
            conditions=[
                "米国拠点でEビザでマネージャー以上として認められるポジションに就きます",
                "マネージャー以上のポジションの業務を遂行する十分な能力があります"
            ],
            actions=["申請者がEビザのマネージャー以上の条件を満たします"],
            rule_type="#i"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("米国拠点でEビザでマネージャー以上として認められるポジションに就きます")
        cond2 = working_memory.get_value("マネージャー以上のポジションの業務を遂行する十分な能力があります")
        return cond1 and cond2

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("申請者がEビザのマネージャー以上の条件を満たします", True)


class VisaRule7(Rule):
    """
    ルール7: 米国拠点でEビザでマネージャー以上として認められるポジションかチェック
    """
    def __init__(self):
        super().__init__(
            name="7",
            conditions=[
                "CEOなどのオフィサーのポジションに就きます",
                "経営企画のマネージャーなど、米国拠点の経営に関わるポジションに就きます",
                "評価・雇用に責任を持つ複数のフルタイムのスタッフを部下に持つマネージャー以上のポジションに就きます"
            ],
            actions=["米国拠点でEビザでマネージャー以上として認められるポジションに就きます"],
            rule_type="#i",
            condition_logic="OR"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("CEOなどのオフィサーのポジションに就きます")
        cond2 = working_memory.get_value("経営企画のマネージャーなど、米国拠点の経営に関わるポジションに就きます")
        cond3 = working_memory.get_value("評価・雇用に責任を持つ複数のフルタイムのスタッフを部下に持つマネージャー以上のポジションに就きます")
        return cond1 or cond2 or cond3

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("米国拠点でEビザでマネージャー以上として認められるポジションに就きます", True)


class VisaRule8(Rule):
    """
    ルール8: マネージャー以上のポジションの業務を遂行する十分な能力があるかチェック
    """
    def __init__(self):
        super().__init__(
            name="8",
            conditions=[
                "米国拠点のポジションの業務に深く関連する業務の経験が2年以上あります",
                "マネジメント経験が2年以上あります"
            ],
            actions=["マネージャー以上のポジションの業務を遂行する十分な能力があります"],
            rule_type="#i"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("米国拠点のポジションの業務に深く関連する業務の経験が2年以上あります")
        cond2 = working_memory.get_value("マネジメント経験が2年以上あります")
        return cond1 and cond2

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("マネージャー以上のポジションの業務を遂行する十分な能力があります", True)


class VisaRule9(Rule):
    """
    ルール9: マネジメント経験が2年以上あるかチェック
    """
    def __init__(self):
        super().__init__(
            name="9",
            conditions=[
                "2年以上のマネージャー経験があります",
                "マネジメントが求められるプロジェクトマネージャーなどの2年以上の経験があります"
            ],
            actions=["マネジメント経験が2年以上あります"],
            rule_type="#i",
            condition_logic="OR"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("2年以上のマネージャー経験があります")
        cond2 = working_memory.get_value("マネジメントが求められるプロジェクトマネージャーなどの2年以上の経験があります")
        return cond1 or cond2

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("マネジメント経験が2年以上あります", True)


class VisaRule10(Rule):
    """
    ルール10: 申請者がEビザのスタッフの条件を満たすかチェック
    """
    def __init__(self):
        super().__init__(
            name="10",
            conditions=[
                "理系の大学院卒で、米国拠点の技術系の業務に深く関連する3年以上の業務経験があります",
                "理系の学部卒で、米国拠点の技術系の業務に深く関連する4年以上の業務経験があります",
                "米国拠点の業務に深く関連する5年以上の業務経験があります"
            ],
            actions=["申請者がEビザのスタッフの条件を満たします"],
            rule_type="#i",
            condition_logic="OR"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("理系の大学院卒で、米国拠点の技術系の業務に深く関連する3年以上の業務経験があります")
        cond2 = working_memory.get_value("理系の学部卒で、米国拠点の技術系の業務に深く関連する4年以上の業務経験があります")
        cond3 = working_memory.get_value("米国拠点の業務に深く関連する5年以上の業務経験があります")
        return cond1 or cond2 or cond3

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("申請者がEビザのスタッフの条件を満たします", True)


class VisaRule11(Rule):
    """
    ルール11: EビザTDY(short-term needs)の条件を満たすかチェック
    """
    def __init__(self):
        super().__init__(
            name="11",
            conditions=[
                "2年以内の期間で、目的を限定した派遣理由を説明できます",
                "米国拠点の業務に深く関連する2年以上の業務経験があります"
            ],
            actions=["EビザTDY(short-term needs)の条件を満たします"],
            rule_type="#i"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("2年以内の期間で、目的を限定した派遣理由を説明できます")
        cond2 = working_memory.get_value("米国拠点の業務に深く関連する2年以上の業務経験があります")
        return cond1 and cond2

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("EビザTDY(short-term needs)の条件を満たします", True)


class VisaRule12(Rule):
    """
    ルール12: Blanket Lビザでの申請が可能かチェック
    """
    def __init__(self):
        super().__init__(
            name="12",
            conditions=[
                "アメリカ以外からアメリカへのグループ内での異動です",
                "会社がBlanket Lビザの条件を満たします",
                "申請者がBlanket Lビザの条件を満たします"
            ],
            actions=["Blanket Lビザでの申請ができます"],
            rule_type="#n!"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("アメリカ以外からアメリカへのグループ内での異動です")
        cond2 = working_memory.get_value("会社がBlanket Lビザの条件を満たします")
        cond3 = working_memory.get_value("申請者がBlanket Lビザの条件を満たします")
        return cond1 and cond2 and cond3

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("Blanket Lビザでの申請ができます", True)


class VisaRule13(Rule):
    """
    ルール13: 会社がBlanket Lビザの条件を満たすかチェック
    """
    def __init__(self):
        super().__init__(
            name="13",
            conditions=[
                "アメリカにある子会社の売り上げの合計が25百万ドル以上です",
                "アメリカにある子会社が1,000人以上ローカル採用をしています",
                "1年間に10人以上Lビザのペティション申請をしています"
            ],
            actions=["会社がBlanket Lビザの条件を満たします"],
            rule_type="#i",
            condition_logic="OR"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("アメリカにある子会社の売り上げの合計が25百万ドル以上です")
        cond2 = working_memory.get_value("アメリカにある子会社が1,000人以上ローカル採用をしています")
        cond3 = working_memory.get_value("1年間に10人以上Lビザのペティション申請をしています")
        return cond1 or cond2 or cond3

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("会社がBlanket Lビザの条件を満たします", True)


class VisaRule14(Rule):
    """
    ルール14: 申請者がBlanket Lビザの条件を満たすかチェック
    """
    def __init__(self):
        super().__init__(
            name="14",
            conditions=[
                "直近3年のうち1年以上、アメリカ以外のグループ会社に所属していました",
                "Blanket Lビザのマネージャーまたはスタッフの条件を満たします"
            ],
            actions=["申請者がBlanket Lビザの条件を満たします"],
            rule_type="#i"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("直近3年のうち1年以上、アメリカ以外のグループ会社に所属していました")
        cond2 = working_memory.get_value("Blanket Lビザのマネージャーまたはスタッフの条件を満たします")
        return cond1 and cond2

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("申請者がBlanket Lビザの条件を満たします", True)


class VisaRule15(Rule):
    """
    ルール15: Blanket Lビザのマネージャーまたはスタッフの条件を満たすかチェック
    """
    def __init__(self):
        super().__init__(
            name="15",
            conditions=[
                "Blanket Lビザのマネージャーの条件を満たします",
                "Blanket Lビザスタッフの条件を満たします"
            ],
            actions=["Blanket Lビザのマネージャーまたはスタッフの条件を満たします"],
            rule_type="#i",
            condition_logic="OR"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("Blanket Lビザのマネージャーの条件を満たします")
        cond2 = working_memory.get_value("Blanket Lビザスタッフの条件を満たします")
        return cond1 or cond2

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("Blanket Lビザのマネージャーまたはスタッフの条件を満たします", True)


class VisaRule16(Rule):
    """
    ルール16: Blanket Lビザのマネージャーの条件を満たすかチェック
    """
    def __init__(self):
        super().__init__(
            name="16",
            conditions=[
                "マネージャーとしての経験があります",
                "アメリカでの業務はマネージャーとみなされます"
            ],
            actions=["Blanket Lビザのマネージャーの条件を満たします"],
            rule_type="#i"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("マネージャーとしての経験があります")
        cond2 = working_memory.get_value("アメリカでの業務はマネージャーとみなされます")
        return cond1 and cond2

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("Blanket Lビザのマネージャーの条件を満たします", True)


class VisaRule17(Rule):
    """
    ルール17: Blanket Lビザのスタッフの条件を満たすかチェック
    """
    def __init__(self):
        super().__init__(
            name="17",
            conditions=[
                "specialized knowledgeがあります",
                "アメリカでの業務はspecialized knowledgeを必要とします"
            ],
            actions=["Blanket Lビザスタッフの条件を満たします"],
            rule_type="#i"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("specialized knowledgeがあります")
        cond2 = working_memory.get_value("アメリカでの業務はspecialized knowledgeを必要とします")
        return cond1 and cond2

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("Blanket Lビザスタッフの条件を満たします", True)


class VisaRule18(Rule):
    """
    ルール18: Lビザ（Individual）での申請が可能かチェック
    """
    def __init__(self):
        super().__init__(
            name="18",
            conditions=[
                "アメリカ以外からアメリカへのグループ内での異動です",
                "申請者がLビザ（Individual）の条件を満たします"
            ],
            actions=["Lビザ（Individual）での申請ができます"],
            rule_type="#n!"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("アメリカ以外からアメリカへのグループ内での異動です")
        cond2 = working_memory.get_value("申請者がLビザ（Individual）の条件を満たします")
        return cond1 and cond2

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("Lビザ（Individual）での申請ができます", True)


class VisaRule19(Rule):
    """
    ルール19: 申請者がLビザ（Individual）の条件を満たすかチェック
    """
    def __init__(self):
        super().__init__(
            name="19",
            conditions=[
                "直近3年のうち1年以上、アメリカ以外のグループ会社に所属していました",
                "Lビザ（Individual）のマネージャーまたはスタッフの条件を満たします"
            ],
            actions=["申請者がLビザ（Individual）の条件を満たします"],
            rule_type="#i"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("直近3年のうち1年以上、アメリカ以外のグループ会社に所属していました")
        cond2 = working_memory.get_value("Lビザ（Individual）のマネージャーまたはスタッフの条件を満たします")
        return cond1 and cond2

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("申請者がLビザ（Individual）の条件を満たします", True)


class VisaRule20(Rule):
    """
    ルール20: Lビザ（Individual）のマネージャーの条件を満たすかチェック
    """
    def __init__(self):
        super().__init__(
            name="20",
            conditions=[
                "マネージャーとしての経験があります",
                "アメリカでの業務はマネージャーとみなされます",
                "アメリカでは大卒、フルタイムの部下が2名以上います"
            ],
            actions=["Lビザ（Individual）のマネージャーの条件を満たします"],
            rule_type="#i"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("マネージャーとしての経験があります")
        cond2 = working_memory.get_value("アメリカでの業務はマネージャーとみなされます")
        cond3 = working_memory.get_value("アメリカでは大卒、フルタイムの部下が2名以上います")
        return cond1 and cond2 and cond3

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("Lビザ（Individual）のマネージャーの条件を満たします", True)


class VisaRule21(Rule):
    """
    ルール21: Lビザ（Individual）のスタッフの条件を満たすかチェック
    """
    def __init__(self):
        super().__init__(
            name="21",
            conditions=[
                "specialized knowledgeがあります",
                "アメリカでの業務はspecialized knowledgeを必要とします"
            ],
            actions=["Lビザ（Individual）のスタッフの条件を満たします"],
            rule_type="#i"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("specialized knowledgeがあります")
        cond2 = working_memory.get_value("アメリカでの業務はspecialized knowledgeを必要とします")
        return cond1 and cond2

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("Lビザ（Individual）のスタッフの条件を満たします", True)


class VisaRule22(Rule):
    """
    ルール22: H-1Bビザでの申請が可能かチェック
    """
    def __init__(self):
        super().__init__(
            name="22",
            conditions=[
                "大卒以上で、専攻内容と業務内容が一致しています",
                "大卒以上で、専攻内容と業務内容が異なりますが、実務経験が3年以上あります",
                "大卒以上ではありませんが、実務経験が(高卒は12年以上、高専卒は3年以上）あります"
            ],
            actions=["H-1Bビザでの申請ができます"],
            rule_type="#n!",
            condition_logic="OR"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("大卒以上で、専攻内容と業務内容が一致しています")
        cond2 = working_memory.get_value("大卒以上で、専攻内容と業務内容が異なりますが、実務経験が3年以上あります")
        cond3 = working_memory.get_value("大卒以上ではありませんが、実務経験が(高卒は12年以上、高専卒は3年以上）あります")
        return cond1 or cond2 or cond3

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("H-1Bビザでの申請ができます", True)


class VisaRule23(Rule):
    """
    ルール23: Bビザの申請ができるかチェック
    """
    def __init__(self):
        super().__init__(
            name="23",
            conditions=[
                "Bビザの申請条件を満たす（ESTAの認証は通る）",
                "Bビザの申請条件を満たす（ESTAの認証は通らない）"
            ],
            actions=["Bビザの申請ができます"],
            rule_type="#n!",
            condition_logic="OR"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("Bビザの申請条件を満たす（ESTAの認証は通る）")
        cond2 = working_memory.get_value("Bビザの申請条件を満たす（ESTAの認証は通らない）")
        return cond1 or cond2

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("Bビザの申請ができます", True)


class VisaRule24(Rule):
    """
    ルール24: Bビザの申請条件を満たす（ESTAの認証は通る）
    """
    def __init__(self):
        super().__init__(
            name="24",
            conditions=[
                "アメリカでの活動は商用の範囲です",
                "1回の滞在期間は90日を越えます",
                "1回の滞在期間は6か月を越えません"
            ],
            actions=["Bビザの申請条件を満たす（ESTAの認証は通る）"],
            rule_type="#i"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("アメリカでの活動は商用の範囲です")
        cond2 = working_memory.get_value("1回の滞在期間は90日を越えます")
        cond3 = working_memory.get_value("1回の滞在期間は6か月を越えません")
        return cond1 and cond2 and cond3

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("Bビザの申請条件を満たす（ESTAの認証は通る）", True)


class VisaRule25(Rule):
    """
    ルール25: Bビザの申請条件を満たす（ESTAの認証は通らない）
    """
    def __init__(self):
        super().__init__(
            name="25",
            conditions=[
                "アメリカでの活動は商用の範囲です",
                "1回の滞在期間は6か月を越えません"
            ],
            actions=["Bビザの申請条件を満たす（ESTAの認証は通らない）"],
            rule_type="#i"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("アメリカでの活動は商用の範囲です")
        cond2 = working_memory.get_value("1回の滞在期間は6か月を越えません")
        return cond1 and cond2

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("Bビザの申請条件を満たす（ESTAの認証は通らない）", True)


class VisaRule26(Rule):
    """
    ルール26: 契約書に基づくBビザの申請ができるかチェック
    """
    def __init__(self):
        super().__init__(
            name="26",
            conditions=[
                "アメリカの会社に販売した装置や設備のための作業をします",
                "装置や設備の販売を示す契約書や発注書があります",
                "1回の滞在期間は6か月を越えません"
            ],
            actions=["契約書に基づくBビザの申請ができます"],
            rule_type="#n!"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("アメリカの会社に販売した装置や設備のための作業をします")
        cond2 = working_memory.get_value("装置や設備の販売を示す契約書や発注書があります")
        cond3 = working_memory.get_value("1回の滞在期間は6か月を越えません")
        return cond1 and cond2 and cond3

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("契約書に基づくBビザの申請ができます", True)


class VisaRule27(Rule):
    """
    ルール27: B-1 in lieu of H-1Bビザの申請ができるかチェック
    """
    def __init__(self):
        super().__init__(
            name="27",
            conditions=[
                "H-1Bビザが必要な専門性の高い作業をします",
                "1回の滞在期間は6か月を越えません"
            ],
            actions=["B-1 in lieu of H-1Bビザの申請ができます"],
            rule_type="#n!"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("H-1Bビザが必要な専門性の高い作業をします")
        cond2 = working_memory.get_value("1回の滞在期間は6か月を越えません")
        return cond1 and cond2

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("B-1 in lieu of H-1Bビザの申請ができます", True)


class VisaRule28(Rule):
    """
    ルール28: J-1ビザの申請ができるかチェック
    """
    def __init__(self):
        super().__init__(
            name="28",
            conditions=[
                "研修にOJTが含まれます",
                "研修期間は18か月以内です",
                "申請者に研修に必要な英語力はあります"
            ],
            actions=["J-1ビザの申請ができます"],
            rule_type="#n!"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("研修にOJTが含まれます")
        cond2 = working_memory.get_value("研修期間は18か月以内です")
        cond3 = working_memory.get_value("申請者に研修に必要な英語力はあります")
        return cond1 and cond2 and cond3

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("J-1ビザの申請ができます", True)


class VisaRule29(Rule):
    """
    ルール29: Bビザの申請ができるかチェック（研修内容が商用の範囲）
    """
    def __init__(self):
        super().__init__(
            name="29",
            conditions=[
                "研修内容は商用の範囲です",
                "研修期間は６か月以内です"
            ],
            actions=["Bビザの申請ができます"],
            rule_type="#n!"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("研修内容は商用の範囲です")
        cond2 = working_memory.get_value("研修期間は６か月以内です")
        return cond1 and cond2

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("Bビザの申請ができます", True)


class VisaRule30(Rule):
    """
    ルール30: B-1 in lieu of H3ビザの申請ができるかチェック
    """
    def __init__(self):
        super().__init__(
            name="30",
            conditions=[
                "研修内容は商用の範囲です",
                "研修期間は６か月以内です"
            ],
            actions=["B-1 in lieu of H3ビザの申請ができます"],
            rule_type="#n!"
        )

    def check_conditions(self, working_memory) -> bool:
        cond1 = working_memory.get_value("研修内容は商用の範囲です")
        cond2 = working_memory.get_value("研修期間は６か月以内です")
        return cond1 and cond2

    def execute_actions(self, working_memory) -> None:
        working_memory.put_value_of_hypothesis("B-1 in lieu of H3ビザの申請ができます", True)


# 全ルールをリストで返す関数
def get_all_visa_rules():
    """
    すべてのビザルールを取得

    Returns:
        全31個のビザルールのリスト
    """
    return [
        VisaRule1(), VisaRule2(), VisaRule3(), VisaRule4(), VisaRule5(),
        VisaRule6(), VisaRule7(), VisaRule8(), VisaRule9(), VisaRule10(),
        VisaRule11(), VisaRule12(), VisaRule13(), VisaRule14(), VisaRule15(),
        VisaRule16(), VisaRule17(), VisaRule18(), VisaRule19(), VisaRule20(),
        VisaRule21(), VisaRule22(), VisaRule23(), VisaRule24(), VisaRule25(),
        VisaRule26(), VisaRule27(), VisaRule28(), VisaRule29(), VisaRule30()
    ]


def get_rules_by_visa_type(visa_type: str):
    """
    指定されたビザタイプに関連するルールのみを取得

    Args:
        visa_type: ビザタイプ（"E", "L", "B"）

    Returns:
        指定されたビザタイプに関連するルールのリスト
    """
    if visa_type == "E":
        # Eビザ関連: ルール1-11
        return [
            VisaRule1(), VisaRule2(), VisaRule3(), VisaRule4(), VisaRule5(),
            VisaRule6(), VisaRule7(), VisaRule8(), VisaRule9(), VisaRule10(),
            VisaRule11()
        ]
    elif visa_type == "L":
        # Lビザ関連: ルール12-21
        return [
            VisaRule12(), VisaRule13(), VisaRule14(), VisaRule15(), VisaRule16(),
            VisaRule17(), VisaRule18(), VisaRule19(), VisaRule20(), VisaRule21()
        ]
    elif visa_type == "B":
        # Bビザ関連: ルール23-27, 29-30
        return [
            VisaRule23(), VisaRule24(), VisaRule25(), VisaRule26(), VisaRule27(),
            VisaRule29(), VisaRule30()
        ]
    else:
        # デフォルトは全ルール
        return get_all_visa_rules()
