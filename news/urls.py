# news/urls.py
from django.urls import path
from .views import ArticleListView, ArticleDetailView

urlpatterns = [
    path('', ArticleListView.as_view(), name='article_list'),  # /news/
    path('<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),  # /news/5/
]
