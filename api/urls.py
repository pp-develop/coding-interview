from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.category import CategoryViewSet

router = DefaultRouter()

# CategoryViewSet を登録することで以下のエンドポイントが自動生成される:
# GET    /api/categories/       → 一覧
# POST   /api/categories/       → 作成
# GET    /api/categories/{id}/  → 詳細
# PUT    /api/categories/{id}/  → 全更新
# PATCH  /api/categories/{id}/  → 部分更新
# DELETE /api/categories/{id}/  → 削除
router.register("categories", CategoryViewSet)

urlpatterns = [path("", include(router.urls))]
