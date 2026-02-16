from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryCrudTests(APITestCase):
    """CategoryViewSet の基本 CRUD 操作をテストする。"""

    def setUp(self):
        """各テストメソッドの実行前に呼ばれる共通セットアップ。"""
        self.company = Company.objects.create(name="テスト企業")
        self.category = Category.objects.create(
            company=self.company,
            name="テストカテゴリ",
        )

    def test_list(self):
        """GET /api/categories/ でカテゴリ一覧を取得できること。"""
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve(self):
        """GET /api/categories/{id}/ で特定のカテゴリを取得できること。"""
        response = self.client.get(f"/api/categories/{self.category.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "テストカテゴリ")

    def test_create(self):
        """POST /api/categories/ でカテゴリを作成できること。"""
        data = {
            "company": self.company.id,
            "name": "新規カテゴリ",
        }
        response = self.client.post("/api/categories/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(Category.objects.get(name="新規カテゴリ").company, self.company)

    def test_update(self):
        """PATCH /api/categories/{id}/ でカテゴリを部分更新できること。"""
        data = {"name": "更新後カテゴリ"}
        response = self.client.patch(f"/api/categories/{self.category.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "更新後カテゴリ")

    def test_destroy(self):
        """DELETE /api/categories/{id}/ でカテゴリを削除できること。"""
        response = self.client.delete(f"/api/categories/{self.category.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)
