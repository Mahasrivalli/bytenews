from django.urls import path
from . import views
from .views import ReadingHistoryListView  # ✅ Import the class-based view

app_name = 'users'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('preferences/', views.preferences, name='preferences'),
    path('history/', ReadingHistoryListView.as_view(), name='reading_history'),  # ✅ New path added
]
