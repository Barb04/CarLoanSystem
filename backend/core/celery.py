import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Run every hour to check overdue loans
    'check-overdue-loans-every-hour': {
        'task': 'loans.tasks.check_overdue_loans',
        'schedule': crontab(minute=0),   # Top of every hour
    },
}