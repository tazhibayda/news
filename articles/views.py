from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from django.core.files.storage import FileSystemStorage
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormMixin

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
        return context

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


