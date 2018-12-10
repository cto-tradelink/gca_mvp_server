from __future__ import absolute_import
from __future__ import absolute_import, unicode_literals
import os
from datetime import timedelta

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gca_mvp.settings')

from django.conf import settings

from celery.schedules import crontab

CELERY_TIMEZONE = 'Asia/Seoul'
app = Celery('gca_mvp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


app.conf.beat_schedule = {
    'add-every-minute-contrab': {
        'task': 'multiply_two_numbers',
        'schedule': crontab(),
        'args': (),
    },
    'add-every-5-seconds': {
        'task': 'multiply_two_numbers',
        'schedule': 5.0,
        'args': ()
    },
    'add-every-30-seconds': {
        'task': 'alarm_to_startup_due',
        'schedule': timedelta(seconds=60),
        'args': ()
    },
}

@app.task(bind=True)
def sum(a, b):
    print(str(a+b))
    return a + b


#result = sum.apply_async((2, 3), countdown=5)

#print(result.get())