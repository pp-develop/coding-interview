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

    加えて、以下のカスタムバリデーションを validate() で実装:
    - parent_category は同一企業のカテゴリであること
    - 自分自身を親カテゴリに設定できないこと（自己参照・循環参照の防止）
    - 更新時に company を変更できないこと
    """

    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        # id, created_at, updated_at はモデル側で editable=False のため自動で read_only になるが、
        # 明示的に記載して意図を明確にする
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        # 更新時: company の変更を禁止
        if self.instance and "company" in data and data["company"] != self.instance.company:
            raise serializers.ValidationError({"company": "企業の変更はできません"})

        # parent_category が同一企業に属しているかチェック
        # 更新時に company が送られない場合(PATCH)は instance の company を使う
        parent = data.get("parent_category")
        company = data.get("company", getattr(self.instance, "company", None))
        if parent and company and parent.company != company:
            raise serializers.ValidationError({"parent_category": "親カテゴリは同じ企業に属している必要があります"})

        # 更新時: 自己参照・循環参照の防止
        # 親を辿っていって自分自身に到達する場合はエラー（例: A→B→C→A）
        if self.instance and parent:
            current = parent
            while current is not None:
                if current.id == self.instance.id:
                    raise serializers.ValidationError({"parent_category": "循環参照が発生するため、この親カテゴリは設定できません"})
                current = current.parent_category

        return data
