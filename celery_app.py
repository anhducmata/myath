from celery import Celery
from config.settings import settings

def make_celery():
    """Create and configure Celery app"""
    celery = Celery(
        'math_homework_processor',
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=['app.tasks']
    )
    
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_reject_on_worker_lost=True,
        result_expires=3600,
    )
    
    return celery

celery_app = make_celery()

if __name__ == '__main__':
    celery_app.start()
