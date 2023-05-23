from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from .views import register
from news import settings, views
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('', RedirectView.as_view(url='/articles/')),
    path('login/', auth_views.LoginView.as_view(next_page="/profile",template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/articles/',template_name='registration/logout.html'), name='logout'),
    path('admin/', admin.site.urls),
    path('articles/', include('articles.urls')),
    path('register/', register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit', views.ProfileUpdateView.as_view(template_name='articles/profile_edit.html'), name='profile_edit'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
