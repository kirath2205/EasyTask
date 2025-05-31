# Trigger the task
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EasyTask.settings')

# Create the TaskProcessor app instance
app = Celery('EasyTask', broker='redis://localhost:6379/0')

# Optionally, configure TaskProcessor settings
app.conf.update(
    result_backend='redis://localhost:6379/0',
)
app.autodiscover_tasks()
