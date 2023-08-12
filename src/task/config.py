from celery import Celery

from src.config import (
    BACKEND_HOST,
    BACKEND_PASS,
    BACKEND_PORT,
    BACKEND_USER,
    BROKER_HOST,
    BROKER_PASS,
    BROKER_PORT,
    BROKER_USER,
)

CELERY_BROKER = f'pyamqp://{BROKER_USER}:{BROKER_PASS}@{BROKER_HOST}:{BROKER_PORT}//'
CELERY_BACKEND = f'rpc://{BACKEND_USER}:{BACKEND_PASS}@{BACKEND_HOST}:{BACKEND_PORT}//'

celery_app = Celery(
    'excel_task', broker=CELERY_BROKER, backend=CELERY_BACKEND, include=['src.task.tasks']
)


celery_app.conf.update(
    result_expires=3600,
)

celery_app.conf.beat_schedule = {
    'check-excel-every-15-seconds': {
        'task': 'check_excel',
        'schedule': 15.0,
    },
}
