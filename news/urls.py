from django.urls import path
from .views import (
    ArticleListView,
    ArticleDetailView,
    generate_summary_view,
    generate_audio_view,
    generate_audio_ajax,
    submit_summary_feedback,
    approve_article_view
)

app_name = 'news'  # ✅ Required for namespaced URL reversing like 'news:detail'

urlpatterns = [
    # 🔹 Main article list page
    path('', ArticleListView.as_view(), name='article_list'),

    # 🔹 Detail view for a specific article
    path('article/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),

    # 🔹 Summary generation (manual)
    path('article/<int:pk>/generate-summary/', generate_summary_view, name='generate_summary'),

    # 🔹 Audio generation (manual)
    path('article/<int:pk>/generate-audio/', generate_audio_view, name='generate_audio'),

    # 🔹 Audio generation via AJAX
    path('article/<int:pk>/ajax/generate-audio/', generate_audio_ajax, name='generate_audio_ajax'),

    # 🔹 Feedback for article summary
    path('article/<int:pk>/feedback/', submit_summary_feedback, name='submit_summary_feedback'),

    # 🔹 Admin article approval
    path('article/<int:pk>/approve/', approve_article_view, name='approve_article'),
]
