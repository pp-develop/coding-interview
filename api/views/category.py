from rest_framework.viewsets import ModelViewSet

from api.models.category import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(ModelViewSet):
    """
    CategoryモデルのCRUD APIを提供するViewSet。
    ModelViewSet により以下のエンドポイントが自動で提供される:
    - GET    /api/categories/       一覧取得（list）
    - GET    /api/categories/{id}/  詳細取得（retrieve）
    - POST   /api/categories/       作成（create）
    - PUT    /api/categories/{id}/  全更新（update）
    - PATCH  /api/categories/{id}/  部分更新（partial_update）
    - DELETE /api/categories/{id}/  削除（destroy）

    認証は要件にないため追加しない。
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
