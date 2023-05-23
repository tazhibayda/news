from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Genre(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='article_connect_comment')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Article(models.Model):
    title = models.CharField(max_length=100)
    source = models.CharField(max_length=100, null=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    date_posted = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='article_images', null=True)
    genres = models.ManyToManyField(Genre, blank=True)
    url = models.CharField(max_length=100, null=True)
    comments = models.ManyToManyField(Comment, blank=True, related_name='articles_comments')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'pk': self.pk})


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures', blank=True)

    def __str__(self):
        return self.user.username


