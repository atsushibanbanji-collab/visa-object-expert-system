"""
既存のハードコードされたルールをデータベースに移行するスクリプト
"""
from backend.database import init_db, SessionLocal
from backend.models.rule_db import RuleDB
from backend.rules.visa_rules import (
    VisaRule1, VisaRule2, VisaRule3, VisaRule4, VisaRule5,
    VisaRule6, VisaRule7, VisaRule8, VisaRule9, VisaRule10,
    VisaRule11, VisaRule12, VisaRule13, VisaRule14, VisaRule15,
    VisaRule16, VisaRule17, VisaRule18, VisaRule19, VisaRule20,
    VisaRule21, VisaRule22, VisaRule23, VisaRule24, VisaRule25,
    VisaRule26, VisaRule27, VisaRule28, VisaRule29, VisaRule30
)


# ルールとビザタイプのマッピング
RULE_VISA_MAPPING = {
    # Eビザ関連: ルール1-11
    **{f"VisaRule{i}": "E" for i in range(1, 12)},
    # Lビザ関連: ルール12-21
    **{f"VisaRule{i}": "L" for i in range(12, 22)},
    # H-1Bビザ: ルール22
    "VisaRule22": "H",
    # Bビザ関連: ルール23-27, 29-30
    **{f"VisaRule{i}": "B" for i in [23, 24, 25, 26, 27, 29, 30]},
    # J-1ビザ: ルール28
    "VisaRule28": "J"
}


def migrate_rules():
    """
    既存のルールをデータベースに移行（ルールがない場合のみ）
    """
    # データベースを初期化
    print("🗄️  データベースを初期化しています...")
    init_db()

    # セッションを作成
    db = SessionLocal()

    try:
        # 既存のルール数を確認
        existing_count = db.query(RuleDB).count()
        if existing_count > 0:
            print(f"✅ データベースには既に {existing_count} 件のルールが存在します。移行をスキップします。")
            return

        # 各ルールクラスをインスタンス化してデータベースに保存
        rule_classes = [
            VisaRule1, VisaRule2, VisaRule3, VisaRule4, VisaRule5,
            VisaRule6, VisaRule7, VisaRule8, VisaRule9, VisaRule10,
            VisaRule11, VisaRule12, VisaRule13, VisaRule14, VisaRule15,
            VisaRule16, VisaRule17, VisaRule18, VisaRule19, VisaRule20,
            VisaRule21, VisaRule22, VisaRule23, VisaRule24, VisaRule25,
            VisaRule26, VisaRule27, VisaRule28, VisaRule29, VisaRule30
        ]

        print(f"📝 {len(rule_classes)}個のルールを移行しています...")

        for i, rule_class in enumerate(rule_classes, 1):
            # ルールをインスタンス化
            rule_obj = rule_class()

            # ビザタイプを取得
            class_name = rule_class.__name__
            visa_type = RULE_VISA_MAPPING.get(class_name, "ALL")

            # データベースに保存
            import json
            rule_db = RuleDB(
                name=rule_obj.name,
                visa_type=visa_type,
                rule_type=rule_obj.type,
                condition_logic=rule_obj.condition_logic,
                conditions=json.dumps(rule_obj.conditions, ensure_ascii=False),  # JSON形式で保存
                actions=json.dumps(rule_obj.actions, ensure_ascii=False),  # JSON形式で保存
                priority=i  # ルール番号を優先順位として使用
            )

            db.add(rule_db)
            print(f"  ✓ ルール{rule_obj.name} ({visa_type}ビザ) を追加しました")

        # コミット
        db.commit()
        print(f"✅ {len(rule_classes)}個のルールの移行が完了しました！")

        # 確認のため件数を表示
        count = db.query(RuleDB).count()
        print(f"📊 データベースに {count} 件のルールが保存されています")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_rules()
