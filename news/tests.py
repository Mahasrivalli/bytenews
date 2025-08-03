from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Article, Category

class ArticleViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="TestCat")
        self.article = Article.objects.create(
            title="Test Article",
            content="This is a test article.",
            approved=True,
            category=self.category
        )
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_article_list_view(self):
        response = self.client.get(reverse('news:article_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)

    def test_article_detail_view(self):
        response = self.client.get(reverse('news:article_detail', kwargs={'pk': self.article.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.content)

    def test_generate_summary_requires_login(self):
        response = self.client.get(reverse('news:generate_summary', kwargs={'pk': self.article.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_api_article_list(self):
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 200)
