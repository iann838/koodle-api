from random import random
from datetime import date, timedelta

from django.db.models import F

from .models import Metric


class MetricManager:

    @staticmethod
    def value(a: str):
        return a.lower().replace(" ", "").replace("'", "").rstrip("s")

    @staticmethod
    def autodel():
        Metric.objects.filter(period='daily', period_start__lt=date.today() - timedelta(days=1)).delete()
        Metric.objects.filter(period='weekly', period_start__lt=date.today() - timedelta(days=7)).delete()

    @staticmethod
    def visits():
        Metric.objects.get_or_create(category="all", type="visits", period="daily", period_start=date.today())
        Metric.objects.get_or_create(category="all", type="visits", period="weekly", period_start=date.today() - timedelta(date.today().weekday()))
        Metric.objects.filter(category="all", type='visits', period="daily", period_start=date.today()).update(count=F("count") + 1)
        Metric.objects.filter(category="all", type='visits', period="weekly", period_start=date.today() - timedelta(date.today().weekday())).update(count=F("count") + 1)
        MetricManager.autodel()

    @staticmethod
    def search(name: str, category: str):
        value = MetricManager.value(name)
        if value:
            Metric.objects.get_or_create(category=category, value=value, type="search", period="daily", period_start=date.today())
            Metric.objects.get_or_create(category=category, value=value, type="search", period="weekly", period_start=date.today() - timedelta(date.today().weekday()))
            Metric.objects.filter(category=category, value=value, type='search', period="daily", period_start=date.today()).update(count=F("count") + 1, name=name)
            Metric.objects.filter(category=category, value=value, type='search', period="weekly", period_start=date.today() - timedelta(date.today().weekday())).update(count=F("count") + 1, name=name)
        MetricManager.autodel()

    @staticmethod
    def clicks(name: str, category: str):
        value = MetricManager.value(name)
        if value:
            Metric.objects.get_or_create(category=category, value=value, type="clicks", period="daily", period_start=date.today())
            Metric.objects.get_or_create(category=category, value=value, type="clicks", period="weekly", period_start=date.today() - timedelta(date.today().weekday()))
            Metric.objects.filter(category=category, value=value, type='clicks', period="daily", period_start=date.today()).update(count=F("count") + 1, name=name)
            Metric.objects.filter(category=category, value=value, type='clicks', period="weekly", period_start=date.today() - timedelta(date.today().weekday())).update(count=F("count") + 1, name=name)
        MetricManager.autodel()
