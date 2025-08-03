from django.contrib import admin
from .models import Category, Article, UserPreference, ReadingHistory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
        'published_date',
        'created_at',
        'get_approval_status',
        'summary_feedback',
    ]
    list_filter = ['category', 'published_date', 'source', 'approved']
    search_fields = ['title', 'content', 'summary']
    
    # ✅ Make sure 'approved' is editable (remove it from readonly_fields)
    readonly_fields = ['created_at']  # ✅ Now approved is editable in admin form

    actions = ['approve_articles', 'disapprove_articles']
    list_display_links = ['title']
    ordering = ['-published_date']

    def get_approval_status(self, obj):
        return "✅ Approved" if obj.approved else "❌ Pending"
    get_approval_status.short_description = "Approval Status"
    get_approval_status.admin_order_field = 'approved'

    def summary_feedback(self, obj):
        return f"👍 {obj.summary_helpful} / 👎 {obj.summary_not_helpful}"
    summary_feedback.short_description = "Summary Feedback"

    def approve_articles(self, request, queryset):
        updated = queryset.update(approved=True)
        self.message_user(request, f"{updated} article(s) approved.")
    approve_articles.short_description = "✅ Approve selected articles"

    def disapprove_articles(self, request, queryset):
        updated = queryset.update(approved=False)
        self.message_user(request, f"{updated} article(s) disapproved.")
    disapprove_articles.short_description = "❌ Disapprove selected articles"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            qs = Article.objects.all()

        extra_context = extra_context or {}
        extra_context['article_stats'] = {
            'approved': qs.filter(approved=True).count(),
            'pending': qs.filter(approved=False).count(),
            'total': qs.count(),
        }
        response.context_data.update(extra_context)
        return response


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user']
    filter_horizontal = ['preferred_categories']


@admin.register(ReadingHistory)
class ReadingHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'read_at']
    list_filter = ['read_at']
    readonly_fields = ['read_at']
