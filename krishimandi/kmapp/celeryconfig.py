
# Celery settings

CELERY_BROKER_URL = 'redis://localhost:6379/0'
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_IMPORTS = ("kmapp.tasks",)
CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"
