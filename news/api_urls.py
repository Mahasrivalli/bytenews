from django.urls import path
from .api_views import (
    ArticleListAPIView,
    ArticleDetailAPIView,
    UserPreferenceAPIView,
    GenerateSummaryAudioAPIView,
)

urlpatterns = [
    path('articles/', ArticleListAPIView.as_view(), name='api_article_list'),
    path('articles/<int:pk>/', ArticleDetailAPIView.as_view(), name='api_article_detail'),
    path('preferences/', UserPreferenceAPIView.as_view(), name='api_user_preferences'),
    path('articles/<int:pk>/generate-summary-audio/', GenerateSummaryAudioAPIView.as_view(), name='api_generate_audio'),
]
