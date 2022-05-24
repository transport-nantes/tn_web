from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# setting the Django settings module.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_nantes.settings')
app = Celery('transport_nantes')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Looks up for task modules in Django applications and loads them
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
