from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from .models import Article, Category

class ArticleListView(ListView):
    model = Article
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    paginate_by = 6
    ordering = ['-published_date']

    def get_queryset(self):
        queryset = super().get_queryset()

        category_name = self.request.GET.get('category')
        search_query = self.request.GET.get('q')

        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = Category.objects.annotate(
            article_count=Count('articles')
        ).order_by('name')

        context['current_category'] = self.request.GET.get('category', 'All')
        context['search_query'] = self.request.GET.get('q', '')

        return context

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'news/article_detail.html'
    context_object_name = 'article'
