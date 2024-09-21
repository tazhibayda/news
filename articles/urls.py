from django.urls import path
from django.contrib.auth import views as auth_views
from .redis import *
from .views import ArticleListView, ArticleDetailView, ArticleCreateView, ArticleUpdateView, ArticleDeleteView

# articles/ ''
urlpatterns = [
    path('', ArticleListView.as_view(), name='article_list'),
    path('<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('new/', ArticleCreateView.as_view(), name='article_new'),
    path('<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_edit'),
    path('<int:pk>/delete/', ArticleDeleteView.as_view(), name='article_delete'),
    path('top-articles/day/', top_articles_of_day, name='top_articles_day'),
    path('top-articles/week/', top_articles_of_week, name='top_articles_week'),
    path('top-articles/month/', top_articles_of_month, name='top_articles_month'),
]

