from .services.commodity_service import insert_commodity_price_data
from .views import delete_old
from celery import Celery
import os
from celery.schedules import crontab
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'krishimandi.settings')
from django.conf import settings  # noqa
app = Celery('krishimandi')


app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(name='run_service')
def run_service():
   insert_commodity_price_data()

run_service.apply_async()

# @app.task(name="delete_service")
# def delete_service():
#     delete_old()
# delete_service.apply_async()