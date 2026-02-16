from rest_framework import status
from rest_framework.test import APITestCase

from api.models.category import Category
from api.models.company import Company


class CategoryValidationTests(APITestCase):
    """CategoryViewSet のバリデーション・ビジネスルールをテストする。"""

    def setUp(self):
        """各テストメソッドの実行前に呼ばれる共通セットアップ。"""
        self.company = Company.objects.create(name="テスト企業")
        self.other_company = Company.objects.create(name="別企業")
        self.category = Category.objects.create(
            company=self.company,
            name="テストカテゴリ",
        )

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

    def test_create_without_name(self):
        """name なしで作成すると400を返すこと。"""
        data = {"company": self.company.id}
        response = self.client.post("/api/categories/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_without_company(self):
        """company なしで作成すると400を返すこと。"""
        data = {"name": "カテゴリ"}
        response = self.client.post("/api/categories/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_duplicate_name_in_same_company(self):
        """同一企業内でカテゴリ名が重複する場合は400を返すこと。"""
        data = {
            "company": self.company.id,
            "name": "テストカテゴリ",  # setUp で作成済みの名前
        }
        response = self.client.post("/api/categories/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
