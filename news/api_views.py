from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Article, UserPreference
from .serializers import ArticleSerializer, UserPreferenceSerializer
from .utils import generate_summary
from gtts import gTTS
from django.core.files.base import ContentFile
import io


class ArticleListAPIView(generics.ListAPIView):
    queryset = Article.objects.filter(approved=True).order_by('-published_date')
    serializer_class = ArticleSerializer


class ArticleDetailAPIView(generics.RetrieveAPIView):
    queryset = Article.objects.filter(approved=True)
    serializer_class = ArticleSerializer


class UserPreferenceAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserPreferenceSerializer

    def get_object(self):
        return self.request.user.preference


class GenerateSummaryAudioAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            article = Article.objects.get(pk=pk)

            if not article.summary:
                article.summary = generate_summary(article.content, article.title)
                article.save()

            tts = gTTS(article.summary[:5000], lang='en')
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)

            filename = f"{article.pk}_summary_api.mp3"
            article.audio_file.save(filename, ContentFile(audio_bytes.read()))
            article.save()

            return Response({'message': 'Audio summary generated successfully.', 'audio_url': article.audio_file.url})
        except Article.DoesNotExist:
            return Response({'error': 'Article not found.'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
