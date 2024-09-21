import redis
from datetime import datetime, timedelta
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Article
from django.shortcuts import render

# Initialize Redis connection
r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


def get_top_articles_by_period(period_key_format, start_date, end_date):
    keys = []

    # Get the keys for articles from the given period
    for day in range((end_date - start_date).days + 1):
        day_key = (start_date + timedelta(days=day)).strftime('%Y-%m-%d')
        keys += r.keys(pattern=f"article:views:*:{day_key}")

    # Retrieve and sort articles by their view counts
    view_counts = []
    for key in keys:
        article_id = key.split(':')[2]
        view_count = int(r.get(key))
        view_counts.append((article_id, view_count))

    # Sort by view counts and return top articles
    sorted_articles = sorted(view_counts, key=lambda x: x[1], reverse=True)
    top_articles = [Article.objects.get(pk=article_id) for article_id, count in sorted_articles]

    return top_articles


def get_top_articles_of_day():
    today = datetime.now().date()
    return get_top_articles_by_period(f"article:views:*:{today}", today, today)


def get_top_articles_of_week():
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    return get_top_articles_by_period("article:views:*", week_start, today)


def get_top_articles_of_month():
    today = datetime.now().date()
    month_start = today.replace(day=1)
    return get_top_articles_by_period("article:views:*", month_start, today)


def top_articles_of_day(request):
    top_articles = get_top_articles_of_day()
    return render(request, 'articles/top_articles.html', {'articles': top_articles, 'period': 'Today'})


def top_articles_of_week(request):
    top_articles = get_top_articles_of_week()
    return render(request, 'articles/top_articles.html', {'articles': top_articles, 'period': 'This Week'})


def top_articles_of_month(request):
    top_articles = get_top_articles_of_month()
    return render(request, 'articles/top_articles.html', {'articles': top_articles, 'period': 'This Month'})