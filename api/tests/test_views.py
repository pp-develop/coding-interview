from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryViewTests(APITestCase):
    """
    CategoryViewSet の CRUD 操作をテストする。
    APITestCase は DRF が提供するテスト基盤で、以下を自動で行う:
    - テスト用DBの作成・破棄（テストごとにロールバックされるため各テストは独立）
    - self.client: APIリクエストを送信するテスト用クライアント
    """

    def setUp(self):
        """各テストメソッドの実行前に呼ばれる共通セットアップ。"""
        self.company = Company.objects.create(name="テスト企業")
        self.other_company = Company.objects.create(name="別企業")
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

    def test_create_with_parent(self):
        """親カテゴリを指定してカテゴリを作成できること。"""
        data = {
            "company": self.company.id,
            "name": "子カテゴリ",
            "parent_category": self.category.id,
        }
        response = self.client.post("/api/categories/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        child = Category.objects.get(name="子カテゴリ")
        self.assertEqual(child.parent_category, self.category)

    def test_create_with_parent_from_other_company(self):
        """親カテゴリが別企業の場合は作成できないこと。"""
        other_category = Category.objects.create(
            company=self.other_company,
            name="別企業カテゴリ",
        )
        data = {
            "company": self.company.id,
            "name": "子カテゴリ",
            "parent_category": other_category.id,
        }
        response = self.client.post("/api/categories/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_self_reference(self):
        """自分自身を親カテゴリに設定できないこと。"""
        data = {"parent_category": self.category.id}
        response = self.client.patch(f"/api/categories/{self.category.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_circular_reference(self):
        """循環参照となる親カテゴリを設定できないこと（A→B→A）。"""
        child = Category.objects.create(
            company=self.company,
            name="子カテゴリ",
            parent_category=self.category,
        )
        # 親(self.category) の parent を 子(child) に変更 → A→B→A の循環
        data = {"parent_category": child.id}
        response = self.client.patch(f"/api/categories/{self.category.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_company_change(self):
        """更新時に企業を変更できないこと。"""
        data = {"company": self.other_company.id}
        response = self.client.patch(f"/api/categories/{self.category.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
