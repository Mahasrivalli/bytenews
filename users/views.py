from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from users.Registration.registration import Registration
from users.Registration.forms import UserPreferenceForm

from news.models import UserPreference, ReadingHistory, Article  # ✅ Added Article

# -----------------------------
# HOME PAGE VIEW (with articles)
# -----------------------------
def home(request):
    articles = Article.objects.all().order_by('-published_date')[:6]  # Show latest 6 articles
    return render(request, 'users/home.html', {'articles': articles})


# -----------------------------
# USER REGISTRATION VIEW
# -----------------------------
def register(request):
    if request.method == 'POST':
        form = Registration(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    else:
        form = Registration()
    return render(request, 'users/register.html', {'form': form})


# -----------------------------
# USER PREFERENCES VIEW
# -----------------------------
@login_required
def preferences(request):
    preference, _ = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserPreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            messages.success(request, "Preferences updated.")
            return redirect('users:preferences')
    else:
        form = UserPreferenceForm(instance=preference)

    return render(request, 'users/preferences.html', {'form': form})


# -----------------------------
# READING HISTORY VIEW
# -----------------------------
class ReadingHistoryListView(ListView):
    model = ReadingHistory
    template_name = 'users/history.html'
    context_object_name = 'history'
    paginate_by = 10

    def get_queryset(self):
        return ReadingHistory.objects.filter(
            user=self.request.user
        ).select_related('article').order_by('-read_at')
