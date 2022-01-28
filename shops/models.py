from datetime import date, timedelta

from django.db import models
from django.forms import ValidationError

from .constants import CATEGORIES_CHOICES, METRIC_PERIODS, METRIC_TYPES


class Metric(models.Model):
    category = models.CharField(max_length=64, choices=CATEGORIES_CHOICES)
    name = models.CharField(max_length=64, blank=True)
    value = models.CharField(max_length=64, blank=True)
    count = models.IntegerField(default=0)
    type = models.CharField(max_length=16, choices=METRIC_TYPES)
    period = models.CharField(max_length=16, choices=METRIC_PERIODS)
    period_start = models.DateField(default=date.today)

    def clean(self) -> None:
        if self.type == 'visits' and self.value:
            raise ValidationError("Metric type visits does not accept value")
        return super().clean()

    def save(self, *args, **kwargs) -> None:
        if self.period == 'weekly':
            self.period_start = self.period_start - timedelta(days=self.period_start.weekday())
        return super().save(*args, **kwargs)
