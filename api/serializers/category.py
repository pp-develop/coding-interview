from rest_framework import serializers

from api.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    CategoryモデルのSerializer。
    ModelSerializer はモデル定義を読み取り、以下のバリデーションを自動生成する:
    - name: 必須チェック、max_length=255
    - company: 存在する企業IDであること（ForeignKey の参照整合性）
    - parent_category: 存在するカテゴリIDであること（null は許可 = ルートカテゴリ作成可）
    - (company, name): 同一企業内でカテゴリ名の重複不可（UniqueConstraint による自動検出）
    そのため、カスタムバリデーションは実装しない。
    """

    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        # id, created_at, updated_at はモデル側で editable=False のため自動で read_only になるが、
        # 明示的に記載して意図を明確にする
        read_only_fields = ["id", "created_at", "updated_at"]
