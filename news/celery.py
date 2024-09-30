from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news.settings')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

app = Celery('news')


app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update_top_10_day_every_hour': {
        'task': 'articles.tasks.update_top_10_day',
        'schedule': crontab(minute=0, hour='*/1'),  # Every hour
    },
    'update_top_10_week_every_day': {
        'task': 'articles.tasks.update_top_10_week',
        'schedule': crontab(minute=0, hour=0),  # Every day at midnight
    },
    'update_top_10_month_every_week': {
        'task': 'articles.tasks.update_top_10_month',
        'schedule': crontab(minute=0, hour=0, day_of_week='monday'),  # Every week on Monday
    },
}

app.conf.timezone = 'UTC'

