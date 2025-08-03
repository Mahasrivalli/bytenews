from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from users import views as user_views

# 👇 For serving media during development
from django.conf import settings
from django.conf.urls.static import static
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_views.home, name='home'),
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),

    path('news/', include(('news.urls', 'news'), namespace='news')),
    path('users/', include(('users.urls', 'users'), namespace='users')),

    # ✅ API endpoints
    path('api/', include('news.api_urls')),

    # ✅ Debug toolbar (add this)
    path('__debug__/', include(debug_toolbar.urls)),
]

# ✅ Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
