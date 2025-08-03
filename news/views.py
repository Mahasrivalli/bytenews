from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


import io
from gtts import gTTS

from .models import Article, Category, ReadingHistory, UserPreference
from .utils import generate_summary, generate_audio_summary
# -----------------------------
# 📄 CACHED ARTICLE LIST VIEW
# -----------------------------
@method_decorator(cache_page(60 * 2), name='dispatch')  # Cache for 2 minutes
class ArticleListView(ListView):
    model = Article
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    paginate_by = 6
    ordering = ['-published_date']
# -----------------------------
# 📄 ARTICLE LIST VIEW
# -----------------------------
class ArticleListView(ListView):
    model = Article
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    paginate_by = 6
    ordering = ['-published_date']

    def get_queryset(self):
        queryset = super().get_queryset().filter(approved=True)
        queryset = queryset.select_related('category')
        queryset = queryset.prefetch_related('category__articles', 'readinghistory_set')

        category_name = self.request.GET.get('category')
        search_query = self.request.GET.get('q')

        if category_name and category_name != 'All':
            queryset = queryset.filter(category__name__iexact=category_name)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

        if self.request.user.is_authenticated:
            try:
                user_pref = self.request.user.preference
                preferred_categories = user_pref.preferred_categories.all()
                if preferred_categories.exists():
                    queryset = queryset.filter(category__in=preferred_categories).distinct()
                    messages.info(self.request, "Showing personalized articles.")
                else:
                    messages.info(self.request, "No preferences set. Showing all articles.")
            except UserPreference.DoesNotExist:
                messages.info(self.request, "Set your preferences to customize your feed.")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = Category.objects.annotate(
            article_count=Count('articles')
        ).order_by('name')

        context['current_category'] = self.request.GET.get('category', 'All')
        context['search_query'] = self.request.GET.get('q', '')
        context['recommendations'] = []

        if self.request.user.is_authenticated:
            try:
                preferred = self.request.user.preference.preferred_categories.all()
                if preferred.exists():
                    read_ids = ReadingHistory.objects.filter(
                        user=self.request.user
                    ).values_list('article_id', flat=True)

                    recommended = Article.objects.filter(
                        category__in=preferred,
                        approved=True
                    ).exclude(id__in=read_ids).distinct().order_by('-published_date')[:5]

                    context['recommendations'] = recommended
            except UserPreference.DoesNotExist:
                pass

        return context

# -----------------------------
# 📄 ARTICLE DETAIL VIEW
# -----------------------------
class ArticleDetailView(DetailView):
    model = Article
    template_name = 'news/article_detail.html'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user.is_authenticated:
            ReadingHistory.objects.get_or_create(
                user=self.request.user,
                article=obj
            )
        return obj

# -----------------------------
# 📝 GENERATE SUMMARY VIEW
# -----------------------------
@login_required
def generate_summary_view(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.summary = generate_summary(article.content, article.title)
    article.save()
    messages.success(request, "Summary generated successfully!")
    return redirect('news:article_detail', pk=pk)

# -----------------------------
# 🎧 GENERATE AUDIO (Manual)
# -----------------------------
@login_required
def generate_audio_view(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if article.audio_file:
        messages.info(request, "Audio already exists for this article.")
        return redirect('news:article_detail', pk=pk)

    try:
        if not article.summary:
            article.summary = generate_summary(article.content, article.title)
            article.save()

        tts = gTTS(text=article.summary[:5000], lang='en')
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)

        filename = f"{article.pk}_summary.mp3"
        article.audio_file.save(filename, ContentFile(audio_bytes.read()))
        article.save()

        messages.success(request, "Audio generated successfully!")
    except Exception as e:
        messages.error(request, f"Failed to generate audio: {e}")

    return redirect('news:article_detail', pk=pk)

# -----------------------------
# 💬 SUMMARY FEEDBACK VIEW
# -----------------------------
@login_required
@require_POST
def submit_summary_feedback(request, pk):
    article = get_object_or_404(Article, pk=pk)
    feedback_type = request.POST.get('feedback')

    if feedback_type == 'helpful':
        article.summary_helpful += 1
    elif feedback_type == 'not_helpful':
        article.summary_not_helpful += 1

    article.save()
    messages.success(request, "Thanks for your feedback!")
    return redirect('news:article_detail', pk=pk)

# -----------------------------
# ✅ APPROVE ARTICLE VIEW
# -----------------------------
@staff_member_required
@require_POST
@csrf_protect
def approve_article_view(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.approved = True
    article.save()
    messages.success(request, "Article approved successfully.")
    return redirect('news:article_detail', pk=pk)

# -----------------------------
# 🔁 AJAX: GENERATE AUDIO ON-DEMAND
# -----------------------------
@login_required
@require_POST
def generate_audio_ajax(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if not article.summary:
        article.summary = generate_summary(article.content, article.title)
        article.save()
        if not article.summary:
            return JsonResponse({'status': 'error', 'message': 'Could not generate summary.'}, status=500)

    audio_url = generate_audio_summary(article.summary, article.id)

    if audio_url:
        article.audio_file.name = audio_url.replace(settings.MEDIA_URL, '', 1)
        article.save()
        messages.success(request, "Audio summary generated!")
        return JsonResponse({'status': 'success', 'audio_url': audio_url})
    else:
        messages.error(request, "Failed to generate audio summary.")
        return JsonResponse({'status': 'error', 'message': 'Failed to generate audio'}, status=500)
