from celery import shared_task
from datetime import datetime, timedelta
from django.core.cache import cache

# Import your models
from .models import Article


@shared_task
def update_top_10_day():
    # Calculate top 10 articles of the day
    day_view_keys = cache.keys("article:views:*:day")
    day_view_counts = cache.get_many(day_view_keys)
    sorted_articles = sorted(day_view_counts.items(), key=lambda item: item[1], reverse=True)
    top_10_articles_day = sorted_articles[:10]

    # Cache the result for 1 hour
    cache.set("top_10_day", top_10_articles_day, timeout=3600)  # Cache for 1 hour


@shared_task
def update_top_10_week():
    # Calculate top 10 articles of the week
    week_view_keys = cache.keys("article:views:*:week")
    week_view_counts = cache.get_many(week_view_keys)
    sorted_articles = sorted(week_view_counts.items(), key=lambda item: item[1], reverse=True)
    top_10_articles_week = sorted_articles[:10]

    # Cache the result for 1 day
    cache.set("top_10_week", top_10_articles_week, timeout=86400)  # Cache for 1 day


@shared_task
def update_top_10_month():
    # Calculate top 10 articles of the month
    month_view_keys = cache.keys("article:views:*:month")
    month_view_counts = cache.get_many(month_view_keys)
    sorted_articles = sorted(month_view_counts.items(), key=lambda item: item[1], reverse=True)
    top_10_articles_month = sorted_articles[:10]

    # Cache the result for 1 week
    cache.set("top_10_month", top_10_articles_month, timeout=604800)  # Cache for 1 week
