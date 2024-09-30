from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
import redis
from django.conf import settings
from django.core.cache import cache

from django.core.files.storage import FileSystemStorage
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormMixin
from datetime import datetime, timedelta, time
from .forms import *
from .models import Article
from django.core.paginator import Paginator


class ArticleListView(ListView):
    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'
    ordering = ['-date_posted']
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        genre = self.request.GET.get('genre')
        q = self.request.GET.get('q')
        if genre:
            queryset = queryset.filter(genres__name=genre)
        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(content__icontains=q))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        articles = context['articles']
        total_pages = (Article.objects.all().count() + self.paginate_by - 1) // self.paginate_by
        paginator = Paginator(articles, self.paginate_by, total_pages)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        if page_number is None:
            context['page_number'] = 1
        else:
            context['page_number'] = int(page_number)
        return context


class ArticleDetailView(FormMixin, DetailView):
    model = Article
    template_name = 'articles/article_detail.html'
    form_class = CommentForm
    success_url = reverse_lazy('article_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = Comment.objects.filter(article__id=self.object.id)

        # Get the session ID
        session = self.request.session
        session_key = f"viewed_article_{self.object.id}"

        # Check if the session has already viewed the article
        if not session.get(session_key):
            # If not viewed, increment the view count in Redis
            self.increment_article_views()

            # Set a flag in the session to mark this article as viewed
            session[session_key] = True
            session.modified = True

        return context

    def increment_article_views(self):

        now = datetime.now()

        # Day-based view count
        day_key = f"article:views:{self.object.id}:day"
        day_count = cache.get(day_key)
        midnight = datetime.combine(now.date(), time())
        seconds_since_midnight = (now - midnight).total_seconds()
        day_time = int(seconds_since_midnight)

        if day_count:
            cache.set(day_key, day_count + 1, day_time)
        else:
            cache.set(day_key, 1, day_time)

        # Week-based view count
        week_key = f"article:views:{self.object.id}:week"
        week_count = cache.get(week_key)
        days_until_next_monday = (7 - now.weekday()) % 7
        next_monday = now + timedelta(days=days_until_next_monday)
        next_monday = next_monday.replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_to_next_week = (next_monday - now).total_seconds()
        week_time = int(seconds_to_next_week)

        if week_count:
            cache.set(week_key, week_count + 1, week_time)
        else:
            cache.set(week_key, 1, week_time)

        # Month-based view count
        month_key = f"article:views:{self.object.id}:month"
        month_count = cache.get(month_key)
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_month = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        seconds_to_next_month = (next_month - now).total_seconds()
        month_time = int(seconds_to_next_month)

        if month_count:
            cache.set(month_key, month_count + 1, month_time)
        else:
            cache.set(month_key, 1, month_time)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'comment' in request.POST:
            return self.comment_post(request, *args, **kwargs)

    def comment_post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = self.object
            comment.author = request.user
            comment.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    template_name = 'articles/article_form.html'
    fields = ['title', 'content','image','genres']

    def form_valid(self, form):
        form.instance.author = self.request.user
        image_file = self.request.FILES.get('image')
        if image_file:
            fs = FileSystemStorage(location='media/article_images')
            ext = image_file.name.split('.')[-1]
            name = f'{timezone.now().strftime("%Y-%m-%d_%H%M%S")}.{ext}'
            filename = fs.save(name, image_file)
            form.instance.image = filename
        return super().form_valid(form)

    def test_func(self):
        article = self.get_object()
        if self.request.user.is_superuser:
            return True
        return False


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    template_name = 'articles/article_form.html'
    fields = ['title', 'content', 'image','genres']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        article = self.get_object()
        if self.request.user == article.author:
            return True
        if self.request.user.is_superuser:
            return True
        return False


class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = 'articles/article_confirm_delete.html'
    success_url = reverse_lazy('article_list')

    def test_func(self):
        article = self.get_object()
        if self.request.user == article.author:
            return True
        if self.request.user.is_superuser:
            return True
        return False

