from rest_framework import serializers
from .models import Article, Category, UserPreference


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'summary', 'content', 'author', 'published_date', 'category', 'audio_file']


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['preferred_categories']
