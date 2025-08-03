from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ---------------------------
# 📂 Category Model
# ---------------------------
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


# ---------------------------
# 🔖 Article Model
# ---------------------------
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(blank=True, null=True)

    link = models.URLField(max_length=500, unique=True, null=True, blank=True)
    source = models.CharField(max_length=100, default='Unknown')
    author = models.CharField(max_length=100, default='Unknown')

    source_url = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles')

    published_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    audio_file = models.FileField(upload_to='audio/', blank=True, null=True)

    summary_helpful = models.PositiveIntegerField(default=0)
    summary_not_helpful = models.PositiveIntegerField(default=0)

    approved = models.BooleanField(default=False)

    def approved_status(self):
        return "✅ Approved" if self.approved else "❌ Pending"
    approved_status.boolean = True
    approved_status.short_description = "Approval Status"

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_date']
        verbose_name = "Article"
        verbose_name_plural = "Articles"


# ---------------------------
# 👤 User Preference Model
# ---------------------------
class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preference')
    preferred_categories = models.ManyToManyField(Category, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Preferences"


# ---------------------------
# 📖 Reading History Model
# ---------------------------
class ReadingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} read {self.article.title}"

    class Meta:
        ordering = ['-read_at']
        verbose_name = "Reading History"
        verbose_name_plural = "Reading Histories"
